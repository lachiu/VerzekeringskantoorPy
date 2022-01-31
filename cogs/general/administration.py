import os
import time
import signal
import typing
import discord
import general
import mysql.connector
from logs import return_embed
from logs import make_embed
from logs import make_log
from logs import make_discord_log
from dotenv.main import load_dotenv
from discord.ext import commands
from general_bot import bot_speaks

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

    async def button_action(self, button: discord.ui.Button, interaction: discord.Interaction, tickettype):
        load_dotenv()
        mydb = mysql.connector.connect(
            host=os.getenv('DB_SERVERNAME'),
            user=os.getenv('DB_USERNAME'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME')
        )

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

                dmchannel = await user.create_dm()
                embed = await return_embed(dict_)
                await dmchannel.send(embed=embed)
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

    @discord.ui.button(label="❗ Ik heb een probleem ❗", style=discord.ButtonStyle.danger, custom_id="channelbutton:probleem")
    async def probleem(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.button_action(button, interaction, "probleem")
    
    @discord.ui.button(label="❓ Ik heb een vraag ❓", style=discord.ButtonStyle.danger, custom_id='channelbutton:vraag')
    async def vraag(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.button_action(button, interaction, "vraag")

    @discord.ui.button(label="📋 Ik wil graag product x 📋", style=discord.ButtonStyle.danger, custom_id='channelbutton:aanvraag')
    async def aanvraag(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.button_action(button, interaction, "aanvraag")

    @discord.ui.button(label="😱 Ik heb een ongeluk gehad 😱", style=discord.ButtonStyle.danger, custom_id='channelbutton:claim')
    async def claim(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.button_action(button, interaction, "claim")

class administration(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        rolegivermessageid = int(general.open_yaml("rolegiver"))
        if rolegivermessageid == payload.message_id and not payload.user_id == self.bot.user.id:
            if str(payload.emoji) == '👌':
                message = await self.bot.ruleschannel.fetch_message(payload.message_id)
                vkgGuild = self.bot.get_guild(875098573262438420)
                role = vkgGuild.get_role(general.return_role_id("klant"))
                await payload.member.add_roles(role)

            await message.clear_reactions()
            await message.add_reaction('👌')

    @commands.command()
    async def setuprules(self, ctx):
        if general.check_perms('dev', ctx):
            vkgGuild = self.bot.get_guild(875098573262438420)
            await self.bot.ruleschannel.purge(limit=10, bulk=False)
            jobmanagers = discord.utils.get(vkgGuild.roles, id=general.return_role_id("job manager"))
            dict_ = {
                "url": "",
                "title": "Algemeen | Lid 1",
                "description": f"Hieronder vind u de regels die ten alle tijden gelden in deze Discord server.\
                    \nDeze server word uitsluitend beheerd door {self.bot.boss.mention}.\
                    \nDe {jobmanagers.mention} zijn ook aanwezig waar u, indien nodig ook naartoe kan.\
                    \n\
                    \nNa het behandeld hebben van uw ticket \
                    ([die vind u hier overigens terug](https://discord.com/channels/875098573262438420/918435738662629386)) \
                    vragen wij u om deel te nemen aan een review.\
                    \nDeze word, na beoordeling op spelling en grof taalgebruik, toegevoegd en getoond op onze site.",
                "author": "",
                "items": {}
            }
                
            embed = await return_embed(dict_)
            await self.bot.ruleschannel.send(embed=embed)

            dict_ = {
                "url": "",
                "title": "Algemeen | Lid 2",
                "description": f"{self.bot.user.mention} is onze secretaresse. Deze, en overigens onze andere \
                    medewerkers ook, dient u altijd met respect te benaderen.\
                    \nGebeurd dat niet? Dan kunnen wij sancties opleggen:\
                    \n- Waarschuwing\
                    \n- Mute\
                    \n- Kick\
                    \n- Ban\
                    \n- Sancties vanuit de gemeente\
                    \n- Blacklist\
                    \n\
                    \nIk hoop dat ik dat maar 1 keer hoef te herhalen.\
                    \nAls we ons allen aan deze regels kunnen houden komt het goed.",
                "author": "",
                "items": {}
            }
                
            embed = await return_embed(dict_)
            await self.bot.ruleschannel.send(embed=embed)

            dict_ = {
                "url": "",
                "title": "Regel 1",
                "description": f"Het is niet toegestaan om medewerkers te gaan PM'en of \
                    een vriendschapsverzoek te sturen of te bellen.",
                "author": "",
                "items": {}
            }
                
            embed = await return_embed(dict_)
            await self.bot.ruleschannel.send(embed=embed)

            dict_ = {
                "url": "",
                "title": "Regel 2",
                "description": f"Het bespreken van strafmaatregelen tegen andere klanten dient \
                    te geschieden in een ticket, bij voorkeur, of de algemene Discord.\
                    \n\
                    \nStaff lastigvallen om hier dingen geregeld te krijgen heeft ook geen effect.",
                "author": "",
                "items": {}
            }
                
            embed = await return_embed(dict_)
            await self.bot.ruleschannel.send(embed=embed)

            dict_ = {
                "url": "",
                "title": "Regel 3",
                "description": f"Taalgebruik verder dient te gebeuren met al het mogelijke respect voor anderen.\
                    \nMet ziektes schelden, het n-woord of andere racistische of seksistische uitspraken \
                    zijn hier ook niet welkom.",
                "author": "",
                "items": {}
            }
                
            embed = await return_embed(dict_)
            await self.bot.ruleschannel.send(embed=embed)

            dict_ = {
                "url": "",
                "title": "Regel 4",
                "description": f"Het is niet toegestaan om zinloze tickets te openen, \
                    te spammen (meerdere berichten, caps, emojis).",
                "author": "",
                "items": {}
            }
                
            embed = await return_embed(dict_)
            await self.bot.ruleschannel.send(embed=embed)

            dict_ = {
                "url": "",
                "title": "Regel 5",
                "description": f"Mocht het nog niet duidelijk zijn, het is dus de bedoeling \
                    dat u ten allen tijden met respect praat t.o.v. anderen.\
                    \nHet maakt niet uit of het een medewerker, vriend, burger of stafflid is.\
                    \n\
                    \nDe communicatie hier gebeurt strikt professioneel.",
                "author": "",
                "items": {}
            }
                
            embed = await return_embed(dict_)
            await self.bot.ruleschannel.send(embed=embed)

            dict_ = {
                "url": "",
                "title": "Regel 6",
                "description": f"Roddels of onwaarheden verspreiden (lees eerroof of laster) zal \
                    met harde hand op gereageerd worden (in RP).\
                    \n\
                    \nFouten kunnen gebeuren, dat is nu eenmaal menselijk.\
                    \nWe doen ons uiterste best om daar een compromis als oplossing in te bekomen, \
                    indien mogelijk.\
                    \nOnze excuses mocht dat bij u plaats vinden/hebben gevonden.\
                    \nWij streven naar professionaliteit en voortbrengen van een nieuwe RP in Grp.\
                    \nRoddels of onwaarheden verspreiden ",
                "author": "",
                "items": {}
            }
                
            embed = await return_embed(dict_)
            await self.bot.ruleschannel.send(embed=embed)

            dict_ = {
                "url": "",
                "title": "Regel 7",
                "description": f"Alle communicatie op dit kanaal na, gebeurt IC.\
                    \nDiscord word hulpcentrum/contactformulier.\
                    \nOverige termen lijken ons vanzelfsprekend.\
                    \nHet is dus ten strengste verboden om IC en OOC door elkaar te halen.\
                    \nHier zal streng op worden toegekeken.",
                "author": "",
                "items": {}
            }
                
            embed = await return_embed(dict_)
            await self.bot.ruleschannel.send(embed=embed)

            dict_ = {
                "url": "",
                "title": "Overeenkomst",
                "description": f"Indien u akkoord bent met deze regels en onze manier van werken \
                    klikt u vervolgens op de emoji hieronder.",
                "author": "",
                "items": {}
            }

            embed = await return_embed(dict_)
            message = await self.bot.ruleschannel.send(embed=embed)
            await message.add_reaction('👌')
            general.write_yaml("rolegiver", message.id)

    @commands.command()
    async def setupbutton(self, ctx):
        if general.check_perms('dev', ctx):
            dict_ = {
                "url": "",
                "title": "Verzekerings Kantoor Groningen - Supportcentrum",
                "description": "Klik hieronder op een van de knoppen om de juiste hulp te krijgen.",
                "author": "",
                "items": {}
            }
                
            embed = await return_embed(dict_)        
            await self.bot.ticketchannel.send(embed=embed, view=ChannelButton(self.bot))

    @commands.command(aliases=['waarschuw'])
    async def warn(self, ctx, member: discord.Member, *, reason="geen reden opgegeven"):
        if general.check_perms('administrative', ctx):
            dict_ = {
                "url": "",
                "title": "Waarschuwing gelogd",
                "description": f"{member.mention} werd gewaarschuwd voor: {reason}.",
                "author": "",
                "items": {}
            }
            
            await make_embed(self, ctx, dict_)

            log_dict = {
                "mod": ctx.author.id,
                "user": member.id,
                "reason": reason,
                "unixtime": int(time.time()),
                "perms": "administrative",
                "type": 0
            }

            make_log(log_dict)

            try:
                channel = await member.create_dm()
                embed = await return_embed(dict_)
                await channel.send(embed=embed)
            except:
                pass

            await make_discord_log(self, ctx, log_dict)
        else:
            await ctx.send(f'{ctx.author.mention}, jammer genoeg heeft u niet genoeg permissies.', delete_after=10)

    @commands.command(aliases=['stamp'])
    async def kick(self, ctx, member: discord.Member, *, reason="geen reden opgegeven"):
        if general.check_perms('administrative', ctx):
            dict_ = {
                "url": "",
                "title": "Kick gelogd",
                "description": f"{member.mention} werd gekickt voor: {reason}.",
                "author": "",
                "items": {}
            }

            await make_embed(self, ctx, dict_)

            log_dict = {
                "mod": ctx.author.id,
                "user": member.id,
                "reason": reason,
                "unixtime": int(time.time()),
                "perms": "administrative",
                "type": 1
            }

            make_log(log_dict)
            
            try:
                channel = await member.create_dm()
                embed = await return_embed(dict_)
                await channel.send(embed=embed)
            except:
                pass

            await make_discord_log(self, ctx, log_dict)
            await member.kick(reason=reason)
        else:
            await ctx.send(f'{ctx.author.mention}, jammer genoeg heeft u niet genoeg permissies.', delete_after=10)

    @commands.command(aliases=['banhamer'])
    async def ban(self, ctx, member: discord.Member, *, reason="geen reden opgegeven"):
        if general.check_perms('administrative', ctx):
            dict_ = {
                "url": "",
                "title": "Ban gelogd",
                "description": f"{member.mention} werd geband voor: {reason}.",
                "author": "",
                "items": {}
            }
            
            await make_embed(self, ctx, dict_)

            log_dict = {
                "mod": ctx.author.id,
                "user": member.id,
                "reason": reason,
                "unixtime": int(time.time()),
                "perms": "administrative",
                "type": 2
            }

            make_log(log_dict)

            try:
                channel = await member.create_dm()
                embed = await return_embed(dict_)
                await channel.send(embed=embed)
            except:
                pass

            await make_discord_log(self, ctx, log_dict)
            await member.ban(reason=reason)
        else:
            await ctx.send(f'{ctx.author.mention}, jammer genoeg heeft u niet genoeg permissies.', delete_after=10)

    @commands.command()
    async def unban(self, ctx, member, *, reason="geen reden opgegeven"):
        if general.check_perms('administrative', ctx):
            banned_users = await ctx.guild.bans()
            member_name, member_discriminator = member.split('#')

            for ban_entry in banned_users:
                user = ban_entry.user

                if (user.name, user.discriminator) == (member_name, member_discriminator):
                    dict_ = {
                        "url": "",
                        "title": "Unban gelogd",
                        "description": f"{member} werd geunband.",
                        "author": "",
                        "items": {}
                    }
                    
                    await make_embed(self, ctx, dict_)
                    
                    log_dict = {
                        "mod": ctx.author.id,
                        "user": user.id,
                        "reason": reason,
                        "unixtime": int(time.time()),
                        "perms": "administrative",
                        "type": 3
                    }
                    
                    make_log(log_dict)

                    try:
                        channel = await member.create_dm()
                        embed = await return_embed(dict_)
                        await channel.send(embed=embed)
                    except:
                        pass

                    await make_discord_log(self, ctx, log_dict)
                    await ctx.guild.unban(user)
                    return
        else:
            await ctx.send(f'{ctx.author.mention}, jammer genoeg heeft u niet genoeg permissies.', delete_after=10)

    @commands.command()
    async def purge(self, ctx, qty: int):
        if general.check_perms('administrative', ctx):
            await ctx.channel.purge(limit=(qty+1))

    @commands.command(aliases=['dc'])
    async def disconnect(self, ctx):
        if general.check_perms('dev', ctx):
            bot_speaks(self.bot, 'Ik sluit af.')
            await ctx.self.close()
            os.kill(os.getppid(), signal.SIGHUP)

    @commands.command(aliases=['reload'])
    async def reload_specific_cog_command(self, ctx, arg: str):        
        if general.check_perms('dev', ctx):
            await ctx.send(f'{ctx.author.mention}, ik ga proberen om {arg} te reloaden.', delete_after=10)
            cog = None

            if self.bot.coglist[arg]:
                cog = self.bot.coglist[arg]
                self.bot.reload_extension(cog)
                await ctx.send(f'{ctx.author.mention}, {arg} werd gereload.', delete_after=10)
                
            else:
                await ctx.send(f'{ctx.author.mention}, jammer genoeg is er geen cog met die naam.', delete_after=10)                            

    @commands.command(aliases=['geef'])
    async def _add_role(self, ctx, param_one: typing.Union[discord.Member, discord.Role, str], param_two: typing.Union[discord.Member, discord.Role, str]):
        member = None
        role = None
        run = True
        if general.check_perms('administrative', ctx):
            if isinstance(param_one, discord.Member):
                member = param_one
            elif isinstance(param_one, discord.Role):
                role = param_one
            elif isinstance(param_one, str):
                role = discord.utils.get(ctx.guild.roles, id=general.return_role_id(param_one))
            else:
                await ctx.send(f'{ctx.author.mention}, parameter :one: werd niet gevonden.')
                run = False
                
            if isinstance(param_two, discord.Member):
                member = param_two
            elif isinstance(param_two, discord.Role):
                role = param_two
            elif isinstance(param_two, str):
                role = general.return_role_id(param_two)
            else:
                await ctx.send(f'{ctx.author.mention}, parameter :two: werd niet gevonden.')
                run = False

            if run:
                bot_speaks(self.bot, f'{ctx.author} heeft voldoende permissies en geeft {member} de {role} rol.')
                await member.add_roles(role)
                await ctx.send(f'{ctx.author.mention}, het is gelukt. {member.mention} heeft nu de {role} rol.')
        else:
            await ctx.send(f'{ctx.author.mention}, u heeft niet voldoende permissies hiervoor.', delete_after=10)
        
    @commands.command(aliases=['neem'])
    async def _take_role(self, ctx, param_one: typing.Union[discord.Member, discord.Role, str], param_two: typing.Union[discord.Member, discord.Role, str]):
        member = None
        role = None
        run = True
        if general.check_perms('administrative', ctx):
            if isinstance(param_one, discord.Member):
                member = param_one
            elif isinstance(param_one, discord.Role):
                role = param_one
            elif isinstance(param_one, str):
                role = discord.utils.get(ctx.guild.roles, id=general.return_role_id(param_one))
            else:
                await ctx.send(f'{ctx.author.mention}, parameter :one: werd niet gevonden.', delete_after=10)
                run = False
                
            if isinstance(param_two, discord.Member):
                member = param_two
            elif isinstance(param_two, discord.Role):
                role = param_two
            elif isinstance(param_two, str):
                role = general.return_role_id(param_two)
            else:
                await ctx.send(f'{ctx.author.mention}, parameter :two: werd niet gevonden.', delete_after=10)
                run = False

            if run:
                bot_speaks(self.bot, f'{ctx.author} heeft voldoende permissies en neemt van {member} de {role} rol af.')
                await member.remove_roles(role)
                await ctx.send(f'{ctx.author.mention}, het is gelukt. {member.mention} heeft nu geen {role} rol meer.')
        else:
            await ctx.send(f'{ctx.author.mention}, u heeft niet voldoende permissies hiervoor.', delete_after=10)
        
def setup(bot):
    bot.add_cog(administration(bot))