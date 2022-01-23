from asyncio.windows_events import NULL
import os
import html
import math
import asyncio
import discord
import mysql.connector
import datetime
from dotenv.main import load_dotenv
from discord.ext import commands
from general_bot import bot_speaks
#from permissions import check_perms

def check_perms():
    pass

class cars(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def make_embed(self, ctx, input_: dict):
        home = "http://acg.groningenrp.xyz"

        tmp = input_["merk"]
        brand = tmp.capitalize()
        
        tmp = input_["model"]
        model = tmp.capitalize()

        if input_["url"]:
            # Brand url forming
            brand_url = brand.replace(' ', '%20')
            brand_product_page = tmp.lower().replace(' ', '_')

            # Car model url forming
            model_url = model.replace(' ', '%20')
            model_product_page = tmp.lower().replace(' ', '_')

            # Declaring url
            url = f"{home}/product_page.php?brand={brand_url}&model={model_url}#{brand_product_page}-{model_product_page}"
        else:
            url = home

        # Making embed
        embed=discord.Embed(title=f'{brand} {model}', url=url, color=0xff0000)

        # Toon merk en model zolang het getoond mag worden
        if input_["show"] == 1:
            if not "gmerk" == None:
                embed.add_field(name=f"Merk: ", value=input_["gmerk"], inline=False)
            else:
                embed.add_field(name=f"Merk: ", value=input_["merk"], inline=False)

            embed.add_field(name=f"Model: ", value=input_["model"], inline=False)

        input_.pop("url")
        input_.pop("show")
        input_.pop("merk")
        input_.pop("gmerk")
        input_.pop("model")

        # Iterating over keys in input_
        for x in input_.keys():
            if not input_[x] == None:
                key = x
                value = input_[x]
                name_value = f"{key.capitalize()}:"
                
                if value == 0 and (key == "limited" or key == "uitverkocht" or key == "trailer" or key == "nieuw"):
                    value = '❌'
                elif value == 1 and (key == "limited" or key == "uitverkocht" or key == "trailer" or key == "nieuw"):
                    value = '✅'

                if key == "kofferbakruimte":
                    value = f"{value}L"
                    embed.add_field(name=name_value, value=value, inline=False)

                elif key == "acceleratie, 0-100km/h":
                    value = f"{value}s"
                    embed.add_field(name=name_value, value=value, inline=False)
                
                elif key == "topsnelheid":
                    value = f"{value}km/h"
                    embed.add_field(name=name_value, value=value, inline=False)

                elif key == "datum":
                    embed.add_field(name=name_value, value=value, inline=True)

                
                elif key == "prijs":
                    value = int(value)
                    value = f"€ {format(value * 1000, '8_.2f').replace('.', ',').replace('_', '.')}"
                    embed.add_field(name=name_value, value=value, inline=True)
                    embed.add_field(name="\u200b", value="\u200b", inline=True)

                elif key == "beschrijving":
                    if len(value) > 1024:
                        # Then we iterate to split it into multiple embeds
                        
                        # Variable declaration
                        str_ = ''
                        sentences = value.split('.')
                        embed_fields = []
                        first_message = 1
                        
                        # Iteration
                        # We add the sentences as a paragraph to the embed_fields list, if it has more than 1000 chars 
                        # if you were to add the next sentence. 
                        i = 0
                        while i < len(sentences):
                            if len(str_ + sentences[i]) < 1000:
                                last_str = '.'
                                if len(sentences[i]) == 0 or sentences[i][-1] == '.':
                                    last_str = ''

                                str_ += sentences[i] + last_str

                            if len(str_ + sentences[i]) > 1000 or i == len(sentences) - 1:
                                embed_fields.append(str_)
                                str_ = ''
                            
                            i += 1

                        # Here we iterate over the embed_fields list and make an embed.
                        # Unless it is the 6th embed field. Each paragrpah would have 1000 chars.
                        # The max limit of an embed is 6000 chars.
                        i = 0
                        while i < len(embed_fields):
                            if first_message == 1:
                                embed.add_field(name=name_value, value=embed_fields[i], inline=False)
                                first_message = 0
                            elif i < 6:
                                embed.add_field(name="\u200b", value=embed_fields[i], inline=False)

                            i += 1

                    # If the description doesn't even count 1000 chars, it doesn't matter at all.       
                    else:
                        embed.add_field(name=name_value, value=value, inline=False)
                    
                else:
                    embed.add_field(name=name_value, value=value, inline=False)

        embed.set_footer(text=self.bot.user.name)
        await ctx.send(embed=embed)

    @commands.command(aliases=['car-add'])
    async def _car_add_command(self, ctx, merk):
        def check(m):
            return m.channel == ctx.channel and m.author == ctx.author

        def check2(reaction, user):
            return user == ctx.author

        def return_smt(v):
            if str(v[0]) == '✅':
                return 1
            elif str(v[0]) == '❌':
                return 0

        if check_perms('administrative', ctx):
            load_dotenv()
            mydb = mysql.connector.connect(
                host=os.getenv('DB_SERVERNAME'),
                user=os.getenv('DB_USERNAME'),
                password=os.getenv('DB_PASSWORD'),
                database=os.getenv('DB_NAME')
            )

            mycursor = mydb.cursor()
            if isinstance(merk, str):
                mycursor.execute(f"SELECT `id`,`name`,`special` FROM `tbl_brands` WHERE `name` = '{html.escape(merk)}';")
            if isinstance(merk, int):
                mycursor.execute(f"SELECT `id`,`name`,`special` FROM `tbl_brands` WHERE `id` = '{html.escape(merk)}';")
            myresult = mycursor.fetchall()
            merk_id = myresult[0][0]
            brand_value = myresult[0][1]
            gbrand_value = myresult[0][2]
            votes = ['✅','❌']

            if gbrand_value != None:
                merk_name = myresult[0][2]
            else:
                merk_name = myresult[0][1]

            ToDelete = []
            
            ToDelete.append(ctx.message)

            # Model naam
            tmp = await ctx.send(f'{ctx.author.mention}, u wilt een nieuwe {merk_name} toevoegen. \nHoe heet dit model?')    
            ToDelete.append(tmp)
            tmp = await self.bot.wait_for('message', timeout=30.0, check=check)
            await tmp.add_reaction('👍')
            ToDelete.append(tmp)
            model_name = f'{tmp.content}'
        
            # Beschrijving
            tmp = await ctx.send(f'Wat is de beschrijving van dit merk? Als u \"geen\" antwoordt dan kies ik er een voor u.')
            ToDelete.append(tmp)
            tmp = await self.bot.wait_for('message', timeout=30.0, check=check)
            await tmp.add_reaction('👍')
            ToDelete.append(tmp)
            if tmp.content == 'geen':
                description_tmp = "Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum."
            else:
                description_tmp = tmp.content

            # Kofferbak
            tmp = await ctx.send(f'Hoeveel liter kofferbakruimte heeft de {model_name}? Indien u \"onbekend\" antwoordt vul ik zelf 0 in.')
            ToDelete.append(tmp)
            tmp = await self.bot.wait_for('message', timeout=30.0, check=check)
            await tmp.add_reaction('👍')
            ToDelete.append(tmp)
            if tmp.content == 'onbekend':
                trunk_tmp = 0
            else:
                trunk_tmp = tmp.content

            # Acceleration
            tmp = await ctx.send(f'Hoe snel gaat de {model_name} van 0 naar 100km/h? Indien u \"onbekend\" antwoordt vul ik zelf 0 in.')
            ToDelete.append(tmp)
            tmp = await self.bot.wait_for('message', timeout=30.0, check=check)
            await tmp.add_reaction('👍')
            ToDelete.append(tmp)
            if tmp.content == 'onbekend':
                acceleration_tmp = 0.0
            else:
                acceleration_tmp = tmp.content

            # Top speed
            tmp = await ctx.send(f'Wat is de topsnelheid van de {model_name}? Indien u \"onbekend\" antwoordt vul ik zelf 0 in.')
            ToDelete.append(tmp)
            tmp = await self.bot.wait_for('message', timeout=30.0, check=check)
            await tmp.add_reaction('👍')
            ToDelete.append(tmp)
            if tmp.content == 'onbekend':
                topspeed_tmp = 0
            else:
                topspeed_tmp = tmp.content

            # Limited
            tmp = await ctx.send(f'Is de {model_name} limited?')
            ToDelete.append(tmp)
            for x in votes:
                await tmp.add_reaction(x)
            reaction_limited = await self.bot.wait_for('reaction_add', timeout=60.0, check=check2)

            # Trailer
            tmp = await ctx.send(f'Heeft de {model_name} een trekhaak?')
            ToDelete.append(tmp)
            for x in votes:
                await tmp.add_reaction(x)
            reaction_trailer = await self.bot.wait_for('reaction_add', timeout=60.0, check=check2)

            # Uitverkocht
            tmp = await ctx.send(f'Is de {model_name} uitverkocht?')
            ToDelete.append(tmp)
            for x in votes:
                await tmp.add_reaction(x)
            reaction_sold = await self.bot.wait_for('reaction_add', timeout=60.0, check=check2)

            # Nieuw
            tmp = await ctx.send(f'Is de {model_name} nieuw?')
            ToDelete.append(tmp)
            for x in votes:
                await tmp.add_reaction(x)
            reaction_new = await self.bot.wait_for('reaction_add', timeout=60.0, check=check2)

            dict_ = {
                "url" : 0,
                "show" : 0,
                "merk" : brand_value,
                "gmerk" : gbrand_value,
                "model" : model_name,
                "beschrijving" : description_tmp,
                "limited" : return_smt(str(reaction_limited)),
                "uitverkocht" : return_smt(str(reaction_sold)),
                "trailer" : return_smt(str(reaction_trailer)),
                "nieuw" : return_smt(str(reaction_new)),
                "kofferbakruimte" : trunk_tmp,
                "acceleratie, 0-100km/h" : acceleration_tmp,
                "topsnelheid" : topspeed_tmp,
            }

            await self.make_embed(ctx, dict_)
            tmp = await ctx.send(f'Bent u akkoord met dit toe te voegen aan de databank?')
            ToDelete.append(tmp)
            for x in votes:
                await tmp.add_reaction(x)
            reaction = await self.bot.wait_for('reaction_add', timeout=120.0, check=check2)
            if str(reaction[0]) == '✅':
                tmp = await ctx.send(f'Ik ga nu {model_name} toevoegen aan de website.')
                ToDelete.append(tmp)
                brand_id = merk_id
                model = html.escape(model_name)
                description = html.escape(description_tmp)
                limited = return_smt(reaction_limited)
                trailer = return_smt(reaction_trailer)
                sold_out = return_smt(reaction_sold)
                new = return_smt(reaction_new)
                trunk = trunk_tmp
                acceleration = acceleration_tmp
                topspeed = topspeed_tmp
                sql = "INSERT INTO `tbl_cars`(`id`, `brand_id`, `model`, `description`, `limited`, `trailer`, `sold_out`, `new`, `trunk`, `acceleration`, `topspeed`) VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
                val = (brand_id, model, description, limited, trailer, sold_out, new, trunk, acceleration, topspeed)
                mycursor.execute(sql, val)
                mydb.commit()
                bot_speaks(self.bot, f'{ctx.author} heeft {model_name} van {merk_name} toegevoegd.')
            else:
                tmp = await ctx.send(f'U heeft nu even pech, probeer zo opnieuw.')
                ToDelete.append(tmp)

            await asyncio.sleep(5)
            await ctx.channel.delete_messages(ToDelete)
        else:
            await ctx.send(f'{ctx.author.mention}, u bezit helaas niet over de permissies om een nieuwe auto toe te voegen.\nGelieve contact op te nemen met de ACG manager of directeur indien u van mening bent dat dit een fout is.', delete_after=10)

    @commands.command(aliases=['car-edit'])
    async def _car_edit_command(self, ctx, merk: str, model: str, tmp_var: str):
        values = ['✅','❌']
        def check(m):
            return m.channel == ctx.channel and m.author == ctx.author

        def check2(reaction, user):
            return user == ctx.author

        def return_smt(v):
            if v == 1:
                return '✅'
            elif v == 0:
                return '❌'
            elif str(v[0]) == '✅':
                return 1
            elif str(v[0]) == '❌':
                return 0

        def make_price(v):
            print(v)
            num = format(v * 1000, '8_.2f').replace('.', ',').replace('_', '.')
            return f"€ {num}"

        if check_perms('administrative', ctx):
            ToDelete = []
            load_dotenv()
            mydb = mysql.connector.connect(
                host=os.getenv('DB_SERVERNAME'),
                user=os.getenv('DB_USERNAME'),
                password=os.getenv('DB_PASSWORD'),
                database=os.getenv('DB_NAME')
            )
            ToDelete.append(ctx)
            mycursor = mydb.cursor()
            mycursor.execute(f"SELECT * FROM `tbl_brands` WHERE `name` = '{html.escape(merk)}';")
            brands_result = mycursor.fetchall()

            if brands_result[0][0] != None:
                brand_name = brands_result[0][1]
                brand_gname = brands_result[0][2]
                mycursor.execute(f"SELECT * FROM `tbl_cars` WHERE `model` = '{html.escape(model)}' AND `brand_id` = {brands_result[0][0]};")
                cars_result = mycursor.fetchall()

                if cars_result[0][0] != None:
                    model_name = cars_result[0][2]

                    if tmp_var == 'merk':
                        tmp = await ctx.send('Dit is hoe het er nu uit ziet:')
                        ToDelete.append(tmp)
                        sql = f"SELECT `tbl_cars`.`brand_id`, `tbl_brands`.`name`, `tbl_brands`.`special`, `tbl_cars`.`model` FROM `tbl_cars` INNER JOIN `tbl_brands` ON `tbl_brands`.`id` = `tbl_cars`.`brand_id` WHERE `tbl_brands`.`name` = '{html.escape(brand_name)}' AND `tbl_cars`.`model` = '{html.escape(model_name)}';"
                        mycursor.execute(sql)
                        brand_command_result = mycursor.fetchall()

                        dict_ = {
                            "url" : 1,
                            "show" : 1,
                            "merk" : brand_name,
                            "gmerk" : brand_gname,
                            "model" : model_name
                        }

                        await self.make_embed(ctx, dict_)

                        reaction = []
                        reaction.append('👎')
                        while str(reaction[0]) == '👎':
                            tmp = await ctx.send('Naar wat wil je dit aanpassen?')
                            ToDelete.append(tmp)
                            tmp = await self.bot.wait_for('message', timeout=30.0, check=check)
                            new_value = tmp.content
                            await tmp.add_reaction('👍')
                            await asyncio.sleep(2)
                            ToDelete.append(tmp)
                            tmp = await ctx.send('Zo wordt het:')
                            ToDelete.append(tmp)

                            dict_ = {
                            "url" : 1,
                            "show" : 1,
                            "merk" : brand_name,
                            "gmerk" : brand_gname,
                            "model" : model_name
                            }

                            await self.make_embed(ctx, dict_)

                            tmp = await ctx.send('Klopt dit?')
                            ToDelete.append(tmp)
                            await tmp.add_reaction('👍')
                            await tmp.add_reaction('👎')
                            reaction = await self.bot.wait_for('reaction_add', timeout=60.0, check=check2)
                            if str(reaction[0]) == '👍':
                                break
                        
                        tmp = await ctx.send('Ik pas het voor je aan.')
                        ToDelete.append(tmp)
                        sql = f"SELECT `tbl_brands`.`id`, `tbl_brands`.`name` FROM `tbl_brands` WHERE `tbl_brands`.`name` = '{html.escape(new_value)}';"
                        mycursor.execute(sql)
                        brand_command_result = mycursor.fetchall()                        
                        sql = f"UPDATE `tbl_cars` INNER JOIN `tbl_brands` ON `tbl_brands`.`id` = `tbl_cars`.`brand_id` SET `tbl_cars`.`brand_id` = '{brand_command_result[0][0]}' WHERE `tbl_brands`.`name` = '{html.escape(brand_name)}' AND `tbl_cars`.`model` = '{html.escape(model_name)}';"
                        mycursor.execute(sql)
                        mydb.commit()
                        tmp = await ctx.send(f'Het {tmp_var} van de {brand_command_result[0][1].capitalize()} {model_name.capitalize()} werd aangepast **van** *{brand_name.capitalize()}* **naar** *{brand_command_result[0][1].capitalize()}*.')
                        ToDelete.append(tmp)
                        await asyncio.sleep(30)
                        await ctx.channel.delete_messages(ToDelete)
                        bot_speaks(self.bot, f'{ctx.author} heeft het {tmp_var} van de {brand_command_result[0][1].capitalize()} {model_name.capitalize()} werd aangepast **van** *{brand_name.capitalize()}* **naar** *{brand_command_result[0][1].capitalize()}*.')

                    elif tmp_var == 'prijs':
                        tmp = await ctx.send('Dit is hoe het er nu uit ziet:')
                        ToDelete.append(tmp)
                        
                        qry = f'''SELECT 
                        `tbl_prices`.`price` as 'price',
                        `tbl_dates`.`date` as 'date',
                        `tbl_cars`.`id` as 'id'
                        FROM `tbl_cars`
                            INNER JOIN
                            `tbl_brands`
                            ON `tbl_brands`.`id` = `tbl_cars`.`brand_id`
                            INNER JOIN
                            `tbl_prices`
                            ON `tbl_prices`.`model_id` = `tbl_cars`.`id`
                            INNER JOIN
                            `tbl_dates`
                            ON `tbl_dates`.`id` = `tbl_prices`.`date_id`
                        WHERE `tbl_brands`.`name` = '{html.escape(brand_name)}' AND `model` = '{html.escape(model_name)}'
                        GROUP BY `tbl_prices`.`price`
                        ORDER BY `tbl_dates`.`date` DESC
                        LIMIT 1;'''
                        mycursor.execute(qry)
                        price_select_command_result = mycursor.fetchall()
                        ToDelete.append(tmp)

                        dict_ = {
                            "url" : 1,
                            "show" : 0,
                            "merk" : brand_name,
                            "gmerk" : brand_gname,
                            "model" : model_name,
                            "datum" : price_select_command_result[0][1],
                            "prijs" : price_select_command_result[0][0]
                        }

                        await self.make_embed(ctx, dict_)

                        tmp_now = datetime.now()
                        TodayDate = tmp_now.strftime('%Y-%m-%d')
                        reaction = []
                        reaction.append('👎')
                        while str(reaction[0]) == '👎':
                            tmp = await ctx.send('Naar wat wil je dit aanpassen? Stel dat het voertuig **€ 20.000,00** word, dan reageer je **20**.')
                            ToDelete.append(tmp)
                            tmp = await self.bot.wait_for('message', timeout=30.0, check=check)
                            ToDelete.append(tmp)
                            new_value = tmp.content
                            await tmp.add_reaction('👍')
                            await asyncio.sleep(2)
                            tmp = await ctx.send('Zo wordt het:')
                            ToDelete.append(tmp)

                            dict_ = {
                            "url" : 1,
                            "show" : 0,
                            "merk" : brand_name,
                            "gmerk" : brand_gname,
                            "model" : model_name,
                            "datum" : TodayDate,
                            "prijs" : int(new_value)
                            }

                            await self.make_embed(ctx, dict_)

                            tmp = await ctx.send('Is dit juist?')
                            ToDelete.append(tmp)
                            await tmp.add_reaction('👍')
                            await tmp.add_reaction('👎')
                            reaction = await self.bot.wait_for('reaction_add', timeout=60.0, check=check2)
                            if str(reaction[0]) == '👍':
                                break
                        
                        tmp = await ctx.send('Ik pas het voor je aan.')
                        ToDelete.append(tmp)
                        sql = "SELECT * FROM `tbl_dates` WHERE `tbl_dates`.`date` = %s;"
                        mycursor.execute(sql, (TodayDate,))
                        tmp_fetch = mycursor.fetchall()
                        if not tmp_fetch:
                            # Er is geen datum. Die voegen we toe
                            sql = "INSERT INTO `tbl_dates` (`date`) VALUES (%s);"
                            mycursor.execute(sql, (TodayDate,))
                            mydb.commit()
                        # Datum vandaag bestaat. Nu gaan we de prijs toevoegen.
                        sql = "SELECT * FROM `tbl_dates` WHERE `tbl_dates`.`date` = %s;"
                        mycursor.execute(sql, (TodayDate,))
                        tmp_fetch = mycursor.fetchall()
                        date_id_today = tmp_fetch[0][0]
                        # Checken of er vandaag al een prijs is.
                        car_id = cars_result[0][0]
                        sql = "SELECT * FROM `tbl_prices` INNER JOIN `tbl_dates` ON `tbl_dates`.`id` = `tbl_prices`.`date_id` WHERE `tbl_dates`.`date` = %s AND `tbl_prices`.`model_id` = %s;"
                        mycursor.execute(sql, (TodayDate, car_id))
                        pricing_command_result = mycursor.fetchall()
                        if pricing_command_result:
                            # Als er een prijs is ingesteld voor het model op vandaag:
                            # Doe dit
                            sql = "UPDATE `tbl_prices` SET `price` = %s WHERE `date_id` = %s AND `model_id` = %s;"
                            mycursor.execute(sql, (html.escape(new_value), date_id_today, car_id))
                            mydb.commit()
                        else:
                            # Er is geen prijs ingesteld op vandaag
                            sql = "INSERT INTO `tbl_prices` (`id`, `date_id`, `model_id`, `price`) VALUES (NULL, %s, %s, %s);"
                            mycursor.execute(sql, (date_id_today, car_id, html.escape(new_value)))
                            mydb.commit()

                        tmp = await ctx.send(f'De prijs van de {brand_name.capitalize()} {model_name.capitalize()} werd aangepast **van** *{make_price(int(price_select_command_result[0][0]))}* **naar** *{make_price(int(new_value))}*.')
                        ToDelete.append(tmp)
                        await asyncio.sleep(30)
                        await ctx.channel.delete_messages(ToDelete)
                        bot_speaks(self.bot, f'{ctx.author} heeft de prijs van de {brand_name.capitalize()} {model_name.capitalize()} werd aangepast **van** *€ {make_price(int(price_select_command_result[0][0]))}* **naar** *€ {make_price(int(new_value))}*.')    
                        
                    elif tmp_var == 'limited' or tmp_var == 'trekhaak' or tmp_var == 'uitverkocht' or tmp_var == 'nieuw':
                        if tmp_var == 'limited':
                            var = 'limited'
                        elif tmp_var == 'trekhaak':
                            var = 'trailer'
                        elif tmp_var == 'uitverkocht':
                            var = 'sold_out'
                        elif tmp_var == 'nieuw':
                            var = 'new'
                        
                        sql = f"SELECT `tbl_cars`.`{var}` FROM `tbl_cars` INNER JOIN `tbl_brands` ON `tbl_brands`.`id` = `tbl_cars`.`brand_id` WHERE `tbl_brands`.`name` = '{html.escape(brand_name)}' AND `tbl_cars`.`model` = '{html.escape(model_name)}';"
                        mycursor.execute(sql)
                        car_command_result = mycursor.fetchall()
                        # Toon de huidige gegevens                                                     /product_page.php?brand=Alpine&model=A110#alpine-a110
                        tmp = await ctx.send('Dit is hoe het er nu uit ziet:')
                        ToDelete.append(tmp)

                        dict_ = {
                            "url" : 1,
                            "show" : 0,
                            "merk" : brand_name,
                            "gmerk" : brand_gname,
                            "model" : model_name 
                        }
                        
                        dict_[tmp_var] = car_command_result[0][0]

                        await self.make_embed(ctx, dict_)

                        reaction = []
                        reaction.append('👎')
                        while str(reaction[0]) == '👎':
                            tmp = await ctx.send('Naar wat wil je dit aanpassen?')
                            ToDelete.append(tmp)
                            for x in values:
                                await tmp.add_reaction(x)
                            reaction_message = await self.bot.wait_for('reaction_add', timeout=60.0, check=check2)
                            tmp = await ctx.send('Ik heb je reactie gezien.')
                            await tmp.add_reaction('👍')
                            ToDelete.append(tmp)                                
                            await asyncio.sleep(2)
                            tmp = await ctx.send('Zo wordt het:')
                            ToDelete.append(tmp)

                            dict_ = {
                            "url" : 1,
                            "show" : 0,
                            "merk" : brand_name,
                            "gmerk" : brand_gname,
                            "model" : model_name 
                            }
                            
                            dict_[tmp_var] = str(reaction_message[0])

                            await self.make_embed(ctx, dict_)

                            tmp = await ctx.send('Is dit juist?')
                            ToDelete.append(tmp)
                            await tmp.add_reaction('👍')
                            await tmp.add_reaction('👎')
                            reaction = await self.bot.wait_for('reaction_add', timeout=60.0, check=check2)
                            if str(reaction[0]) == '👍':
                                break
                        
                        tmp = await ctx.send('Ik pas het voor je aan.')
                        ToDelete.append(tmp)
                        sql = "UPDATE `tbl_cars` INNER JOIN `tbl_brands` ON `tbl_brands`.`id` = `tbl_cars`.`brand_id` SET "+html.escape(var)+" = %s WHERE `tbl_brands`.`name` = %s AND `tbl_cars`.`model` = %s;"
                        mycursor.execute(sql, (int(return_smt(reaction_message)), brand_name, model_name))
                        mydb.commit()
                        tmp = await ctx.send(f'De {tmp_var} van de {brand_name.capitalize()} {model_name.capitalize()} werd aangepast **van** *{return_smt(car_command_result[0][0])}* **naar** *{str(reaction_message[0])}*.')
                        ToDelete.append(tmp)
                        await asyncio.sleep(30)
                        await ctx.channel.delete_messages(ToDelete)
                        bot_speaks(self.bot, f'{ctx.author} heeft de {tmp_var} van de {brand_name.capitalize()} {model_name.capitalize()} werd aangepast **van** *{car_command_result[0][0]}* **naar** *{reaction_message}*.')

                    else:  
                        behind = ''
                        if tmp_var == 'model':
                            var = 'model'
                        elif tmp_var == 'beschrijving':
                            var = 'description'
                        elif tmp_var == 'kofferbak':
                            var = 'trunk'
                            behind = 'L'
                        elif tmp_var == 'acceleratie':
                            var = 'acceleration'    
                            behind = 's'
                        elif tmp_var == 'topsnelheid':
                            var = 'topspeed'
                            behind = 'km/h'

                        sql = f"SELECT `tbl_cars`.`{var}` FROM `tbl_cars` INNER JOIN `tbl_brands` ON `tbl_brands`.`id` = `tbl_cars`.`brand_id` WHERE `tbl_brands`.`name` = '{html.escape(brand_name)}' AND `tbl_cars`.`model` = '{html.escape(model_name)}';"
                        mycursor.execute(sql)
                        car_command_result = mycursor.fetchall()
                        # Toon de huidige gegevens                                                     /product_page.php?brand=Alpine&model=A110#alpine-a110
                        tmp = await ctx.send('Dit is hoe het er nu uit ziet:')
                        ToDelete.append(tmp)

                        dict_ = {
                            "url" : 1,
                            "show" : 0,
                            "merk" : brand_name,
                            "gmerk" : brand_gname,
                            "model" : model_name 
                        }
                        
                        dict_[tmp_var] = car_command_result[0][0]

                        await self.make_embed(ctx, dict_)

                        reaction = []
                        reaction.append('👎')
                        while str(reaction[0]) == '👎':
                            tmp = await ctx.send('Naar wat wil je dit aanpassen?')
                            ToDelete.append(tmp)
                            tmp = await self.bot.wait_for('message', timeout=30.0, check=check)
                            new_value = tmp.content
                            await tmp.add_reaction('👍')
                            await asyncio.sleep(5)
                            ToDelete.append(tmp)
                            tmp = await ctx.send('Zo wordt het:')
                            ToDelete.append(tmp)

                            dict_ = {
                            "url" : 1,
                            "show" : 0,
                            "merk" : brand_name,
                            "gmerk" : brand_gname,
                            "model" : model_name 
                            }
                            
                            dict_[tmp_var] = new_value

                            await self.make_embed(ctx, dict_)

                            tmp = await ctx.send('Is dit juist?')
                            ToDelete.append(tmp)
                            await tmp.add_reaction('👍')
                            await tmp.add_reaction('👎')
                            reaction = await self.bot.wait_for('reaction_add', timeout=60.0, check=check2)
                            if str(reaction[0]) == '👍':
                                break
                        
                        tmp = await ctx.send('Ik pas het voor je aan.')
                        ToDelete.append(tmp)
                        sql = f"UPDATE `tbl_cars` INNER JOIN `tbl_brands` ON `tbl_brands`.`id` = `tbl_cars`.`brand_id` SET `tbl_cars`.`{html.escape(var)}` = '{html.escape(new_value)}' WHERE `tbl_brands`.`name` = '{html.escape(brand_name)}' AND `tbl_cars`.`model` = '{html.escape(model_name)}';"
                        mycursor.execute(sql)
                        mydb.commit()
                        tmp = await ctx.send(f'De {tmp_var} van de {brand_name.capitalize()} {model_name.capitalize()} werd aangepast **van** *{car_command_result[0][0]}* **naar** *{new_value}*.')
                        ToDelete.append(tmp)
                        await asyncio.sleep(30)
                        await ctx.channel.delete_messages(ToDelete)
                        bot_speaks(self.bot, f'{ctx.author} heeft de {tmp_var} van de {brand_name.capitalize()} {model_name.capitalize()} werd aangepast **van** *{car_command_result[0][0]}* **naar** *{new_value}*.')    

                else:
                    await ctx.send(f'{ctx.author.mention}, er is geen model gevonden met de naam {model}.')

            else:
                await ctx.send(f'{ctx.author.mention}, er is geen merk gevonden met de naam {merk}.')

        else:
            await ctx.send(f'{ctx.author.mention}, u bezit helaas niet over de permissies om dit merk aan te passen.\nGelieve contact op te nemen met de ACG manager of directeur indien u van mening bent dat dit een fout is.', delete_after=5)

    @commands.command(aliases=['car-see'])
    async def _car_see_command(self, ctx, brand: str, car: str):
        def return_smt(v):
            if v == 1:
                return '✅'
            elif v == 0:
                return '❌'
            
        def make_price(v):
            price = format(v * 1000, '8_.2f').replace('.', ',').replace('_', '.')
            return f"€ {price}"

        if check_perms('basic', ctx):
            # Connectie maken
            load_dotenv()
            mydb = mysql.connector.connect(
                host=os.getenv('DB_SERVERNAME'),
                user=os.getenv('DB_USERNAME'),
                password=os.getenv('DB_PASSWORD'),
                database=os.getenv('DB_NAME')
            )
            mycursor = mydb.cursor()

            # De query
            qry = f'''SELECT 
            `tbl_cars`.`id` as 'id',
            `tbl_brands`.`name` as 'brand',
            `tbl_brands`.`special` as 'special',
            `tbl_cars`.`model` as 'model',
            `tbl_cars`.`description` as 'description_model',
            `tbl_cars`.`limited` as 'limited',
            `tbl_cars`.`sold_out` as 'sold',
            `tbl_cars`.`trailer` as 'trailer',
            `tbl_cars`.`new` as 'new',
            `tbl_cars`.`trunk` as 'trunk',
            `tbl_cars`.`acceleration` as 'acceleration',
            `tbl_cars`.`topspeed` as 'topspeed'
            FROM `tbl_cars`
                INNER JOIN
                `tbl_brands`
                ON `tbl_brands`.`id` = `tbl_cars`.`brand_id`
            WHERE `tbl_brands`.`name` = '{html.escape(brand)}' AND `model` = '{html.escape(car)}';'''

            # Query executen
            mycursor.execute(qry)

            # Query ophalen
            myresult = mycursor.fetchall()
            
            # Variable declaratie
            model_id_value = myresult[0][0]
            brand_value = myresult[0][1]
            gbrand_value = myresult[0][2]
            model_value = myresult[0][3]
            description_value = myresult[0][4]
            limited_value = myresult[0][5]
            sold_value = myresult[0][6]
            trailer_value = myresult[0][7]
            new_value = myresult[0][8]
            trunk_value = myresult[0][9]
            acceleration_value = myresult[0][10]
            topspeed_value = myresult[0][11]

            # Laatste prijs ophalen
            qry = "SELECT `tbl_dates`.`date` as 'date', `tbl_prices`.`price` FROM `tbl_prices` INNER JOIN `tbl_dates` ON `tbl_dates`.`id` = `tbl_prices`.`date_id` WHERE `tbl_prices`.`model_id` = %s ORDER BY `tbl_dates`.`date` DESC LIMIT 1;"
            mycursor.execute(qry, (model_id_value,))
            myresult = mycursor.fetchall()
            date_value = myresult[0][0]
            price_value = int(myresult[0][1])

            dict_ = {
                "url" : 1,
                "show" : 0,
                "merk" : brand_value,
                "gmerk" : gbrand_value,
                "model" : model_value,
                "beschrijving" : description_value,
                "limited" : limited_value,
                "uitverkocht" : sold_value,
                "trailer" : trailer_value,
                "nieuw" : new_value,
                "kofferbakruimte" : trunk_value,
                "acceleratie, 0-100km/h" : acceleration_value,
                "topsnelheid" : topspeed_value,
                "datum" : date_value,
                "prijs" : price_value
            }

            await self.make_embed(ctx, dict_)
        else:
            await ctx.send(f'{ctx.author.mention}, je hebt niet genoeg permissies.\nGelieve contact op te nemen met de ACG manager of directeur indien u van mening bent dat dit een fout is.', delete_after=5)
        
    @commands.command(aliases=['cars-see'])
    async def _cars_see_command(self, ctx, brand: str):
        if check_perms('basic', ctx):
            load_dotenv()
            mydb = mysql.connector.connect(
                host=os.getenv('DB_SERVERNAME'),
                user=os.getenv('DB_USERNAME'),
                password=os.getenv('DB_PASSWORD'),
                database=os.getenv('DB_NAME')
            )
            mycursor = mydb.cursor()
            mycursor.execute(f"SELECT `tbl_cars`.`model`, `tbl_brands`.`special` FROM `tbl_cars` INNER JOIN `tbl_brands` ON `tbl_brands`.`id` = `tbl_cars`.`brand_id` WHERE `tbl_brands`.`name` = '{html.escape(brand)}';")
            myresult = mycursor.fetchall()

            await ctx.send(f"Van {brand.capitalize()} hebben we de volgende voertuigen: ")
            for x in myresult:
                dict_ = {
                    "url" : 1,
                    "show" : 0,
                    "merk" : brand,
                    "gmerk" : x[1],
                    "model" : x[0]
                }

                await self.make_embed(ctx, dict_)

        else:
            await ctx.send(f'{ctx.author.mention}, u bezit helaas niet over de permissies om dit merk aan te passen.\nGelieve contact op te nemen met de ACG manager of directeur indien u van mening bent dat dit een fout is.', delete_after=5)

    @commands.command(aliases=['cars-add-month'])
    async def _cars_new_month_command(self, ctx):
        if check_perms('dev', ctx):
            # Connectie maken
            load_dotenv()
            mydb = mysql.connector.connect(
                host=os.getenv('DB_SERVERNAME'),
                user=os.getenv('DB_USERNAME'),
                password=os.getenv('DB_PASSWORD'),
                database=os.getenv('DB_NAME')
            )
            mycursor = mydb.cursor()

            # De query
            qry = "SELECT COUNT(id) FROM `tbl_cars`;"

            # Query executen
            mycursor.execute(qry)

            # Query ophalen
            myresult = mycursor.fetchall()
            
            # Variable declaratie
            amount_of_cars = myresult[0][0]

            # De query
            qry = f'''SELECT
            `tbl_cars`.`id`,
            SUBSTRING_INDEX(GROUP_CONCAT(`tbl_prices`.`price`), ',', -1) as 'prijs'
            FROM `tbl_cars`
                INNER JOIN
                `tbl_prices`
                ON
                `tbl_prices`.`model_id` = `tbl_cars`.`id`
                LEFT JOIN
                `tbl_dates`
                ON
                `tbl_dates`.`id` = `tbl_prices`.`date_id`
            GROUP BY `tbl_cars`.`id`;'''

            # Query executen
            mycursor.execute(qry)

            # Query ophalen
            myresult = mycursor.fetchall()

            cars_dict = {}
            for x in myresult:
                cars_dict[x[0]] = x[1]

            # Datum, eerste dag vd maand genereren.
            date_tmp = f"2021-{datetime.now().month}-01"
            qry = "INSERT INTO `tbl_dates` (`id`, `date`) VALUES (NULL, %s);"
            mycursor.execute(qry, ( date_tmp,))

            #Id van date grabben
            qry = "SELECT `id`, MAX(`date`) FROM `tbl_dates`;"

            # Query executen
            mycursor.execute(qry)

            # Query ophalen
            myresult = mycursor.fetchall()
            
            # Variable declaratie
            date_id = myresult[0][0]
            
            for key, value in cars_dict.items():
                sql = "INSERT INTO `tbl_prices`(`id`, `date_id`, `model_id`, `price`) VALUES (NULL, %s, %s, %s);"
                mycursor.execute(sql, (date_id, key, value))
            
            mydb.commit()

        else:
            await ctx.send(f'{ctx.author.mention}, u bezit helaas niet over de permissies om dit merk aan te passen.\nGelieve contact op te nemen met de ACG manager of directeur indien u van mening bent dat dit een fout is.', delete_after=5)
        
    @commands.command(aliases=['cars-fix'])
    async def _cars_new_month_command_fix(self, ctx):
        if check_perms('dev', ctx):
            # Connectie maken
            load_dotenv()
            mydb = mysql.connector.connect(
                host=os.getenv('DB_SERVERNAME'),
                user=os.getenv('DB_USERNAME'),
                password=os.getenv('DB_PASSWORD'),
                database=os.getenv('DB_NAME')
            )
            mycursor = mydb.cursor()

            await ctx.send("Ik bereken nu het aantal auto's.")
            # De query
            qry = "SELECT COUNT(id) FROM `tbl_cars`;"

            # Query executen
            mycursor.execute(qry)

            # Query ophalen
            myresult = mycursor.fetchall()
            
            # Variable declaratie
            amount_of_cars = myresult[0][0] + 1
            start_date = datetime.date(2021, 11, 9)
            end_date = datetime.date(2021, 11, 22)
            delta = datetime.timedelta(days=1)

            while start_date <= end_date:
                # De query
                qry = "SELECT `id` FROM `tbl_dates` WHERE `date` LIKE %s;"

                # Query executen
                mycursor.execute(qry, (start_date, ))

                myresult = mycursor.fetchall()
                # Query ophalen
                if (len(myresult) == 0):
                    qry = "INSERT INTO `tbl_dates`(`id`, `date`) VALUES (null, %s);"

                    # Query executen
                    mycursor.execute(qry, (start_date ,))

                    mydb.commit()

                yesterday = start_date - delta
                await ctx.send(f"Ik bekijk de laatste prijs van elke auto van {yesterday}.")
                for x in range(1, amount_of_cars):
                    # De query
                    qry = '''SELECT `tbl_dates`.`id`,`price`,`type` FROM `tbl_prices`
                        INNER JOIN
                        `tbl_dates`
                        ON `tbl_prices`.`date_id` = `tbl_dates`.`id`
                    WHERE `tbl_prices`.`model_id` LIKE %s AND `tbl_dates`.`date` LIKE %s;'''
                    
                    # Query executen
                    mycursor.execute(qry, (x, yesterday))

                    # Query ophalen
                    myresult = mycursor.fetchall()

                    # Variabele declaratie
                    tmp_date_id = myresult[0][0]
                    tmp_price = myresult[0][1]
                    tmp_type = myresult[0][2]
                    qry = "SELECT * FROM `tbl_prices` WHERE `date_id` LIKE %s AND `model_id` LIKE %s AND `price` LIKE %s;"

                    # Query executen
                    mycursor.execute(qry, (tmp_date_id + 1, x, tmp_price))

                    myresult = mycursor.fetchall()
                    # Query ophalen
                    if (len(myresult) == 0):
                        # De query
                        qry = "INSERT INTO `tbl_prices`(`id`, `date_id`, `model_id`, `price`, `type`) VALUES (null, %s, %s, %s, %s);"

                        # Query executen
                        mycursor.execute(qry, (tmp_date_id + 1, x, tmp_price, tmp_type))

                await ctx.send(f"Ik ga nu de prijzen van {start_date} toevoegen.")
                mydb.commit()      

                # Incrementie
                start_date += delta
            
            await ctx.send("Ik ben helemaal klaar.")

        else:
            await ctx.send(f'{ctx.author.mention}, u bezit helaas niet over de permissies om dit merk aan te passen.\nGelieve contact op te nemen met de ACG manager of directeur indien u van mening bent dat dit een fout is.', delete_after=5)

def setup(bot):
    bot.add_cog(cars(bot))