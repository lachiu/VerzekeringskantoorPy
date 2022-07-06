import os
import yaml
import logs
import json
import random
import general
import discord
import settings
import datetime
import datetime
import cogs.functions
import mysql.connector
from dateutil import parser
from copy import copy
from mimetypes import init
from dateutil.parser import parse
from dotenv.main import load_dotenv
from discord.ext import commands
from general_bot import bot_speaks
from classes.employee import Employee
from classes.client import Client

class Employees(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def werknemer(self, ctx, commandtype: str, *, args = None):
        if general.check_perms('basic', ctx.author):
            load_dotenv()

            mydb = mysql.connector.connect(
                host=os.getenv('DB_SERVERNAME'),
                user=os.getenv('DB_USERNAME'),
                password=os.getenv('DB_PASSWORD'),
                database=os.getenv('DB_NAME')
            )
            
            mycursor = mydb.cursor()

            if args:
                args = args.split()

            toDeleteMessages = []

            def checkReaction(reaction, user):
                return user == ctx.author and reaction.message.channel == ctx.channel

            def checkMessage(m):
                return m.channel == ctx.channel and m.author == ctx.author
            
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

            async def showConfirmationScreen(givendict_):
                result = False
                dict_ = None

                if givendict_:
                    dict_ = givendict_
                else:
                    dict_ = {
                        "url": "",
                        "title": "Kloppen deze gegevens?",
                        "description": f"",
                        "author": "",
                        "items": {}
                    }

                embed = await logs.return_embed(dict_, color=0xffffff)
                message = await ctx.send(embed=embed)
                toDeleteMessages.append(message)
                list = ['✅', '❌']
                await cogs.functions.addReactions(message, list)
                reaction = await self.bot.wait_for('reaction_add', timeout=120.0, check=checkReaction)

                if str(reaction[0].emoji) == '✅':
                    result = True

                return result

            async def vraagFivem():
                validResult = False
                tmp = None
                while not validResult:
                    dict_ = {
                        "url": "",
                        "title": "Er ontbreken gegevens.",
                        "description": f"Wat is de werknemer zijn/haar stadscode?",
                        "author": "",
                        "items": {}
                    }

                    embed = await logs.return_embed(dict_, color=0xffffff)
                    message = await ctx.send(embed=embed)
                    toDeleteMessages.append(message)
                    message = await self.bot.wait_for('message', timeout=120.0, check=checkMessage)
                    toDeleteMessages.append(message)
                    tmp = message.content

                    dict_ = {
                        "url": "",
                        "title": "Klopt dit?",
                        "description": f"__**Nieuwe stadscode:**__\n{tmp}",
                        "author": "",
                        "items": {}
                    }

                    result = await showConfirmationScreen(dict_)

                    if result:
                        validResult = True

                return tmp

            async def vraagDiscord():
                validResult = False
                tmp = None
                while not validResult:
                    dict_ = {
                        "url": "",
                        "title": "Er ontbreken gegevens.",
                        "description": f"Wat is de werknemer zijn/haar gemeenteapp?",
                        "author": "",
                        "items": {}
                    }

                    embed = await logs.return_embed(dict_, color=0xffffff)
                    message = await ctx.send(embed=embed)
                    toDeleteMessages.append(message)
                    message = await self.bot.wait_for('message', timeout=120.0, check=checkMessage)
                    toDeleteMessages.append(message)
                    
                    try:
                        tmp = await cogs.functions.returnMember(ctx, message.content)
                    except:
                        pass
                    finally:
                        dict_ = {
                            "url": "",
                            "title": "Klopt dit?",
                            "description": f"__**Nieuwe gemeenteapp:**__\n{tmp.mention}",
                            "author": "",
                            "items": {}
                        }

                        result = await showConfirmationScreen(dict_)

                        if result:
                            validResult = True

                        return tmp.id

            async def vraagVoornaam():
                validResult = False
                tmp = None
                while not validResult:
                    dict_ = {
                        "url": "",
                        "title": "Er ontbreken gegevens.",
                        "description": f"Wat is de werknemer zijn/haar voornaam?",
                        "author": "",
                        "items": {}
                    }

                    embed = await logs.return_embed(dict_, color=0xffffff)
                    message = await ctx.send(embed=embed)
                    toDeleteMessages.append(message)
                    message = await self.bot.wait_for('message', timeout=120.0, check=checkMessage)
                    toDeleteMessages.append(message)
                    tmp = message.content

                    dict_ = {
                        "url": "",
                        "title": "Klopt dit?",
                        "description": f"__**Nieuwe voornaam:**__\n{tmp}",
                        "author": "",
                        "items": {}
                    }

                    result = await showConfirmationScreen(dict_)

                    if result:
                        validResult = True

                return tmp

            async def vraagAchternaam():
                validResult = False
                tmp = None
                while not validResult:
                    dict_ = {
                        "url": "",
                        "title": "Er ontbreken gegevens.",
                        "description": f"Wat is de werknemer zijn/haar achternaam?",
                        "author": "",
                        "items": {}
                    }

                    embed = await logs.return_embed(dict_, color=0xffffff)
                    message = await ctx.send(embed=embed)
                    toDeleteMessages.append(message)
                    message = await self.bot.wait_for('message', timeout=120.0, check=checkMessage)
                    toDeleteMessages.append(message)
                    tmp = message.content

                    dict_ = {
                        "url": "",
                        "title": "Klopt dit?",
                        "description": f"__**Nieuwe achternaam:**__\n{tmp}",
                        "author": "",
                        "items": {}
                    }

                    result = await showConfirmationScreen(dict_)

                    if result:
                        validResult = True
                
                return tmp            

            async def vraagDob():
                validResult = False
                tmp = None
                while not validResult:
                    dict_ = {
                        "url": "",
                        "title": "Er ontbreken gegevens.",
                        "description": f"Wat is de werknemer zijn/haar geboortedatum?",
                        "author": "",
                        "items": {}
                    }

                    embed = await logs.return_embed(dict_, color=0xffffff)
                    message = await ctx.send(embed=embed)
                    toDeleteMessages.append(message)
                    message = await self.bot.wait_for('message', timeout=120.0, check=checkMessage)
                    toDeleteMessages.append(message)

                    try:
                        tmp = parser.parse(message.content)
                    except:
                        pass
                    finally:
                        dict_ = {
                            "url": "",
                            "title": "Klopt dit?",
                            "description": f"__**Nieuwe geboortedatum:**__\n{tmp.strftime('%d-%m-%y')}",
                            "author": "",
                            "items": {}
                        }

                        result = await showConfirmationScreen(dict_)

                        if result:
                            validResult = True
            
                return tmp

            async def vraagBSN():
                validResult = False
                tmp = None
                while not validResult:
                    dict_ = {
                        "url": "",
                        "title": "Er ontbreken gegevens.",
                        "description": f"Wat is de werknemer zijn/haar BSN?",
                        "author": "",
                        "items": {}
                    }

                    embed = await logs.return_embed(dict_, color=0xffffff)
                    message = await ctx.send(embed=embed)
                    toDeleteMessages.append(message)
                    message = await self.bot.wait_for('message', timeout=120.0, check=checkMessage)
                    toDeleteMessages.append(message)
                    tmp = message.content

                    dict_ = {
                        "url": "",
                        "title": "Klopt dit?",
                        "description": f"__**Nieuwe BSN:**__\n{tmp}",
                        "author": "",
                        "items": {}
                    }

                    result = await showConfirmationScreen(dict_)

                    if result:
                        validResult = True

                return tmp            

            NieuweWerknemer = {}
            async def toonHuidigMenu(metConfirm = False):
                def returnCross(value):
                    if value == None or value == 0:
                        return ":x:"
                    elif value == 1:
                        return ":white_check_mark:"
                    else:
                        return value

                if isinstance(NieuweWerknemer, dict):
                    tmpNieuweWerknemer = NieuweWerknemer
                elif isinstance(NieuweWerknemer, Employee):
                    tmpNieuweWerknemer = {
                        "stadscode": NieuweWerknemer.fivemID,
                        "gemeenteapp": NieuweWerknemer.discordID,
                        "voornaam": NieuweWerknemer.fname,
                        "achternaam": NieuweWerknemer.lname,
                        "geboortedatum": NieuweWerknemer.dob,
                        "bsn": NieuweWerknemer.bsn,
                        "wachtwoord": NieuweWerknemer.pwd
                    }

                tmpdiscord = None
                print(await cogs.functions.returnMember(ctx, str(tmpNieuweWerknemer["gemeenteapp"])))
                try:
                    
                    tmpdiscord = await cogs.functions.returnMember(ctx, str(tmpNieuweWerknemer["gemeenteapp"]))
                    tmpdiscord = tmpdiscord.mention
                except:
                    tmpdiscord = ":x:"
        
                dict_ = {
                    "url": "",
                    "title": "Dit zijn de huidige gegevens van de werknemer:",
                    "description": f"""
                    __**Stadscode:**__
                    {tmpNieuweWerknemer["stadscode"]}\n
                    __**Gemeenteapp:**__
                    {tmpdiscord}\n
                    __**Voornaam:**__
                    {tmpNieuweWerknemer["voornaam"]}\n
                    __**Achternaam:**__
                    {tmpNieuweWerknemer["achternaam"]}\n
                    __**Geboortedatum:**__
                    {tmpNieuweWerknemer["geboortedatum"].strftime('%d-%m-%y')}\n
                    __**BSN:**__
                    {tmpNieuweWerknemer["bsn"]}\n
                    __**Wachtwoord:**__
                    ||Dat is uiteraard geheim.||""",
                    "author": "",
                    "items": {}
                }
            
                if metConfirm:
                    result = await showConfirmationScreen(dict_)

                    if not result:
                        dict_ = {
                            "url": "",
                            "title": "Welk gegeven wil je aanpassen?:",
                            "description": f"stadscode\ngemeenteapp\nvoornaam\nachternaam\ngeboortedatum\nbsn",
                            "author": "",
                            "items": {}
                        }

                        embed = await logs.return_embed(dict_, color=0xffffff)
                        message = await ctx.send(embed=embed)
                        toDeleteMessages.append(message)

                        message = await self.bot.wait_for('message', timeout=120.0, check=checkMessage)
                        toDeleteMessages.append(message)
                        tmp = message.content

                        if tmp == "stadscode":
                            tmpNieuweWerknemer["stadscode"] = await vraagFivem()
                        elif tmp == "gemeenteapp":
                            tmpNieuweWerknemer["gemeenteapp"] = await vraagDiscord()
                        elif tmp == "voornaam":
                            tmpNieuweWerknemer["voornaam"] = await vraagVoornaam()
                        elif tmp == "achternaam":
                            tmpNieuweWerknemer["achternaam"] = await vraagAchternaam()
                        elif tmp == "geboortedatum":
                            tmpNieuweWerknemer["geboortedatum"] = await vraagDob()
                        elif tmp == "bsn":
                            tmpNieuweWerknemer["bsn"] = await vraagBSN()
                else:
                    embed = await logs.return_embed(dict_, color=0xffffff)
                    message = await ctx.send(embed=embed)
                    toDeleteMessages.append(message)

                #if isinstance(HuidigeKlant, dict):
                    #tmpHuidigeKlant = HuidigeKlant
                if isinstance(NieuweWerknemer, Employee):
                    NieuweWerknemer.discordID = tmpNieuweWerknemer["gemeenteapp"]
                    NieuweWerknemer.fivemID = tmpNieuweWerknemer["stadscode"]
                    NieuweWerknemer.fname = tmpNieuweWerknemer["voornaam"]
                    NieuweWerknemer.lname = tmpNieuweWerknemer["achternaam"]
                    NieuweWerknemer.dob = tmpNieuweWerknemer["geboortedatum"]
                    NieuweWerknemer.bsn = tmpNieuweWerknemer["bsn"]

            HuidigeWerknemer = None
            try:
                HuidigeWerknemer = getEmployee(ctx.author.id)
            except:
                dict_ = {
                    "url": "",
                    "title": "Daar ging iets mis",
                    "description": f"Je bent of geen werknemer of er ging iets mis langs onze kant.",
                    "author": "",
                    "items": {}
                }

                embed = await logs.return_embed(dict_, color=0xffffff)
                message = await ctx.send(embed=embed)
                toDeleteMessages.append(message)
            
            # Als "nieuw", "new", "maak", "add", "toevoegen"
            if commandtype == "add" or commandtype == "new" or commandtype == "nieuw" or commandtype == "toevoegen" or commandtype == "maak":                
                NieuweWerknemer = {
                    "id": None,
                    "stadscode": await vraagFivem(),
                    "gemeenteapp": await vraagDiscord(),
                    "voornaam": await vraagVoornaam(),
                    "achternaam": await vraagAchternaam(),
                    "geboortedatum": await vraagDob(),
                    "bsn": await vraagBSN()
                }

                await toonHuidigMenu(True)

                sql = "SELECT * FROM `tbl_agents` WHERE `discordID` LIKE %s;"            
                mycursor.execute(sql, (NieuweWerknemer["gemeenteapp"],))
                myresult = mycursor.fetchone()

                if not myresult:
                    NieuweWerknemer = Employee(
                        id=NieuweWerknemer["id"],
                        fivemID=NieuweWerknemer["stadscode"],
                        discordID=NieuweWerknemer["gemeenteapp"],
                        bsn=NieuweWerknemer["bsn"],
                        fname=NieuweWerknemer["voornaam"],
                        lname=NieuweWerknemer["achternaam"],
                        pwd=None,
                        dob=NieuweWerknemer["geboortedatum"],
                        enabled=1
                    )

                    sql = """INSERT INTO `tbl_agents`(
                    `id`, 
                    `fivemID`, 
                    `discordID`, 
                    `bsn`,
                    `fname`,
                    `lname`,
                    `pwd`,
                    `dob`,
                    `enabled`) 
                    VALUES
                    (
                        NULL,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        NULL,
                        %s,
                        1
                    );"""           
                    tmpbsn = NieuweWerknemer.bsn
                    mycursor.execute(sql, (
                        NieuweWerknemer.fivemID,
                        NieuweWerknemer.discordID,                    
                        tmpbsn[2:],
                        NieuweWerknemer.fname,
                        NieuweWerknemer.lname,
                        NieuweWerknemer.dob
                    ))

                    mydb.commit()

                    await ctx.send("Werknemer werd toegevoegd.", delete_after=30)

                    sql = """INSERT INTO `tbl_sales`(
                        `id`,
                        `agentID`,
                        `amount`,
                        `reason`,
                        `timestamp`
                    ) VALUES (NULL, %s, %s, %s, %s);"""

                    mycursor.execute(sql, (
                        HuidigeWerknemer.id,
                        500,
                        "Werknemer aangeworven.",
                        datetime.datetime.today().timestamp()
                    ))

                    mydb.commit()
                else:
                    dict_ = {
                        "url": "",
                        "title": "Daar ging iets mis",
                        "description": f"De werknemer bestaat al. Pas deze aan met **!wernemer bewerk**.",
                        "author": "",
                        "items": {}
                    }

                    embed = await logs.return_embed(dict_, color=0xffffff)
                    message = await ctx.send(embed=embed)
                    toDeleteMessages.append(message)   

            elif commandtype == "edit" or commandtype == "bewerk" or commandtype == "pasaan" or commandtype == "aanpassen" or commandtype == "verander":                
                HuidigeWerknemer = getEmployee(ctx.author.id)
                NieuweWerknemer = getEmployee(await vraagDiscord())

                await toonHuidigMenu(True)

                sql = """UPDATE `tbl_clients`
                    SET `fivemID` = %s,
                    SET `discordID` = %s, 
                    SET `fname` = %s, 
                    SET `lname` = %s, 
                    SET `adres` = %s, 
                    SET `dob` = %s, 
                    SET `bsn` = %s, 
                    SET `phone` = %s, 
                    SET `crosses` = %s, 
                    SET `licenseA` = %s, 
                    SET `licenseB` = %s, 
                    SET `licenseC` = %s, 
                    SET `licenseFlight` = %s, 
                    SET `licenseBoat` = %s
                    WHERE `id` = %s;"""

                mycursor.execute(sql, (
                    NieuweWerknemer.fivemID,
                    NieuweWerknemer.discordID,
                    NieuweWerknemer.fname,
                    NieuweWerknemer.lname,
                    NieuweWerknemer.adres,
                    NieuweWerknemer.dob,
                    NieuweWerknemer.bsn[2:len(NieuweWerknemer)],
                    NieuweWerknemer.phone,
                    NieuweWerknemer.crosses,
                    NieuweWerknemer.licenseA,
                    NieuweWerknemer.licenseB,
                    NieuweWerknemer.licenseC,
                    NieuweWerknemer.licenseFlight,
                    NieuweWerknemer.licenseBoat,
                    NieuweWerknemer.id
                ))

                mydb.commit()

                await ctx.send("Werknemer werd aangepast.", delete_after=30)            

            # Als "zie", "bekijk", "see"
            elif commandtype == "zie" or commandtype == "bekijk" or commandtype == "see":
                NieuweWerknemer = getEmployee(await vraagDiscord())

                await toonHuidigMenu()

async def setup(bot):
    await bot.add_cog(Employees(bot))