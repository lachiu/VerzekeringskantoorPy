import os
import yaml
import logs
import json
import random
import general
import discord
import settings
import datetime
import mysql.connector
import cogs.functions
from dateutil import parser
from dotenv.main import load_dotenv
from discord.ext import commands
from general_bot import bot_speaks
from classes.employee import Employee
from classes.client import Client

class Clients(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def klant(self, ctx, commandtype: str, *, args = None):
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

            def getClient(discordID):
                # Klant gegevens ophalen
                sql = "SELECT * FROM `tbl_clients` WHERE `discordID` LIKE %s;"            
                mycursor.execute(sql, (int(discordID),))
                myresult = mycursor.fetchone()

                return Client(
                    id=myresult[0],
                    fivemID=myresult[1],
                    discordID=myresult[2],
                    fname=myresult[3],
                    lname=myresult[4],                    
                    adres=myresult[5],
                    dob=myresult[6],                   
                    bsn=myresult[7],
                    phone=myresult[8],
                    crosses=myresult[9],
                    licenseA=myresult[10],
                    licenseB=myresult[11],
                    licenseC=myresult[12],
                    licenseFlight=myresult[13],
                    licenseBoat=myresult[14]
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
                        "description": f"Wat is de klant zijn/haar stadscode?",
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
                        "description": f"Wat is de klant zijn/haar gemeenteapp?",
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
                        "description": f"Wat is de klant zijn/haar voornaam?",
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
                        "description": f"Wat is de klant zijn/haar achternaam?",
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

            async def vraagAdres():
                validResult = False
                tmp = None
                while not validResult:
                    dict_ = {
                        "url": "",
                        "title": "Er ontbreken gegevens.",
                        "description": f"Wat is de klant zijn/haar adres?",
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
                        "description": f"__**Nieuwe adres:**__\n{tmp}",
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
                        "description": f"Wat is de klant zijn/haar geboortedatum?",
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
                        "description": f"Wat is de klant zijn/haar BSN?",
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

            async def vraagPhone():
                validResult = False
                tmp = None
                while not validResult:
                    dict_ = {
                        "url": "",
                        "title": "Er ontbreken gegevens.",
                        "description": f"Wat is de klant zijn/haar telefoonnummer?",
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
                        "description": f"__**Nieuwe telefoonnummer:**__\n{tmp}",
                        "author": "",
                        "items": {}
                    }

                    result = await showConfirmationScreen(dict_)

                    if result:
                        validResult = True

                return tmp

            async def vraagKruisjes():
                validResult = False
                tmp = None
                while not validResult:
                    dict_ = {
                        "url": "",
                        "title": "Er ontbreken gegevens.",
                        "description": f"Hoeveel kruisjes heeft deze klant?",
                        "author": "",
                        "items": {}
                    }

                    embed = await logs.return_embed(dict_, color=0xffffff)
                    message = await ctx.send(embed=embed)
                    toDeleteMessages.append(message)
                    list = ['1️⃣', '2️⃣', '3️⃣']
                    await cogs.functions.addReactions(message, list)

                    reaction = await self.bot.wait_for('reaction_add', timeout=120.0, check=checkReaction)
                    
                    if str(reaction[0].emoji) == '1️⃣':
                        tmp = 1
                    elif str(reaction[0].emoji) == '2️⃣':
                        tmp = 2
                    elif str(reaction[0].emoji) == '3️⃣':
                        tmp = 3

                    dict_ = {
                        "url": "",
                        "title": "Klopt dit?",
                        "description": f"__**Aantal kruisjes:**__\n{tmp}",
                        "author": "",
                        "items": {}
                    }

                    result = await showConfirmationScreen(dict_)

                    if result:
                        validResult = True

                return tmp

            async def vraagRijbewijsA():
                validResult = False
                tmp = None
                while not validResult:
                    dict_ = {
                        "url": "",
                        "title": "Er ontbreken gegevens.",
                        "description": f"Heeft de klant een rijbewijs cat. A?",
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
                        tmp = 1
                    elif str(reaction[0].emoji) == '❌':
                        tmp = 0                    

                    dict_ = {
                        "url": "",
                        "title": "Klopt dit?",
                        "description": f"__**Heeft rijbewijs cat. A:**__\n{str(reaction[0].emoji)}",
                        "author": "",
                        "items": {}
                    }

                    result = await showConfirmationScreen(dict_)

                    if result:
                        validResult = True

                return tmp

            async def vraagRijbewijsB():
                validResult = False
                tmp = None
                while not validResult:
                    dict_ = {
                        "url": "",
                        "title": "Er ontbreken gegevens.",
                        "description": f"Heeft de klant een rijbewijs cat. B?",
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
                        tmp = 1
                    elif str(reaction[0].emoji) == '❌':
                        tmp = 0                    

                    dict_ = {
                        "url": "",
                        "title": "Klopt dit?",
                        "description": f"__**Heeft rijbewijs cat. B:**__\n{str(reaction[0].emoji)}",
                        "author": "",
                        "items": {}
                    }

                    result = await showConfirmationScreen(dict_)

                    if result:
                        validResult = True

                return tmp

            async def vraagRijbewijsC():
                validResult = False
                tmp = None
                while not validResult:
                    dict_ = {
                        "url": "",
                        "title": "Er ontbreken gegevens.",
                        "description": f"Heeft de klant een rijbewijs cat. C?",
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
                        tmp = 1
                    elif str(reaction[0].emoji) == '❌':
                        tmp = 0                    

                    dict_ = {
                        "url": "",
                        "title": "Klopt dit?",
                        "description": f"__**Heeft rijbewijs cat. C:**__\n{str(reaction[0].emoji)}",
                        "author": "",
                        "items": {}
                    }

                    result = await showConfirmationScreen(dict_)

                    if result:
                        validResult = True

                return tmp

            async def vraagVliegbrevet():
                validResult = False
                tmp = None
                while not validResult:
                    dict_ = {
                        "url": "",
                        "title": "Er ontbreken gegevens.",
                        "description": f"Heeft de klant een vliegbrevet?",
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
                        tmp = 1
                    elif str(reaction[0].emoji) == '❌':
                        tmp = 0                    

                    dict_ = {
                        "url": "",
                        "title": "Klopt dit?",
                        "description": f"__**Heeft vliegbrevet:**__\n{str(reaction[0].emoji)}",
                        "author": "",
                        "items": {}
                    }

                    result = await showConfirmationScreen(dict_)

                    if result:
                        validResult = True

                return tmp

            async def vraagVaarbrevet():
                validResult = False
                tmp = None
                while not validResult:
                    dict_ = {
                        "url": "",
                        "title": "Er ontbreken gegevens.",
                        "description": f"Heeft de klant een vaarbrevet?",
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
                        tmp = 1
                    elif str(reaction[0].emoji) == '❌':
                        tmp = 0                    

                    dict_ = {
                        "url": "",
                        "title": "Klopt dit?",
                        "description": f"__**Heeft vaarbrevet:**__\n{str(reaction[0].emoji)}",
                        "author": "",
                        "items": {}
                    }

                    result = await showConfirmationScreen(dict_)

                    if result:
                        validResult = True

                return tmp

            HuidigeKlant = {}
            async def toonHuidigMenu(metConfirm = False):
                def returnCross(value):
                    if value == None or value == 0:
                        return ":x:"
                    elif value == 1:
                        return ":white_check_mark:"
                    else:
                        return value

                def kruisjesbl(value):
                    tmpvalue = ""

                    if value > 0:
                        while value > 0:
                            tmpvalue += ":x: "
                            value -= 1
                    else:
                        tmpvalue = "Geen"

                    return tmpvalue

                if isinstance(HuidigeKlant, dict):
                    tmpHuidigeKlant = HuidigeKlant
                elif isinstance(HuidigeKlant, Client):
                    tmpHuidigeKlant = {
                        "stadscode": HuidigeKlant.fivemID,
                        "gemeenteapp": HuidigeKlant.discordID,
                        "voornaam": HuidigeKlant.fname,
                        "achternaam": HuidigeKlant.lname,
                        "adres": HuidigeKlant.adres,
                        "geboortedatum": HuidigeKlant.dob,
                        "bsn": HuidigeKlant.bsn,
                        "telefoonnummer": HuidigeKlant.phone,
                        "kruisjes": HuidigeKlant.crosses,
                        "rijbewijs a": HuidigeKlant.licenseA,
                        "rijbewijs b": HuidigeKlant.licenseB,
                        "rijbewijs c": HuidigeKlant.licenseC,
                        "vliegbrevet": HuidigeKlant.licenseFlight,
                        "vaarbrevet": HuidigeKlant.licenseBoat 
                    }

                tmpdiscord = None
                try:
                    tmpdiscord = await cogs.functions.returnMember(ctx, str(tmpHuidigeKlant["gemeenteapp"]))
                    tmpdiscord = tmpdiscord.mention
                except:
                    tmpdiscord = returnCross(tmpdiscord)                

                dict_ = {
                    "url": "",
                    "title": "Dit zijn de huidige klantgegevens:",
                    "description": f"""
                    __**Stadscode:**__
                    {returnCross(tmpHuidigeKlant["stadscode"])}\n
                    __**Gemeenteapp:**__
                    {returnCross(tmpdiscord)}\n
                    __**Voornaam:**__
                    {tmpHuidigeKlant["voornaam"]}\n
                    __**Achternaam:**__
                    {tmpHuidigeKlant["achternaam"]}\n
                    __**Adres:**__
                    {tmpHuidigeKlant["adres"]}\n
                    __**Geboortedatum:**__
                    {tmpHuidigeKlant["geboortedatum"].strftime('%d-%m-%y')}\n
                    __**BSN:**__
                    {tmpHuidigeKlant["bsn"]}\n
                    __**Telefoonnummer:**__
                    {tmpHuidigeKlant["telefoonnummer"]}\n
                    __**Kruisjes:**__
                    {kruisjesbl(tmpHuidigeKlant["kruisjes"])}\n
                    __**Rijbewijs cat. A:**__
                    {returnCross(tmpHuidigeKlant["rijbewijs a"])}\n
                    __**Rijbewijs cat. B:**__
                    {returnCross(tmpHuidigeKlant["rijbewijs b"])}\n
                    __**Rijbewijs cat. C:**__
                    {returnCross(tmpHuidigeKlant["rijbewijs c"])}\n
                    __**Vliegbrevet:**__
                    {returnCross(tmpHuidigeKlant["vliegbrevet"])}\n
                    __**Vaarbrevet:**__
                    {returnCross(tmpHuidigeKlant["vaarbrevet"])}""",
                    "author": "",
                    "items": {}
                }
            
                if metConfirm:
                    result = await showConfirmationScreen(dict_)

                    if not result:
                        dict_ = {
                            "url": "",
                            "title": "Welk gegeven wil je aanpassen?:",
                            "description": f"stadscode\ngemeenteapp\nvoornaam\nachternaam\nadres\ngeboortedatum\nbsn\ntelefoonnummer\nkruisjes\nrijbewijs cat. A\nrijbewijs cat. B\nrijbewijs cat. C\nvliegbrevet\nvaarbrevet",
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
                            tmpHuidigeKlant["stadscode"] = await vraagFivem()
                        elif tmp == "gemeenteapp":
                            tmpHuidigeKlant["gemeenteapp"] = await vraagDiscord()
                        elif tmp == "voornaam":
                            tmpHuidigeKlant["voornaam"] = await vraagVoornaam()
                        elif tmp == "achternaam":
                            tmpHuidigeKlant["achternaam"] = await vraagAchternaam()
                        elif tmp == "adres":
                            tmpHuidigeKlant["adres"] = await vraagAdres()
                        elif tmp == "geboortedatum":
                            tmpHuidigeKlant["geboortedatum"] = await vraagDob()
                        elif tmp == "bsn":
                            tmpHuidigeKlant["bsn"] = await vraagBSN()
                        elif tmp == "telefoonnummer":
                            tmpHuidigeKlant["telefoonnummer"] = await vraagPhone()
                        elif tmp == "kruisjes":
                            tmpHuidigeKlant["kruisjes"] = await vraagKruisjes()
                        elif tmp == "rijbewijs cat. A":
                            tmpHuidigeKlant["rijbewijs a"] = await vraagRijbewijsA()
                        elif tmp == "rijbewijs cat. B":
                            tmpHuidigeKlant["rijbewijs b"] = await vraagRijbewijsB()
                        elif tmp == "rijbewijs cat. C":
                            tmpHuidigeKlant["rijbewijs c"] = await vraagRijbewijsC()
                        elif tmp == "vliegbrevet":
                            tmpHuidigeKlant["vliegbrevet"] = await vraagVliegbrevet()
                        elif tmp == "vaarbrevet":
                            tmpHuidigeKlant["vaarbrevet"] = await vraagVaarbrevet()
                else:
                    embed = await logs.return_embed(dict_, color=0xffffff)
                    message = await ctx.send(embed=embed)
                    toDeleteMessages.append(message)

                #if isinstance(HuidigeKlant, dict):
                    #tmpHuidigeKlant = HuidigeKlant
                if isinstance(HuidigeKlant, Client):
                    HuidigeKlant.discordID = tmpHuidigeKlant["gemeenteapp"]
                    HuidigeKlant.fivemID = tmpHuidigeKlant["stadscode"]
                    HuidigeKlant.fname = tmpHuidigeKlant["voornaam"]
                    HuidigeKlant.lname = tmpHuidigeKlant["achternaam"]
                    HuidigeKlant.adres = tmpHuidigeKlant["adres"]
                    HuidigeKlant.dob = tmpHuidigeKlant["geboortedatum"]
                    HuidigeKlant.bsn = tmpHuidigeKlant["bsn"]
                    HuidigeKlant.phone = tmpHuidigeKlant["telefoonnummer"]
                    HuidigeKlant.crosses = tmpHuidigeKlant["kruisjes"]
                    HuidigeKlant.licenseA = tmpHuidigeKlant["rijbewijs a"]
                    HuidigeKlant.licenseB = tmpHuidigeKlant["rijbewijs b"]
                    HuidigeKlant.licenseC = tmpHuidigeKlant["rijbewijs c"]
                    HuidigeKlant.licenseFlight = tmpHuidigeKlant["vliegbrevet"]
                    HuidigeKlant.licenseBoat = tmpHuidigeKlant["vaarbrevet"]

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
                HuidigeKlant = {
                    "id": None,
                    "stadscode": await vraagFivem(),
                    "gemeenteapp": await vraagDiscord(),
                    "voornaam": await vraagVoornaam(),
                    "achternaam": await vraagAchternaam(),
                    "adres": await vraagAdres(),
                    "geboortedatum": await vraagDob(),
                    "bsn": await vraagBSN(),
                    "telefoonnummer": await vraagPhone(),
                    "kruisjes": 0,
                    "rijbewijs a": await vraagRijbewijsA(),
                    "rijbewijs b": await vraagRijbewijsB(),
                    "rijbewijs c": await vraagRijbewijsC(),
                    "vliegbrevet": await vraagVliegbrevet(),
                    "vaarbrevet": await vraagVaarbrevet()
                }

                await toonHuidigMenu(True)

                sql = "SELECT * FROM `tbl_clients` WHERE `discordID` LIKE %s;"            
                mycursor.execute(sql, (HuidigeKlant["gemeenteapp"],))
                myresult = mycursor.fetchone()

                if not myresult:
                    HuidigeKlant = Client(
                        id=HuidigeKlant["id"],
                        fivemID=HuidigeKlant["stadscode"],
                        discordID=HuidigeKlant["gemeenteapp"],
                        fname=HuidigeKlant["voornaam"],
                        lname=HuidigeKlant["achternaam"],
                        adres=HuidigeKlant["adres"],
                        dob=HuidigeKlant["geboortedatum"],
                        bsn=HuidigeKlant["bsn"],
                        phone=HuidigeKlant["telefoonnummer"],
                        crosses=HuidigeKlant["kruisjes"],
                        licenseA=HuidigeKlant["rijbewijs a"],
                        licenseB=HuidigeKlant["rijbewijs b"],
                        licenseC=HuidigeKlant["rijbewijs c"],
                        licenseFlight=HuidigeKlant["vliegbrevet"],
                        licenseBoat=HuidigeKlant["vaarbrevet"]
                    )

                    sql = """INSERT INTO `tbl_clients`(
                    `id`, 
                    `fivemID`, 
                    `discordID`, 
                    `fname`, 
                    `lname`, 
                    `adres`, 
                    `dob`, 
                    `bsn`, 
                    `phone`, 
                    `crosses`, 
                    `licenseA`, 
                    `licenseB`, 
                    `licenseC`, 
                    `licenseFlight`, 
                    `licenseBoat`) 
                    VALUES
                    (
                        NULL,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s
                    );"""               

                    tmpbsn = HuidigeKlant.bsn
                    mycursor.execute(sql, (
                        HuidigeKlant.fivemID,
                        HuidigeKlant.discordID,
                        HuidigeKlant.fname,
                        HuidigeKlant.lname,
                        HuidigeKlant.adres,
                        HuidigeKlant.dob,
                        tmpbsn[2:],
                        HuidigeKlant.phone,
                        HuidigeKlant.crosses,
                        HuidigeKlant.licenseA,
                        HuidigeKlant.licenseB,
                        HuidigeKlant.licenseC,
                        HuidigeKlant.licenseFlight,
                        HuidigeKlant.licenseBoat
                    ))

                    mydb.commit()

                    await ctx.send("Klant werd toegevoegd.", delete_after=30)

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
                        "Klant aangeworven.",
                        datetime.datetime.today().timestamp()
                    ))

                    mydb.commit()
                else:
                    dict_ = {
                        "url": "",
                        "title": "Daar ging iets mis",
                        "description": f"De klant bestaat al. Pas deze aan met **!klant bewerk**.",
                        "author": "",
                        "items": {}
                    }

                    embed = await logs.return_embed(dict_, color=0xffffff)
                    message = await ctx.send(embed=embed)
                    toDeleteMessages.append(message)    

            elif commandtype == "edit" or commandtype == "bewerk" or commandtype == "pasaan" or commandtype == "aanpassen" or commandtype == "verander":                
                HuidigeKlant = getClient(await vraagDiscord())

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
                    WHERE `id` = %s;                    
                """

                mycursor.execute(sql, (
                    HuidigeKlant.fivemID,
                    HuidigeKlant.discordID,
                    HuidigeKlant.fname,
                    HuidigeKlant.lname,
                    HuidigeKlant.adres,
                    HuidigeKlant.dob,
                    HuidigeKlant.bsn[2:],
                    HuidigeKlant.phone,
                    HuidigeKlant.crosses,
                    HuidigeKlant.licenseA,
                    HuidigeKlant.licenseB,
                    HuidigeKlant.licenseC,
                    HuidigeKlant.licenseFlight,
                    HuidigeKlant.licenseBoat,
                    HuidigeKlant.id
                ))

                mydb.commit()

                await ctx.send("Klant werd aangepast.", delete_after=30)            

            # Als "zie", "bekijk", "see"
            elif commandtype == "zie" or commandtype == "bekijk" or commandtype == "see":
                HuidigeKlant = getClient(await vraagDiscord())

                await toonHuidigMenu()

async def setup(bot):
    await bot.add_cog(Clients(bot))