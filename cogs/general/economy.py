import os
import time
import yaml
import logs
import general
import discord
import settings
import datetime
import mysql.connector
from copy import copy
from dateutil.parser import parse
from dotenv.main import load_dotenv
from discord.ext import commands
from general_bot import bot_speaks

class economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def repairkit(self, ctx, commandtype: str, *, args = None):
        hoeveelheid = None
        reden = None

        def checkmessage(m):
            return m.channel == ctx.channel and m.author == ctx.author

        async def vraag(self, ctx, soort, action=None):
            dict_ = None

            if soort == "reden":
                dict_ = {
                    "url": "",
                    "title": "Reden",
                    "description": f"{ctx.author.mention}, wat mag ik noteren als reden?",
                    "author": "",
                    "items": {}
                }                            

            if soort == "hoeveelheid":
                dict_ = {
                    "url": "",
                    "title": "Reden",
                    "description": f"{ctx.author.mention}, u heeft geen hoeveelheid opgegeven.",
                    "author": "",
                    "items": {}
                }

                if action == "nemen":
                    dict_["description"] = dict_["description"] + " Hoeveel wilt u er meenemen?"

                if action == "toevoegen":
                    dict_["description"] = dict_["description"] + " Hoeveel wilt u er toevoegen?"
            
            embed = await logs.return_embed(dict_)
            await ctx.send(embed=embed, delete_after=60)

        async def verkrijg(self, ctx, soort, action=None):
            await vraag(self, ctx, soort, action)
            message = await self.bot.wait_for('message', timeout=120.0, check=checkmessage)
            await message.delete()
            return message.content

        await ctx.message.delete()
        if general.check_perms('administrative', ctx.author):            
            repairkits = general.open_yaml("repairkits")

            if commandtype == "take" or commandtype == "neem":
                try:
                    args = list(args.split(' '))
                except:
                    pass
                
                try:
                    hoeveelheid = args[0]
                except:
                    hoeveelheid = await verkrijg(self, ctx, "hoeveelheid", "nemen")

                try:
                    reden = args[1]
                except:
                    reden = await verkrijg(self, ctx, "reden")
                
                repairkits = repairkits - int(hoeveelheid)
                woord = "werd"

                if int(hoeveelheid) > 1:
                    woord = woord + "en"

                dict_ = {
                    "url": "",
                    "title": "Repairkits aantal gewijzigd",
                    "description": f"{self.bot.boss.mention}, er {woord} {hoeveelheid} repairkits \
                        uit de kluis gehaald door {ctx.author.mention} met als reden: {reden}.\
                        Er liggen er nu {repairkits} in de kluis.",
                    "author": "",
                    "items": {}
                }

                embed = await logs.return_embed(dict_, 0xFF0000)
                channel = self.bot.get_channel(general.return_log_channel_id("repairkits"))
                await channel.send(embed=embed)

            if commandtype == "add" or commandtype == "voegtoe" or commandtype == "toevoegen":
                try:
                    args = list(args.split(' '))
                except:
                    pass
                
                try:
                    hoeveelheid = args[0]
                except:
                    hoeveelheid = await verkrijg(self, ctx, "hoeveelheid", "toevoegen")

                try:
                    reden = args[1]
                except:
                    reden = await verkrijg(self, ctx, "reden")
                
                repairkits = repairkits + int(hoeveelheid)
                woord = "werd"

                if int(hoeveelheid) > 1:
                    woord = woord + "en"

                dict_ = {
                    "url": "",
                    "title": "Repairkits aantal gewijzigd",
                    "description": f"{self.bot.boss.mention}, er {woord} {hoeveelheid} repairkits \
                        toegevoegd in de kluis door {ctx.author.mention} met als reden: {reden}.\
                        Er liggen er nu {repairkits} in de kluis.",
                    "author": "",
                    "items": {}
                }

                embed = await logs.return_embed(dict_, 0x008000)
                channel = self.bot.get_channel(general.return_log_channel_id("repairkits"))
                await channel.send(embed=embed)
                general.write_yaml("repairkits", repairkits)

            if commandtype == "zie" or commandtype == "see" or commandtype == "huidig" or commandtype == "current":
                repairkits = general.open_yaml("repairkits")
                woord = "zit"
                multiple = ""

                if repairkits > 1:
                    woord = woord + "ten"
                    multiple = "s"

                dict_ = {
                    "url": "",
                    "title": "Repairkits aantal gewijzigd",
                    "description": f"{ctx.author.mention}, er {woord} momenteel nog \
                        {repairkits} repairkit{multiple} in de kluis.",
                    "author": "",
                    "items": {}
                }                
                embed = await logs.return_embed(dict_, 0x1E90FF)
                await ctx.send(embed=embed, delete_after=20)

    @commands.command()
    async def kluis(self, ctx, commandtype: str, *, args = None):    
        hoeveelheid = None
        reden = None

        load_dotenv()
                    
        mydb = mysql.connector.connect(
            host=os.getenv('DB_SERVERNAME'),
            user=os.getenv('DB_USERNAME'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME')
        )

        mycursor = mydb.cursor()

        def transactie_log(hoeveelheid, reden):
            sql = "INSERT INTO `tbl_transactions` (`id`, `agentID`, `text`, `amount`, `timestamp`) VALUES (NULL, %s, %s, %s, %s);"
            agent = getEmployee(ctx.author.id)
            agentID = agent[0][0]
            mycursor.execute(sql, (agentID, reden, hoeveelheid, int(time.time())))
            mydb.commit()

        def getEmployee(discordID):
            # Werknemer gegevens ophalen
            sql = "SELECT * FROM `tbl_agents` WHERE `discordID` LIKE '%s';"
            mycursor.execute(sql, (int(discordID),))
            return mycursor.fetchall()

            

        def checkreaction(reaction, user):
            return user == ctx.author and reaction.message.channel == ctx.channel

        def checkmessage(m):
            return m.channel == ctx.channel and m.author == ctx.author

        async def vraag(self, ctx, soort, action=None):
            dict_ = None

            if soort == "reden":
                dict_ = {
                    "url": "",
                    "title": "Reden",
                    "description": f"{ctx.author.mention}, wat mag ik noteren als reden?",
                    "author": "",
                    "items": {}
                }                            

            if soort == "hoeveelheid":
                dict_ = {
                    "url": "",
                    "title": "Reden",
                    "description": f"{ctx.author.mention}, u heeft geen hoeveelheid opgegeven.",
                    "author": "",
                    "items": {}
                }

                if action == "nemen":
                    dict_["description"] = dict_["description"] + " Hoeveel cash geld wilt u opnemen?"

                if action == "toevoegen":
                    dict_["description"] = dict_["description"] + " Hoeveel cash geld wilt u toevoegen?"
            
            embed = await logs.return_embed(dict_)
            await ctx.send(embed=embed, delete_after=60)

        async def verkrijg(self, ctx, soort, action=None):
            await vraag(self, ctx, soort, action)
            message = await self.bot.wait_for('message', timeout=120.0, check=checkmessage)
            await message.delete()
            return message.content

        await ctx.message.delete()
        if general.check_perms('administrative', ctx.author):
            kluis = general.open_yaml("kluis")

            if commandtype == "take" or commandtype == "neem":
                try:
                    args = list(args.split(' '))
                except:
                    pass
                
                try:
                    hoeveelheid = args[0]
                except:
                    hoeveelheid = await verkrijg(self, ctx, "hoeveelheid", "nemen")

                try:
                    reden = args[1]
                except:
                    reden = await verkrijg(self, ctx, "reden")
                
                transactie_log(0 - int(hoeveelheid), reden)
                kluis = kluis - int(hoeveelheid)
                hoeveelheid = format(int(hoeveelheid), ',')
                kluistmp = format(int(kluis), ',')
 
                dict_ = {
                    "url": "",
                    "title": "Hoeveelheid cash gewijzigd",
                    "description": f"{self.bot.boss.mention}, er werd €{hoeveelheid.replace(',', '.')},00 \
                        uit de kluis gehaald door {ctx.author.mention} met als reden: {reden}.\
                        Er ligt nu €{kluistmp.replace(',', '.')},00 in de kluis.",
                    "author": "",
                    "items": {}
                }
                
                embed = await logs.return_embed(dict_, 0xFF0000)
                channel = self.bot.get_channel(general.return_log_channel_id("kluis"))
                await channel.send(embed=embed)

            if commandtype == "add" or commandtype == "voegtoe" or commandtype == "toevoegen":
                try:
                    args = list(args.split(' '))
                except:
                    pass
                
                try:
                    hoeveelheid = args[0]
                except:
                    hoeveelheid = await verkrijg(self, ctx, "hoeveelheid", "toevoegen")

                try:
                    reden = args[1]
                except:
                    reden = await verkrijg(self, ctx, "reden")
                
                transactie_log(int(hoeveelheid), reden)
                kluis = kluis + int(hoeveelheid)
                hoeveelheid = format(int(hoeveelheid), ',')
                kluistmp = format(int(kluis), ',')

                dict_ = {
                    "url": "",
                    "title": "Hoeveelheid cash gewijzigd",
                    "description": f"{self.bot.boss.mention}, er werd €{hoeveelheid.replace(',', '.')},00 \
                        in de kluis gelegd door {ctx.author.mention} met als reden: {reden}.\
                        Er ligt nu €{kluistmp.replace(',', '.')},00 in de kluis.",
                    "author": "",
                    "items": {}
                }
                
                embed = await logs.return_embed(dict_, 0x008000)
                channel = self.bot.get_channel(general.return_log_channel_id("kluis"))
                await channel.send(embed=embed)
                general.write_yaml("kluis", kluis)

            if commandtype == "zie" or commandtype == "see" or commandtype == "huidig" or commandtype == "current":
                kluis = general.open_yaml("kluis")
                hoeveelheid = format(kluis, ',')
                hoeveelheid = hoeveelheid.replace(',', '.')
                dict_ = {
                    "url": "",
                    "title": "Repairkits aantal gewijzigd",
                    "description": f"{ctx.author.mention}, er zit momenteel €{hoeveelheid},00 \
                        in de kluis.",
                    "author": "",
                    "items": {}
                }                
                embed = await logs.return_embed(dict_, 0x1E90FF)
                await ctx.send(embed=embed, delete_after=20)

async def setup(bot):
    await bot.add_cog(economy(bot))