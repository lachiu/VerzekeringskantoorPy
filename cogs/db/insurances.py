import os
import yaml
import logs
import json
import random
import asyncio
import general
import discord
import datetime
import settings
import cogs.functions
import mysql.connector
from copy import copy
from mimetypes import init
from discord.ext import commands
from dateutil.parser import parse
from general_bot import bot_speaks
from dotenv.main import load_dotenv

from classes.insurance import Insurance
from classes.client import Client
from classes.employee import Employee
from classes.staticclasses import InsurableType, InsuranceType, Category, SubCategory

class Insurances(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def verzekering(self, ctx, commandtype: str, *, args = None):
        load_dotenv()
        mydb = mysql.connector.connect(
            host=os.getenv('DB_SERVERNAME'),
            user=os.getenv('DB_USERNAME'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME')
        )
        
        def checkReaction(reaction, user):
            return user == ctx.author and reaction.message.channel == ctx.channel

        def checkMessage(m):
            return m.channel == ctx.channel and m.author == ctx.author

        def getInsuranceTypes(type, identifierone, identifiertwo = None):
            # Insurance Type ophalen
            mycursor = mydb.cursor()
            if cogs.functions.checkValue("isNumber", type) and type == 1:
                sql = "SELECT * FROM `tbl_insurance_types` WHERE `id` LIKE '%s';"
                mycursor.execute(sql, (identifierone,))

            elif cogs.functions.checkValue("isNumber", type) and type == 2:
                sql = "SELECT * FROM `tbl_insurance_types` WHERE `categoryID` = '%s' AND `insurable_typeID` = '%s';"                
                mycursor.execute(sql, (identifierone, identifiertwo))
            
            return mycursor.fetchall()

        def getInsurableTypes(insurableID):
            # Insurable Type ophalen
            sql = "SELECT * FROM `tbl_insurable_types` WHERE `id` LIKE '%s';"
            mycursor = mydb.cursor()
            mycursor.execute(sql, (insurableID,))
            return mycursor.fetchall()
            
        def getCategories(categoryID):
            # Category ophalen
            sql = "SELECT * FROM `tbl_categories` WHERE `id` LIKE '%s';"
            mycursor = mydb.cursor()
            mycursor.execute(sql, (categoryID,))
            return mycursor.fetchall()

        def getSubCategories(subcategoryID):
            # Subcategory ophalen
            sql = "SELECT * FROM `tbl_sub_categories` WHERE `id` LIKE '%s';"
            mycursor = mydb.cursor()
            mycursor.execute(sql, (subcategoryID,))
            return mycursor.fetchall()

        def getClient(discordID):
            # Klantgegevens ophalen
            sql = "SELECT * FROM `tbl_clients` WHERE `discordID` LIKE '%s';"
            mycursor = mydb.cursor()
            mycursor.execute(sql, (int(discordID),))
            return mycursor.fetchall()

        def getEmployee(discordID):
            # Werknemer gegevens ophalen
            sql = "SELECT * FROM `tbl_agents` WHERE `discordID` LIKE '%s';"
            mycursor = mydb.cursor()
            mycursor.execute(sql, (int(discordID),))
            return mycursor.fetchall()

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
            list = ['✅', '❌']
            await cogs.functions.addReactions(message, list)
            reaction = await self.bot.wait_for('reaction_add', timeout=120.0, check=checkReaction)

            if str(reaction[0].emoji) == '✅':
                result = True

            return result

        # We verwachten
        # !verzekering
        # !verzekering nieuw discordtarget typeverzekering duur
        # !verzekering edit discordtarget polisnummer
        # !verzekering zie discordtarget
        
        HuidigeKlant = None
        HuidigeWerknemer = None

        # Check perms
        if general.check_perms('basic', ctx.author):            
            if args:
                args = args.split()
            
            # Werknemergegevens ophalen            
            gotEmployee = False
            while not gotEmployee:
                # Proberen
                try:                    
                    myresult = getEmployee(ctx.author.id)

                    HuidigeWerknemer = Employee(
                        myresult[0][0],
                        myresult[0][1],
                        myresult[0][2],
                        myresult[0][3],
                        myresult[0][4],
                        myresult[0][5],
                        myresult[0][6],
                        myresult[0][7]
                    )
                    
                # Er ging iets mis
                except:
                    pass

                # Alles ging goed
                else:
                    gotEmployee = True
            
            discordTarget = None
            gotClient = False
            while not gotClient:
                try:
                    discordTarget = await cogs.functions.returnMember(ctx, args[0] if args else None)

                except:
                    dict_ = {
                        "url": "",
                        "title": "Er ging iets mis!",
                        "description": f"{ctx.author.mention}, probeer nog eens om de klant te taggen of de discord id door te geven.",
                        "author": "",
                        "items": {}
                    }

                    await logs.make_embed(self, ctx, dict_, 0xffffff)

                    try:
                        message = await self.bot.wait_for('message', timeout=120.0, check=checkMessage)
                        discordTarget = await cogs.functions.returnMember(ctx, message.content)

                    except TimeoutError:
                        pass

                    else:
                        gotClient = True

                else:
                    gotClient = True

            myresult = getClient(discordTarget.id)
            
            HuidigeKlant = Client(
                myresult[0][0],
                myresult[0][1],
                myresult[0][2],
                myresult[0][3],
                myresult[0][4],
                myresult[0][5],
                myresult[0][6],
                myresult[0][7],
                myresult[0][8],
                myresult[0][9],
                myresult[0][10],
                myresult[0][11]
            )

            # Check commandtype
            # Als "nieuw", "new", "maak", "add", "toevoegen"
            if commandtype == "add" or commandtype == "new" or commandtype == "nieuw" or commandtype == "toevoegen" or commandtype == "maak":
                # Wat hebben we nodig?
                policy_nr = None
                agent = HuidigeWerknemer
                client = HuidigeKlant
                insured = None
                insurance_type = None
                insurance_typeID = None
                multiplier = None
                amount_paid = None
                startDate = datetime.datetime.today()                
                HuidigeInsuranceType = None
                HuidigeInsurableType = None
                HuidigeCategory = None
                HuidigeSubCategory = None
                licensePlate = None
                # Check of args zijn ingevuld
                # typeverzekering = 1
                # duur = 2

                if args and len(args) >= 2 and cogs.functions.checkValue("isNumber", int(args[1])):
                    NieuweVerzekering.insurance_typeID = args[1]                                     
                    
                    myresult = getInsuranceTypes(1, NieuweVerzekering.insurance_typeID)
                    HuidigeInsuranceType = InsuranceType(myresult[0][0], myresult[0][1], myresult[0][2], myresult[0][3], myresult[0][4], myresult[0][5])
                    
                    myresult = getInsurableTypes(HuidigeInsuranceType.insurable_typeID)
                    HuidigeInsurableType = InsurableType(myresult[0][0], myresult[0][1], myresult[0][2], myresult[0][3])
                    
                    myresult = getCategories(HuidigeInsuranceType.categoryID)
                    HuidigeCategory = Category(myresult[0][0], myresult[0][1], myresult[0][2])
                    
                    myresult = getSubCategories(HuidigeInsurableType.subcategoryID)
                    HuidigeSubCategory = SubCategory(myresult[0][0], myresult[0][1], myresult[0][2])
                else:
                    # We weten wie de klant is
                    # We weten wie de werknemer is
                    validValue = False
                    while not validValue:
                        dict_ = {
                            "url": "",
                            "title": "Ik mis nog wat gegevens",
                            "description": f"Wat voor soort verzekering wilt u verkopen?\
                                \n\n__**Persoonlijke Verzekering**__\
                                \nU klikt op de emote :one: of antwoordt met pv of persoon.\
                                \n\
                                \n__**Voertuigverzekering**__\
                                \nU klikt op de emote :two: of antwoordt met vv of vervoer.",
                            "author": "",
                            "items": {}
                        }

                        embed = await logs.return_embed(dict_, color=0xffffff)
                        message = await ctx.send(embed=embed)
                        list = ['1️⃣', '2️⃣', '❌']
                        await cogs.functions.addReactions(message, list)

                        done, pending = await asyncio.wait([
                            self.bot.loop.create_task(self.bot.wait_for('message', timeout=120.0, check=checkMessage)),
                            self.bot.loop.create_task(self.bot.wait_for('reaction_add', timeout=120.0, check=checkReaction))
                        ], return_when=asyncio.FIRST_COMPLETED)
                        
                        try:
                            stuff = done.pop().result()

                            if isinstance(stuff, tuple):
                                if str(stuff[0].emoji) == '1️⃣':
                                    myresult = getSubCategories(1)
                                    HuidigeSubCategory = SubCategory(myresult[0][0], myresult[0][1], myresult[0][2])                                    
                                    
                                elif str(stuff[0].emoji) == '2️⃣':
                                    myresult = getSubCategories(2)
                                    HuidigeSubCategory = SubCategory(myresult[0][0], myresult[0][1], myresult[0][2])                                    

                                elif str(stuff[0].emoji) == '❌':                                    
                                    break

                            elif isinstance(stuff, discord.Message):
                                if stuff.content.lower() == "pv" or stuff.content.lower() == "persoon":
                                    myresult = getSubCategories(1)
                                    HuidigeSubCategory = SubCategory(myresult[0][0], myresult[0][1], myresult[0][2])                                    
                            
                                elif stuff.content.lower() == "vv" or stuff.content.lower() == "vervoer":
                                    myresult = getSubCategories(2)
                                    HuidigeSubCategory = SubCategory(myresult[0][0], myresult[0][1], myresult[0][2])                                    

                            dict_ = {
                                "url": "",
                                "title": "Kloppen deze gegevens?",
                                "description": f"U koos voor:\
                                    \n\n__**{HuidigeSubCategory.name}**__\
                                    \n\nKlopt dit?",
                                "author": "",
                                "items": {}
                            }
                            result = await showConfirmationScreen(dict_)

                            if result:
                                validValue = True

                        except TimeoutError:
                            pass
                
                # Dynamisch nog op te halen
                choices = {
                    1: [1, 2, 5],
                    2: [1, 3, 4]
                }

                choiceslist = choices[HuidigeSubCategory.id]
                listcategoryclasses = []

                for item in choiceslist:
                    myresult = getCategories(item)
                    listcategoryclasses.append(Category(myresult[0][0], myresult[0][1], myresult[0][2]))

                validValue = False
                while not validValue:
                    dict_ = {
                        "url": "",
                        "title": "Ik mis nog wat gegevens",
                        "description": f"Om welke categorie gaat het?\
                            \nReageer met de korte of lange naam.\n",
                        "author": "",
                        "items": {}
                    }

                    index = 0
                    for item in listcategoryclasses:
                        dict_["description"] += f"\n{index + 1} - {item.name} - {item.short_name}"
                        index += 1

                    embed = await logs.return_embed(dict_, color=0xffffff)
                    message = await ctx.send(embed=embed)
                    list = ['1️⃣', '2️⃣', '3️⃣', '❌']
                    await cogs.functions.addReactions(message, list)
                    done, pending = await asyncio.wait([
                        self.bot.loop.create_task(self.bot.wait_for('message', timeout=120.0, check=checkMessage)),
                        self.bot.loop.create_task(self.bot.wait_for('reaction_add', timeout=120.0, check=checkReaction))
                    ], return_when=asyncio.FIRST_COMPLETED)
                    
                    try:
                        stuff = done.pop().result()
                        index = 0
                        dbindex = None
                        if isinstance(stuff, tuple):
                            if str(stuff[0].emoji) == '1️⃣':
                                index = 0

                            elif str(stuff[0].emoji) == '2️⃣':
                                index = 1

                            elif str(stuff[0].emoji) == '3️⃣':
                                index = 2

                            elif str(stuff[0].emoji) == '❌':                                    
                                break
                            
                            dbindex = listcategoryclasses[index].id
                        elif isinstance(stuff, discord.Message):
                            tmp = 0
                            for item in listcategoryclasses:
                                if stuff.content.lower() == item.short_name.lower() or stuff.content.lower() == item.name.lower():
                                    dbindex = item.id
                                    index = tmp

                                tmp += 1
                        
                        dict_ = {
                            "url": "",
                            "title": "Kloppen deze gegevens?",
                            "description": f"U koos voor:\
                                \n\n__**{listcategoryclasses[index].name}**__\
                                \n\nKlopt dit?",
                            "author": "",
                            "items": {}
                        }
                        result = await showConfirmationScreen(dict_)

                        if result:
                            validValue = True
                            HuidigeCategory = listcategoryclasses[index]

                    except TimeoutError:
                        pass
                
                # Kenteken opvragen
                if HuidigeSubCategory.short_name.lower() == "vv":
                    validValue = False
                    while not validValue:
                        dict_ = {
                            "url": "",
                            "title": "Ik mis nog wat gegevens",
                            "description": f"Wat is het kenteken?\
                                \nReageer met de korte of lange naam.\n",
                            "author": "",
                            "items": {}
                        }

                        embed = await logs.return_embed(dict_, color=0xffffff)
                        await ctx.send(embed=embed)
                        message = await self.bot.wait_for('message', timeout=120.0, check=checkMessage)
                        licensePlate = message.content

                        dict_ = {
                            "url": "",
                            "title": "Kloppen deze gegevens?",
                            "description": f"Het opgegeven kenteken:\
                                \n\n__**{licensePlate}**__\
                                \n\nKlopt dit?",
                            "author": "",
                            "items": {}
                        }
                        result = await showConfirmationScreen(dict_)
                    
                        if result:
                                validValue = True

                # Dynamisch nog op te halen
                choices = {
                    1: [1, 2, 3, 4, 5, 6, 18],
                    2: [7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]
                }
                choiceslist = choices[HuidigeSubCategory.id]
                listinsurabletypes = []

                for item in choiceslist:
                    myresult = getInsurableTypes(item)
                    listinsurabletypes.append(InsurableType(myresult[0][0], myresult[0][1], myresult[0][2], myresult[0][3]))

                validValue = False
                while not validValue:
                    dict_ = {
                        "url": "",
                        "title": "Ik mis nog wat gegevens",
                        "description": f"Om wat voor {HuidigeSubCategory.name.lower()} gaat het?\
                            \nReageer met de korte of lange naam of het getalletje vooraan.\n",
                        "author": "",
                        "items": {}
                    }

                    index = 0
                    for item in listinsurabletypes:
                        dict_["description"] += f"\n{index + 1} - {item.name} - {item.short_name}"
                        index += 1

                    embed = await logs.return_embed(dict_, color=0xffffff)
                    message = await ctx.send(embed=embed)
                    list = ['❌']
                    await cogs.functions.addReactions(message, list)
                    done, pending = await asyncio.wait([
                        self.bot.loop.create_task(self.bot.wait_for('message', timeout=120.0, check=checkMessage)),
                        self.bot.loop.create_task(self.bot.wait_for('reaction_add', timeout=120.0, check=checkReaction))
                    ], return_when=asyncio.FIRST_COMPLETED)
                    
                    try:
                        stuff = done.pop().result()
                        index = 0
                        dbindex = None
                        if isinstance(stuff, tuple):
                            if str(stuff[0].emoji) == '❌':                                    
                                break
                            
                        elif isinstance(stuff, discord.Message):
                            tmp = 0
                            for item in listinsurabletypes:
                                print(cogs.functions.checkValue("isNumber", stuff.content))
                                if cogs.functions.checkValue("isNumber", stuff.content) and int(stuff.content) == item.id:
                                    dbindex = item.id
                                    index = tmp

                                elif stuff.content.lower() == item.short_name.lower() or stuff.content.lower() == item.name.lower():
                                    dbindex = item.id
                                    index = tmp

                                tmp += 1

                        dict_ = {
                            "url": "",
                            "title": "Kloppen deze gegevens?",
                            "description": f"U koos voor:\
                                \n\n__**{listinsurabletypes[index].name}**__\
                                \n\nKlopt dit?",
                            "author": "",
                            "items": {}
                        }
                        result = await showConfirmationScreen(dict_)

                        if result:
                            validValue = True
                            HuidigeInsurableType = listinsurabletypes[index]

                    except TimeoutError:
                        pass

                timedelta = None
                timespan = None
                length = None
                timedeltauitleg = None

                if args and len(args) >= 3:
                    timespan = args[2][-1]
                    length = args[2][:-1]

                    if timespan == "w" or timespan == "d" or timespan == "m":
                        if timespan == "w":
                            timedelta = f"weeks"

                            if length == 1:
                                timedeltauitleg = f"{length} week"
                            else:
                                timedeltauitleg = f"{length} weken"

                        elif timespan == "d":
                            timedelta = f"days"
                            
                            if length == 1:
                                timedeltauitleg = f"{length} dag"
                            else:
                                timedeltauitleg = f"{length} dagen"

                        elif timespan == "m":
                            timedelta = f"months"

                            if length == 1:
                                timedeltauitleg = f"{length} maand"
                            else:
                                timedeltauitleg = f"{length} maanden"

                validValue = False
                if not validValue:
                    result = None
                    if timedelta:
                        dict_ = {
                            "url": "",
                            "title": "Kloppen deze gegevens?",
                            "description": f"U koos voor:\
                                \n\n__**{timedelta}**__\
                                \n\nKlopt dit?",
                            "author": "",
                            "items": {}
                        }

                        result = await showConfirmationScreen(dict_)
                    else:
                        dict_ = {
                            "url": "",
                            "title": "Ik mis nog wat gegevens",
                            "description": f"Hoelang moet deze nieuwe verzekering duren?\
                                \nReageer met een getal en dan een eenheid.\
                                \n\
                                \n7d (7 dagen)\
                                \n4w (4 weken)\
                                \n1m (1 maand)",
                            "author": "",
                            "items": {}
                        }

                        embed = await logs.return_embed(dict_, color=0xffffff)
                        message = await ctx.send(embed=embed)
                        reaction = await self.bot.wait_for('message', timeout=120.0, check=checkMessage)                        
                        timespan = reaction.content[-1]
                        length = reaction.content[:-1]

                        if timespan == "w" or timespan == "d" or timespan == "m" and cogs.functions.checkValue("isNumber", length):                            
                            if timespan == "w":
                                timedelta = f"weeks"

                                if length == 1:
                                    timedeltauitleg = f"{length} week"
                                else:
                                    timedeltauitleg = f"{length} weken"

                            elif timespan == "d":
                                timedelta = f"days"
                                
                                if length == 1:
                                    timedeltauitleg = f"{length} dag"
                                else:
                                    timedeltauitleg = f"{length} dagen"

                            elif timespan == "m":
                                timedelta = f"months"

                                if length == 1:
                                    timedeltauitleg = f"{length} maand"
                                else:
                                    timedeltauitleg = f"{length} maanden"

                            dict_ = {
                                "url": "",
                                "title": "Kloppen deze gegevens?",
                                "description": f"U koos voor:\
                                    \n\n__**{timedeltauitleg}**__\
                                    \n\nKlopt dit?",
                                "author": "",
                                "items": {}
                            }

                            result = await showConfirmationScreen(dict_)

                    if result:
                        validValue = True

                myresult = getInsuranceTypes(2, HuidigeCategory.id, HuidigeInsurableType.id)
                HuidigeInsuranceType = InsuranceType(myresult[0][0], myresult[0][1], myresult[0][2], myresult[0][3], myresult[0][4], myresult[0][5])
                timediff = None
                
                if timedelta == "days":
                    timediff = datetime.timedelta(days=int(length))

                elif timedelta == "weeks":
                    timediff = datetime.timedelta(weeks=int(length))

                elif timedelta == "months":
                    timediff = datetime.timedelta(months=int(length))
                
                endDate = startDate + timediff

                dict_ = {
                    "url": "",
                    "title": "Ter bevestiging",
                    "description": f"Kloppen deze gegevens?\
                        \n\
                        \n__**Klant:**__\
                        \n{discordTarget.mention}\
                        \n\
                        \n__**Verkoper:**__\
                        \n{ctx.author.mention}\
                        \n\
                        \n__**Type verzekering:**__\
                        \n{HuidigeSubCategory.name}\
                        \n\
                        \n__**Verzekering's categorie:**__\
                        \n{HuidigeCategory.name}\
                        \n",
                    "author": "",
                    "items": {}
                }

                if HuidigeSubCategory.short_name.lower() == "pv":
                    dict_["description"] += f"\
                        \n__**Beroep:**__"
                        
                elif HuidigeSubCategory.short_name.lower() == "vv":
                    dict_["description"] += f"\
                        \n__**Type voertuig:**__"

                dict_["description"] += f"\
                    \n{HuidigeInsurableType.name}\n"

                if HuidigeSubCategory.short_name.lower() == "vv":
                    dict_["description"] += f"\
                        \n__**Kenteken:**__\
                        \n{licensePlate}\
                        \n"

                dict_["description"] += f"\
                    \n__**Te betalen:**__\
                    \n{HuidigeInsuranceType.price}\
                    \n\
                    \n__**Bonusmalus:**__\
                    \n{HuidigeInsuranceType.default_mp}\
                    \n\
                    \n__**Minimum bonusmalus:**__\
                    \n{HuidigeInsuranceType.min_tmp}\
                    \n\
                    \n__**Startdatum:**__\
                    \n{startDate.strftime('%d-%m-%y')}\
                    \n\
                    \n__**Einddatum:**__\
                    \n{endDate.strftime('%d-%m-%y')}"

                result = await showConfirmationScreen(dict_)

                if result:
                    NieuweVerzekering = Insurance(self.bot, agent.discordID, client.discordID, insured, insurance_typeID, multiplier, amount_paid, startDate, endDate)
                else:
                    # Werd geklikt op het kruisje of timeout, dan zeggen we gewoon dat ie opnieuw mag.
                    pass

            # Als "edit", "bewerk", "pasaan", "aanpassen", "verander"
            elif commandtype == "edit" or commandtype == "bewerk" or commandtype == "pasaan" or commandtype == "aanpassen" or commandtype == "verander":
                # Check of args zijn ingevuld
                pass

            # Als "zie", "bekijk", "see"
            elif commandtype == "zie" or commandtype == "bekijk" or commandtype == "see":
                # Check of args zijn ingevuld
                pass

            # Als geen is meegegeven
            elif not commandtype:
                dict_ = {
                    "url": "",
                    "title": "De verzekering",
                    "description": f"{ctx.author.mention}, u bent vergeten een parameter mee te geven.\
                        \n\
                        \n__**!verzekering:**__\
                        \n**nieuw** (add, new, toevoegen, nieuw, maak)\
                        \n*Optionele parameters:*\
                        \nDiscord ID (tag, id of 'leeg'),\
                        \nType verzekering (nummer of 'leeg'),\
                        \nDuur (in rp)\
                        \n\
                        \n**edit** (aanpassen, pasaan, verander, bewerk, edit)\
                        \n*Optionele parameters:*\
                        \nDiscord id (tag, id of 'leeg'),\
                        \nPolisnummer (getal of 'geen')\
                        \n\
                        \n**zie** (bekijken, see, zie)\
                        \n*Optionele parameters:*\
                        \nDiscord id (tag, id of 'leeg')",
                    "author": "",
                    "items": {}
                }

                await ctx.make_embed(self, dict_, color=0xffffff)
        
async def setup(bot):
    await bot.add_cog(Insurances(bot))