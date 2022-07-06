from asyncio import sleep, wait
import datetime
import os
import time
import typing
import discord
from cogs.functions import returnMember
import general
import mysql.connector
from logs import return_embed
from logs import make_embed
from logs import make_log
from logs import make_discord_log
from dotenv.main import load_dotenv
from discord.ext import commands
from general_bot import bot_speaks
from classes.employee import Employee

typebuttons = {
    "probleem": "❗",
    "vraag": "❓",
    "aanvraag": "📋",
    "claim": "😱"
}

class ChannelButton(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.value = None
        self.bot = bot

    async def button_action(self, interaction: discord.Interaction, button: discord.ui.Button):
        load_dotenv()
        mydb = mysql.connector.connect(
            host=os.getenv('DB_SERVERNAME'),
            user=os.getenv('DB_USERNAME'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME')
        )
        
        tickettype = button.custom_id
        user = interaction.user
        mycursor = mydb.cursor(buffered=True)
        sql = "SELECT count(*) FROM `tbl_tickets` WHERE `agent_discordid` IS NULL AND `client_discordid` LIKE %s;"
        mycursor.execute(sql, (user.id,))
        myresult = mycursor.fetchone()
        aantal_tickets = 0

        if not myresult == None and not myresult == 0:
            aantal_tickets = myresult[0]        

        if aantal_tickets < 5:
            sql = "SELECT MAX(`id`) FROM `tbl_tickets`;"
            mycursor.execute(sql)
            myresult = mycursor.fetchone()
            
            if myresult[0] != None:
                number = myresult[0] + 1
            else:
                number = 1

            icon = typebuttons[tickettype]
            name = f"{icon}-ticket-{number}"
            overwrite = {
                user: discord.PermissionOverwrite()
            }

            category = discord.utils.get(interaction.guild.categories, id=918437790025392138)
            channel = await interaction.guild.create_text_channel(name, category=category)
            await channel.set_permissions(interaction.user, read_message_history=True, view_channel=True, send_messages=True)
            try:
                dict_ = {
                    "url": "",
                    "title": "Er werd een ticket geopend",
                    "description": f"{user.mention}, ik heb een ticket geopend voor u.\
                        \nU word zo spoedig mogelijk geholpen door een medewerker.\
                        \nGelieve even geduldig af te wachten. Alvast bedankt",
                    "author": "",
                    "items": {}
                }

                dmchannel = await user.create_dm()
                embed = await return_embed(dict_)
                await channel.send(embed=embed)

                dict_ = {
                    "url": "",
                    "title": "Er werd een ticket geopend",
                    "description": f"{user.mention}, ik heb een ticket geopend voor u.\
                        \nU word zo spoedig mogelijk geholpen door een medewerker.\
                        \nGelieve even geduldig af te wachten. Alvast bedankt\
                        \n\
                        \n[Klik hier om naar uw ticket te gaan.](https://discord.com/channels/875098573262438420/{channel.id})",
                    "author": "",
                    "items": {}
                }

                embed = await return_embed(dict_)
                await dmchannel.send(embed=embed)
                
            except:
                pass

            try:
                naam = tickettype
                dict_ = {
                    "url": "",
                    "title": "Helpdesk",
                    "description": f"{user.mention}, gelieve alvast het volgende klaar te houden:\
                        \n- uw klantnummer (indien beschikbaar)\
                        \n- uw identiteitskaart\n- uw rijbewijs\
                        \n\
                        \nU mag ook al vast uw {naam} plaatsen.\
                        \n\
                        \nAlvast bedankt voor uw geduld en onze excuses indien uw enige hinder ervaart\
                        in de tussentijd.\
                        \nU word zo snel mogelijk verder geholpen.",
                    "author": "",
                    "items": {}
                }

                embed = await return_embed(dict_)
                await channel.send(embed=embed)
            except:
                pass

            sql = "INSERT INTO `tbl_tickets`(`id`, `channelid`, `agent_discordid`, `client_discordid`, `reviewid`) VALUES (NULL, %s, %s, %s, %s);"
            mycursor.execute(sql, (channel.id, None, user.id, None))
            mydb.commit()
        else:
            try:
                dict_ = {
                    "url": "",
                    "title": "Er ging iets mis",
                    "description": f"{user.mention}, u heeft momenteel al te veel tickets open staan.",
                    "author": "",
                    "items": {}
                }

                dmchannel = await user.create_dm()
                embed = await return_embed(dict_)
                await dmchannel.send(embed=embed)
            except:
                pass

    @discord.ui.button(label="❗ Ik heb een probleem ❗", style=discord.ButtonStyle.danger, custom_id="probleem")
    async def probleem(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.button_action(interaction, button)
    
    @discord.ui.button(label="❓ Ik heb een vraag ❓", style=discord.ButtonStyle.danger, custom_id='vraag')
    async def vraag(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.button_action(interaction, button)

    @discord.ui.button(label="📋 Ik wil graag product x 📋", style=discord.ButtonStyle.danger, custom_id='aanvraag')
    async def aanvraag(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.button_action(interaction, button)

    @discord.ui.button(label="😱 Ik heb een ongeluk gehad 😱", style=discord.ButtonStyle.danger, custom_id='claim')
    async def claim(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.button_action(interaction, button)

class tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def rename(self, ctx, tmpname: str):
        if general.check_perms('basic', ctx.author) and general.isTicket(ctx.channel.category_id):
            current_channel = ctx.message.channel
            channel_icon = current_channel.name[:1]
            newname = f"{channel_icon}-{tmpname}"
            await current_channel.edit(name = newname)

    @commands.command(aliases=['lift'])
    async def elevate(self, ctx):
        # Moved nog uit directeur
        if general.check_perms('basic', ctx.author):
            current_channel = ctx.message.channel
            current_category = current_channel.category_id

            try:
                next_category_id = general.get_next_category(current_category)
            except ValueError:
                await ctx.send(f'{ctx.author.mention}, dat is niet mogelijk in dit kanaal.', delete_after=10)
            else:
                next_category = ctx.guild.get_channel(next_category_id)            
                await current_channel.edit(category = next_category, sync_permissions = True)

    @commands.command(aliases=['zekervanmij'])
    async def forceclaim(self, ctx, target: discord.Member = None):
        if general.check_perms('administrative', ctx.author):
            if general.isTicket(ctx.channel.category_id):
                load_dotenv()
                
                mydb = mysql.connector.connect(
                    host=os.getenv('DB_SERVERNAME'),
                    user=os.getenv('DB_USERNAME'),
                    password=os.getenv('DB_PASSWORD'),
                    database=os.getenv('DB_NAME')
                )
                
                # Agent claimt de ticket
                channelid = ctx.channel.id
                agent_discordid = None

                if target == None:
                    agent_discordid = ctx.author.id
                else:
                    agent_discordid = target.id

                sql = "SELECT `client_discordid` FROM `tbl_tickets` WHERE `channelid` = %s;"
                mycursor = mydb.cursor()
                mycursor.execute(sql, (channelid,))
                myresult = mycursor.fetchone()        

                if not myresult[0] == None and not myresult[0] == "":
                    client_discordid = int(myresult[0])
                    sql = "UPDATE `tbl_tickets` SET `agent_discordid` = %s WHERE `channelid` LIKE %s;"
                    mycursor.execute(sql, (agent_discordid, channelid))
                    mydb.commit()
                    member = discord.utils.get(ctx.guild.members, id=client_discordid)
                    dict_ = {
                        "url": "",
                        "title": "Ticket opnieuw geclaimt",
                        "description": f"{member.mention}, uw ticket werd ditmaal geclaimt door {ctx.author.mention}. \
                            \nDie medewerker zal u verder helpen.",
                        "author": "",
                        "items": {}
                    }

                    try:
                        channel = await member.create_dm()
                        embed = await return_embed(dict_)
                        await channel.send(embed=embed)
                    except:
                        pass

                    await make_embed(self, ctx, dict_)

                    log_dict = {
                        "mod": ctx.author.id,
                        "user": member.id,
                        "reason": "",
                        "unixtime": int(time.time()),
                        "perms": "tickets",
                        "type": 5
                    }

                    make_log(log_dict)
                    await make_discord_log(self, ctx, log_dict)
                else:
                    dict_ = {
                        "url": "",
                        "title": "Probleempje!",
                        "description": f"{ctx.author.mention}, er ging iets mis in ons systeem.\
                            \nOnze oprechte excuses. \
                            \n \
                            \nU word zo snel mogelijk verder geholpen.",
                        "author": "",
                        "items": {}
                    }

                    await make_embed(self, ctx, dict_)

                    dict_ = {
                        "url": "",
                        "title": "Probleempje!",
                        "description": f"{self.bot.boss.mention}, kan u dit verhelpen zodat \
                            de collega's verder kunnen met het helpen van de klant? \
                            \n \
                            \n[Klik hier om naar die ticket te gaan.](https://discord.com/channels/875098573262438420/{ctx.channel.id})",
                        "author": "",
                        "items": {}
                    }

                    embed = await return_embed(dict_)
                    await ctx.bot.alertchannel.send(embed=embed)            
        else:
            await ctx.send(f"{ctx.author.mention}, u heeft niet voldoende permissies om dat te doen.")

    @commands.command(aliases=['vanmij'])
    async def claim(self, ctx):
        if general.check_perms('basic', ctx.author):
            if general.isTicket(ctx.channel.category_id):

                load_dotenv()
                mydb = mysql.connector.connect(
                    host=os.getenv('DB_SERVERNAME'),
                    user=os.getenv('DB_USERNAME'),
                    password=os.getenv('DB_PASSWORD'),
                    database=os.getenv('DB_NAME')
                )
                
                # Agent claimt de ticket
                channelid = ctx.channel.id
                agent_discordid = ctx.author.id
                sql = "SELECT `client_discordid`, `agent_discordid` FROM `tbl_tickets` WHERE `channelid` = %s;"
                mycursor = mydb.cursor()
                mycursor.execute(sql, (channelid,))
                myresult = mycursor.fetchone()        

                if not myresult[0] == None and not myresult[0] == "":
                    if myresult[1] == None or myresult[1] == "":
                        client_discordid = int(myresult[0])
                        sql = "UPDATE `tbl_tickets` SET `agent_discordid` = %s WHERE `channelid` LIKE %s;"
                        mycursor.execute(sql, (agent_discordid, channelid))
                        mydb.commit()
                        member = discord.utils.get(ctx.guild.members, id=client_discordid)
                        dict_ = {
                            "url": "",
                            "title": "Ticket geclaimt",
                            "description": f"{member.mention}, uw ticket werd geclaimt door {ctx.author.mention}. \
                                \nDie medewerker zal u verder helpen.",
                            "author": "",
                            "items": {}
                        }

                        try:
                            channel = await member.create_dm()
                            embed = await return_embed(dict_)
                            await channel.send(embed=embed)
                        except:
                            pass

                        await make_embed(self, ctx, dict_)

                        log_dict = {
                            "mod": ctx.author.id,
                            "user": member.id,
                            "reason": "",
                            "unixtime": int(time.time()),
                            "perms": "tickets",
                            "type": 5
                        }

                        make_log(log_dict)
                        await make_discord_log(self, ctx, log_dict)
                    else:
                        dict_ = {
                            "url": "",
                            "title": "Ticket reeds geclaimt",
                            "description": f"{ctx.author.mention}, u dient contact op te nemen met een "\
                            "manager om de ticket te laten claimen "\
                            "aangezien deze ticket al reeds geclaimt.",
                            "author": "",
                            "items": {}
                        }
                        embed = await return_embed(dict_)
                        await ctx.send(embed=embed, delete_after=10)
                else:
                    dict_ = {
                        "url": "",
                        "title": "Probleempje!",
                        "description": f"{ctx.author.mention}, er ging iets mis in ons systeem.\
                            \nOnze oprechte excuses. \
                            \n \
                            \nU word zo snel mogelijk verder geholpen.",
                        "author": "",
                        "items": {}
                    }

                    await make_embed(self, ctx, dict_)

                    dict_ = {
                        "url": "",
                        "title": "Probleempje!",
                        "description": f"{self.bot.boss.mention}, kan u dit verhelpen zodat \
                            de collega's verder kunnen met het helpen van de klant? \
                            \n \
                            \n[Klik hier om naar die ticket te gaan.](https://discord.com/channels/875098573262438420/{ctx.channel.id})",
                        "author": "",
                        "items": {}
                    }

                    embed = await return_embed(dict_)
                    await ctx.bot.alertchannel.send(embed=embed)
        else:
            await ctx.send(f"{ctx.author.mention}, u heeft niet voldoende permissies om dat te doen.")

    @commands.command(aliases=['afhandelen', 'afgehandeld', 'close'])
    async def done(self, ctx):
        if general.check_perms('basic', ctx.author) and general.isTicket(ctx.channel.category_id):
            load_dotenv()
            mydb = mysql.connector.connect(
                host=os.getenv('DB_SERVERNAME'),
                user=os.getenv('DB_USERNAME'),
                password=os.getenv('DB_PASSWORD'),
                database=os.getenv('DB_NAME')
            )

            dict_ = {
                "url": "",
                "title": "Ticket afgehandeld",
                "description": f"Bedankt voor uw bericht, deze ticket word zo gesloten.",
                "author": "",
                "items": {}
            }

            await make_embed(self, ctx, dict_)
            #await sleep(10)

            categoryName = ctx.channel.category.name
            done_category = discord.utils.get(ctx.guild.categories, id=918437901031849984)
            
            dict_ = {
                "url": "",
                "title": "Ticket afgehandeld",
                "description": f"Ticket werd afgehandeld door {ctx.author}.",
                "author": "",
                "items": {}
            }

            await make_embed(self, ctx, dict_)
            await ctx.message.channel.edit(category = done_category)
            allroles = ctx.channel.changed_roles
            
            for role in allroles:
                try:
                    if not role == self.bot.jmrole and not role == self.bot.superrole:
                        await ctx.channel.set_permissions(role, read_messages=False, send_messages=False)
                except:
                    pass
            
            try:
                await ctx.channel.set_permissions(self.bot.jmrole, read_messages=True, send_messages=True)
            except:
                pass
            
            try:
                await ctx.channel.set_permissions(self.bot.superrole, read_messages=True, send_messages=True)
            except:
                pass
            
            bot_speaks(self.bot, f'{ctx.author.name} heeft {ctx.channel.name} gemoved naar afgehandeld.')
            sql = "SELECT `client_discordid`, `agent_discordid` FROM `tbl_tickets` WHERE `channelid` LIKE %s;"
            mycursor = mydb.cursor(buffered=True)
            mycursor.execute(sql, (ctx.channel.id,))        
            myresult = mycursor.fetchone()
            client = await returnMember(ctx, myresult[0])

            log_dict = {
                "mod": ctx.author.id,
                "user": client.id,
                "reason": "afgehandeld",
                "unixtime": int(time.time()),
                "perms": "tickets",
                "type": 4
            }

            try:
                channel = await client.create_dm()
                embed = await return_embed(dict_)
                await channel.send(embed=embed)
            except:
                pass

            make_log(log_dict)
            await make_discord_log(self, ctx, log_dict)

            werknemer = None            
            categoryLevel = int(categoryName[len(categoryName) - 1:])
            await ctx.send(categoryLevel)

            if len(myresult) >= 2 and myresult[1] != None:
                def getEmployee(discordID):
                    # Werknemer gegevens ophalen
                    sql = "SELECT * FROM `tbl_agents` WHERE `discordID` LIKE %s;"            
                    mycursor.execute(sql, (int(discordID),))
                    myresult = mycursor.fetchone()

                    return Employee(
                        id=myresult[0],
                        fivemID=myresult[1],
                        discordID=myresult[2],
                        bsn=myresult[3],
                        fname=myresult[4],
                        lname=myresult[5],
                        pwd=myresult[6],
                        dob=myresult[7],
                        enabled=myresult[8]
                    )

                werknemer = getEmployee(int(myresult[1]))                
                amount = 500 * categoryLevel
                
                sql = """INSERT INTO `tbl_sales`(
                    `id`,
                    `agentID`,
                    `amount`,
                    `reason`,
                    `timestamp`
                ) VALUES (NULL, %s, %s, %s, %s);"""

                mycursor.execute(sql, (
                    werknemer.id,
                    amount,
                    f"Ticket lvl-{categoryLevel} afgehandelt.",
                    datetime.datetime.today().timestamp()
                ))

                mydb.commit()

            dict_ = {
                "url": "",
                "title": f"Ticket lvl-{categoryLevel} werd afgehandeld",
                "description": f"{ctx.author.mention} heeft de ticket gesloten.",
                "author": "",
                "items": {}
            }
            
            if len(myresult) >= 2 and myresult[1] != None:
                werknemerMember = await returnMember(ctx, werknemer.discordID)
                dict_["description"] += f" Deze was geclaimd door {werknemerMember.mention}, hiervoor wordt €500,00 uitgekeerd."
            else:
                dict_["description"] += " Deze was niet geclaimd."

            embed = await return_embed(dict_)
            await self.bot.administrativelog.send(embed=embed)
        else:
            await ctx.send(f'{ctx.author.mention}, jammer genoeg heeft u niet genoeg permissies.', delete_after=10)

    @commands.command()
    async def survey(self, ctx, target: discord.Member = None):
        def checkreaction(reaction, user):
            return user == target and reaction.message.channel == ctx.channel

        def checkmessage(m):
            return m.channel == ctx.channel and m.author == target

        if general.check_perms('basic', ctx.author):
            # Survey
            # U werd geholpen door ctx.author
            if general.isTicket(ctx.channel.category_id):
                load_dotenv()
                mydb = mysql.connector.connect(
                    host=os.getenv('DB_SERVERNAME'),
                    user=os.getenv('DB_USERNAME'),
                    password=os.getenv('DB_PASSWORD'),
                    database=os.getenv('DB_NAME')
                )

                mycursor = mydb.cursor()

                try:
                    sql = "SELECT * FROM `tbl_tickets` WHERE `channelid` LIKE %s;"                    
                    mycursor.execute(sql, (ctx.channel.id,))
                    myresult = mycursor.fetchone()
                except:
                    bot_speaks(self.bot, f"Ticket met naam {ctx.channel.name} en id {ctx.channel.id} werd niet gevonden.")
                    
                    dict_ = {
                        "url": "",
                        "title": "Probleempje!",
                        "description": f"{ctx.author.mention}, er ging iets mis in ons systeem.\
                            \nOnze oprechte excuses. \
                            \n \
                            \nU word zo snel mogelijk verder geholpen.",
                        "author": "",
                        "items": {}
                    }

                    await make_embed(self, ctx, dict_)

                    dict_ = {
                        "url": "",
                        "title": "Probleempje!",
                        "description": f"{self.bot.boss.mention}, kan u dit verhelpen zodat \
                            de collega's verder kunnen met het helpen van de klant? \
                            \n \
                            \nTicket werd niet gevonden in tbl_tickets. \
                            \n[Klik hier om naar die ticket te gaan.](https://discord.com/channels/875098573262438420/{ctx.channel.id})",
                        "author": "",
                        "items": {}
                    }

                    embed = await return_embed(dict_)
                    await ctx.bot.alertchannel.send(embed=embed)
                else:
                    ticketid = int(myresult[0])
                    ticketchannelid = int(myresult[1])
                    ticketagentid = int(myresult[2])
                    ticketclientid = int(myresult[3])

                    if target == None or target == "":
                        target = discord.utils.get(ctx.guild.members, id=ticketclientid)
                                                                
                    dict_ = {
                        "url": "",
                        "title": "Ticket survey",
                        "description": f"{target.mention} werd geholpen door {ctx.author.mention}.\nWenst u deel te nemen aan onze survey?",
                        "author": "",
                        "items": {}
                    }
                    
                    permission_embed = await return_embed(dict_)
                    permission_msg = await ctx.send(embed=permission_embed)
                    await permission_msg.add_reaction('👍')
                    await permission_msg.add_reaction('👎')
                    reaction = await self.bot.wait_for('reaction_add', timeout=120.0, check=checkreaction)

                    if str(reaction[0].emoji) == '👍':
                        reaction_message = None
                        goedGenoeg = False
                        while not goedGenoeg:
                            dict_ = {
                                "url": "",
                                "title": "Kort samengevat",
                                "description": f"{target.mention}, beschrijf kort wat je er van vond.",
                                "author": "",
                                "items": {}
                            }
                            
                            await make_embed(self, ctx, dict_)                            
                            reaction_message = await self.bot.wait_for('message', timeout=120.0, check=checkmessage)
                            
                            dict_ = {
                                "url": "",
                                "title": "Bevestiging",
                                "description": f"{target.mention}, wilt u hier nog iets aan wijzigen?\
                                    \n\n__**Uw huidig antwoord:**__\
                                    \n{reaction_message}",
                                "author": "",
                                "items": {}
                            }
                            
                            embed = await return_embed(dict_)                                                   
                            message = await ctx.send(embed=embed)
                            await message.add_reaction('👍')
                            await message.add_reaction('👎')
                            reaction = await self.bot.wait_for('reaction_add', timeout=120.0, check=checkreaction)

                            if str(reaction[0].emoji) == '👎':
                                goedGenoeg = True
            
                        dict_ = {
                            "url": "",
                            "title": "Hoeveel sterren geeft u ons?",
                            "description": f"{target.mention}, gelieve een emote te kiezen.",
                            "author": "",
                            "items": {}
                        }

                        aantal_sterren = 1
                        embed = await return_embed(dict_)
                        starmessage = await ctx.send(embed=embed)
                        await starmessage.add_reaction('5️⃣')
                        await starmessage.add_reaction('4️⃣')
                        await starmessage.add_reaction('3️⃣')
                        await starmessage.add_reaction('2️⃣')
                        await starmessage.add_reaction('1️⃣')

                        try:
                            reaction = await self.bot.wait_for('reaction_add', timeout=240.0, check=checkreaction)
                        except:
                            aantal_sterren = 5
                            pass
                        else:
                            if str(reaction[0].emoji) == '5️⃣':
                                aantal_sterren = 5
                            if str(reaction[0].emoji) == '4️⃣':
                                aantal_sterren = 4
                            if str(reaction[0].emoji) == '3️⃣':
                                aantal_sterren = 3
                            if str(reaction[0].emoji) == '2️⃣':
                                aantal_sterren = 2
                            if str(reaction[0].emoji) == '1️⃣':
                                aantal_sterren = 1
                        
                        huidige_tijd = int(time.time())

                        sql = "SELECT `id` FROM `tbl_agents` WHERE `discordID` LIKE %s;"
                        try:
                            mycursor.execute(sql, (ticketagentid,))
                            myresult = mycursor.fetchone()
                        except:
                            dict_ = {
                                "url": "",
                                "title": "Probleempje",
                                "description": f"{ctx.mention} heeft zijn Discord nog niet (laten linken) gelinkt.\
                                    \nKunnen jullie dit regelen?\
                                    \n\
                                    \n[Klik hier om naar die ticket te gaan.](https://discord.com/channels/875098573262438420/{ctx.channel.id})",
                                "author": "",
                                "items": {}
                            }

                            embed = await return_embed(dict_)
                            await self.bot.leveltwochannel.send(embed=embed)
                            # Nog loggen naar lvl 2
                        else:
                            agentid = myresult[0]

                        sql = "SELECT `id` FROM `tbl_clients` WHERE `discordID` LIKE %s;"                        
                        clientid = None
                        try:
                            mycursor.execute(sql, (ticketclientid,))
                            myresult = mycursor.fetchone()
                            clientid = int(myresult[0])
                        except:
                            dict_ = {
                                "url": "",
                                "title": "Probleempje",
                                "description": f"{target.mention}, u moet uw Discord nog laten linken met uw klantenaccount. \
                                    \nEen andere mogelijkheid is dat u geen geregistreerde klant bent. \
                                    \n\
                                    \nZonder gelinkt Discord account kan ik u geen review laten plaatsen.",
                                "author": "",
                                "items": {}
                            }

                            await make_embed(self, ctx, dict_)
                            

                        sql = "INSERT INTO `tbl_reviews`(`id`, `agentID`, `clientID`, `review`, `stars`, `unixtime`, `verified`) VALUES (NULL, %s, %s, %s, %s, %s, 0);"
                        mycursor.execute(sql, (agentid, clientid, reaction_message.content, aantal_sterren, huidige_tijd))
                        mydb.commit()

                        sql = "SELECT `id` FROM `tbl_reviews` WHERE `agentID` LIKE %s AND `clientID` LIKE %s AND `review` LIKE %s AND `unixtime` LIKE %s;"
                        mycursor.execute(sql, (agentid, clientid, reaction_message.content, huidige_tijd))
                        myresult = mycursor.fetchone()
                        reviewid = myresult[0]

                        sql = "UPDATE `tbl_tickets` SET `reviewid` = %s WHERE `channelid` LIKE %s;"
                        mycursor.execute(sql, (reviewid, ctx.channel.id))
                        mydb.commit()

                        log_dict = {
                            "mod": ctx.author.id,
                            "user": target.id,
                            "reason": f"Er is een review toegevoegd voor {ctx.author.mention} door {target.mention}:\n*{reaction_message.content}*",
                            "unixtime": int(time.time()),
                            "perms": "tickets",
                            "type": 6
                        }

                        make_log(log_dict)
                        await make_discord_log(self, ctx, log_dict)
                    
                    else:
                        dict_ = {
                            "url": "",
                            "title": "Ticket survey",
                            "description": f"{target.mention} dat is helemaal geen probleem.\nFijne dag verder!",
                            "author": "",
                            "items": {}
                        }
                        
                        await make_embed(self, ctx, dict_)
            else:
                await ctx.send(f"{ctx.author.mention}, deze actie dient u wel te doen in een ticket kanaal.", delete_after=20)
        else:
            await ctx.send(f"{ctx.author.mention}, jammer genoeg heeft u niet genoeg permissies.", delete_after=10)
    
    @commands.command(aliases=['toevoegen', 'voegtoe'])
    async def add(self, ctx, target: typing.Union[discord.Role, discord.Member] = None):
        if general.check_perms('basic', ctx.author) and general.isTicket(ctx.channel.category_id):
                await ctx.channel.set_permissions(target, read_messages=True, send_messages=True)

    @commands.command(aliases=['haalweg', 'verwijder'])
    async def remove(self, ctx, target: typing.Union[discord.Role, discord.Member] = None):
        if general.check_perms('basic', ctx.author) and general.isTicket(ctx.channel.category_id):
            await ctx.channel.set_permissions(target, read_messages=False, send_messages=False)

async def setup(bot):
    await bot.add_cog(tickets(bot))