import os
import yaml
import logs
import asyncio
import general
import discord
import datetime
import settings
import cogs.functions
import mysql.connector
from discord.ext import commands
from dateutil.parser import parse
from general_bot import bot_speaks
from dotenv.main import load_dotenv
from pdf_generation import generate_conditions_PDF, generate_invoice_PDF

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
        
        mycursor = mydb.cursor()
        toDeleteMessages = []
        vandaag = datetime.datetime.today()
        discordTarget = None        
        timedeltauitleg = None
        timespan = None
        length = None

        HuidigeVerzekering = {
            "agentID": None,
            "clientID": None,
            "insured": None,
            "insurance_typeID": 0,
            "multiplier": 0,
            "amount_paid": 0,
            "startDate": int(vandaag.timestamp()),
            "endDate": None
        }

        HuidigeInsuranceType = None

        def checkReaction(reaction, user):
            return user == ctx.author and reaction.message.channel == ctx.channel

        def checkMessage(m):
            return m.channel == ctx.channel and m.author == ctx.author

        def getInsurance(policy_nr):
            # Insurance ophalen
            sql = "SELECT * FROM `tbl_insurances` WHERE `policy_nr` LIKE %s;"
            mycursor.execute(sql, (policy_nr,))
            return mycursor.fetchone()

        def getInsuranceTypes(type, identifierone, identifiertwo = None):
            # Insurance Type ophalen
            if isinstance(type, int):
                if type == 1:
                    sql = "SELECT * FROM `tbl_insurance_types` WHERE `id` LIKE %s;"
                    mycursor.execute(sql, (identifierone,))

                elif type == 2:
                    sql = "SELECT * FROM `tbl_insurance_types` WHERE `categoryID` = %s AND `insurable_typeID` = %s;"                
                    mycursor.execute(sql, (identifierone, identifiertwo))
                
                return mycursor.fetchone()

        def getInsurableTypes(insurableID):
            # Insurable Type ophalen
            sql = "SELECT * FROM `tbl_insurable_types` WHERE `id` LIKE %s;"
            mycursor.execute(sql, (insurableID,))
            return mycursor.fetchone()
            
        def getCategories(categoryID):
            # Category ophalen
            sql = "SELECT * FROM `tbl_categories` WHERE `id` LIKE %s;"
            mycursor.execute(sql, (categoryID,))
            return mycursor.fetchone()

        def getSubCategories(subcategoryID):
            # Subcategory ophalen
            sql = "SELECT * FROM `tbl_sub_categories` WHERE `id` LIKE %s;"
            mycursor.execute(sql, (subcategoryID,))
            return mycursor.fetchone()

        def getClient(discordID):
            # Klantgegevens ophalen
            sql = "SELECT * FROM `tbl_clients` WHERE `discordID` LIKE %s;"
            mycursor.execute(sql, (int(discordID),))
            return mycursor.fetchone()

        def getEmployee(discordID):
            # Werknemer gegevens ophalen
            sql = "SELECT * FROM `tbl_agents` WHERE `discordID` LIKE %s;"
            mycursor.execute(sql, (int(discordID),))
            return mycursor.fetchone()

        async def verzamelWerknemer():
            myresult = None
            gotEmployee = False
            while not gotEmployee:
                # Proberen
                try:                    
                    myresult = getEmployee(ctx.author.id)                    
                    
                # Er ging iets mis
                except:
                    dict_ = {
                        "url": "",
                        "title": "Er ging iets mis!",
                        "description": f"{ctx.author.mention}, je bent of geen werknemer of er ging iets mis bij mij.\nProbeer later opnieuw.",
                        "author": "",
                        "items": {}
                    }

                    embed = await logs.return_embed(dict_, 0xffffff)
                    message = await ctx.send(embed=embed)
                    toDeleteMessages.append(message)

                # Alles ging goed
                else:
                    gotEmployee = True
            
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

        async def verzamelPolis():
            answer = ""
            gotInsurance = False
            while not gotInsurance:
                # Proberen
                try:                    
                    myresult = getInsurance(answer)

                    HuidigeVerzekering = Insurance(
                        id=myresult[0],
                        policy_nr=myresult[1],
                        agentID=myresult[2],
                        clientID=myresult[3],
                        insured=myresult[4],
                        insurance_typeID=myresult[5],
                        multiplier=myresult[6],
                        startDate=myresult[7],
                        endDate=myresult[8]
                    )
                    
                # Er ging iets mis
                except:
                    dict_ = {
                        "url": "",
                        "title": "Ik mis gegevens!",
                        "description": f"{ctx.author.mention}, die verzekeringspolis bestaat niet.",
                        "author": "",
                        "items": {}
                    }

                    embed = await logs.return_embed(dict_, 0xffffff)
                    message = await ctx.send(embed=embed)
                    toDeleteMessages.append(message)

                # Alles ging goed
                else:
                    gotInsurance = True

        async def verzamelKlant():
            myresult = None
            gotClient = False
            while not gotClient:
                try:
                    discordTarget = await cogs.functions.returnMember(ctx, args[0] if args else None)

                except:
                    dict_ = {
                        "url": "",
                        "title": "Er ging iets mis!",
                        "description": f"{ctx.author.mention}, probeer nog eens om de klant te taggen of de discord id door te geven.\nMogelijk heeft de klant nog geen account bij ons.",
                        "author": "",
                        "items": {}
                    }

                    embed = await logs.return_embed(dict_, 0xffffff)
                    message = await ctx.send(embed=embed)
                    toDeleteMessages.append(message)

                    try:
                        message = await self.bot.wait_for('message', timeout=120.0, check=checkMessage)
                        toDeleteMessages.append(message)
                        discordTarget = await cogs.functions.returnMember(ctx, message.content)

                    except TimeoutError:
                        pass

                    else:
                        gotClient = True

                else:
                    gotClient = True

                myresult = getClient(discordTarget.id)
            
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

        async def verzamelSubCategory():
            HuidigeSubCategory = None
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
                            HuidigeSubCategory = SubCategory(myresult[0], myresult[1], myresult[2])                                    
                            
                        elif str(stuff[0].emoji) == '2️⃣':
                            myresult = getSubCategories(2)
                            HuidigeSubCategory = SubCategory(myresult[0], myresult[1], myresult[2])                                    

                        elif str(stuff[0].emoji) == '❌':                                    
                            break

                    elif isinstance(stuff, discord.Message):
                        if stuff.content.lower() == "pv" or stuff.content.lower() == "persoon":
                            myresult = getSubCategories(1)
                            HuidigeSubCategory = SubCategory(myresult[0], myresult[1], myresult[2])                                    
                    
                        elif stuff.content.lower() == "vv" or stuff.content.lower() == "vervoer":
                            myresult = getSubCategories(2)
                            HuidigeSubCategory = SubCategory(myresult[0], myresult[1], myresult[2])                                    

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

            return HuidigeSubCategory
        
        async def verzamelCategory():
            HuidigeCategory = None
            # Dynamisch nog op te halen
            choices = {
                1: [1, 2, 5],
                2: [1, 3, 4]
            }

            choiceslist = choices[HuidigeSubCategory.id]
            listcategoryclasses = []

            for item in choiceslist:
                myresult = getCategories(item)
                listcategoryclasses.append(Category(myresult[0], myresult[1], myresult[2], myresult[3]))

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
                toDeleteMessages.append(message)
                list = ['1️⃣', '2️⃣', '3️⃣', '❌']
                await cogs.functions.addReactions(message, list)
                done, pending = await asyncio.wait([
                    self.bot.loop.create_task(self.bot.wait_for('message', timeout=120.0, check=checkMessage)),
                    self.bot.loop.create_task(self.bot.wait_for('reaction_add', timeout=120.0, check=checkReaction))
                ], return_when=asyncio.FIRST_COMPLETED)
                
                try:
                    stuff = done.pop().result()
                    index = 0

                    if isinstance(stuff, tuple):
                        if str(stuff[0].emoji) == '1️⃣':
                            index = 0

                        elif str(stuff[0].emoji) == '2️⃣':
                            index = 1

                        elif str(stuff[0].emoji) == '3️⃣':
                            index = 2

                        elif str(stuff[0].emoji) == '❌':                                    
                            break
                    
                    elif isinstance(stuff, discord.Message):
                        tmp = 0
                        for item in listcategoryclasses:
                            if stuff.content.lower() == item.short_name.lower() or stuff.content.lower() == item.name.lower():
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

            return HuidigeCategory

        async def verzamelInsurableType():
            HuidigeInsurableType = None
            # Dynamisch nog op te halen
            choices = {
                1: [1, 2, 3, 4, 5, 6, 18],
                2: [7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]
            }

            choiceslist = choices[HuidigeSubCategory.id]
            listinsurabletypes = []

            for item in choiceslist:
                myresult = getInsurableTypes(item)
                listinsurabletypes.append(InsurableType(myresult[0], myresult[1], myresult[2], myresult[3]))

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
                    if isinstance(stuff, tuple):
                        if str(stuff[0].emoji) == '❌':                                    
                            break
                        
                    elif isinstance(stuff, discord.Message):
                        tmp = 0
                        for item in listinsurabletypes:
                            if isinstance(stuff.content, int) and int(stuff.content) == item.id:
                                index = tmp

                            elif stuff.content.lower() == item.short_name.lower() or stuff.content.lower() == item.name.lower():
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

            return HuidigeInsurableType

        async def verzamelInsured():
            # Kenteken opvragen
            if HuidigeSubCategory.short_name.lower() == "vv":
                validValue = False
                while not validValue:
                    dict_ = {
                        "url": "",
                        "title": "Ik mis nog wat gegevens",
                        "description": f"Wat is het kenteken?",
                        "author": "",
                        "items": {}
                    }

                    embed = await logs.return_embed(dict_, color=0xffffff)
                    message = await ctx.send(embed=embed)
                    toDeleteMessages.append(message)
                    message = await self.bot.wait_for('message', timeout=120.0, check=checkMessage)
                    HuidigeVerzekering["insured"] = message.content

                    dict_ = {
                        "url": "",
                        "title": "Kloppen deze gegevens?",
                        "description": f"Het opgegeven kenteken:\
                            \n\n__**{HuidigeVerzekering['insured']}**__\
                            \n\nKlopt dit?",
                        "author": "",
                        "items": {}
                    }
                    result = await showConfirmationScreen(dict_)
                
                    if result:
                        validValue = True

        def returnTimeDeltaUitleg(timespan, length):
            if timespan == "w":
                if int(length) == 1:
                    timedeltauitleg = f"{length} week"
                else:
                    timedeltauitleg = f"{length} weken"

            elif timespan == "d":
                if int(length) == 1:
                    timedeltauitleg = f"{length} dag"
                else:
                    timedeltauitleg = f"{length} dagen"

            elif timespan == "m":
                if int(length) == 1:
                    timedeltauitleg = f"{length} maand"
                else:
                    timedeltauitleg = f"{length} maanden"

            return timedeltauitleg
        
        async def verzamelLength(timedeltauitleg):
            validValue = False            
            while not validValue:
                result = None
                if timedeltauitleg:
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
                    toDeleteMessages.append(message)
                    reaction = await self.bot.wait_for('message', timeout=120.0, check=checkMessage)                        
                    timespan = reaction.content[-1]
                    length = reaction.content[:-1]
                    timedeltauitleg = returnTimeDeltaUitleg(timespan, length)
            
            timediff = None            
            if timespan == "d":
                timediff = datetime.timedelta(days=int(length))

            elif timespan == "w":
                timediff = datetime.timedelta(weeks=int(length))

            elif timespan == "m":
                timediff = datetime.timedelta(months=int(length))
                            
            endDate = vandaag + timediff
            endDate = int(endDate.timestamp())

            if isinstance(HuidigeVerzekering, dict):
                HuidigeVerzekering["endDate"] = endDate
            elif isinstance(HuidigeVerzekering, Insurance):
                HuidigeVerzekering.endDate = endDate

        def plaatsDecimaalSeps(getal):
            if len(getal[:-3]) > 6:
                getal = getal[0:-9] + "." + getal[-9:-6] + "." + getal[-6:len(getal)]
            elif len(getal[:-3]) > 3:
                getal = getal[0:-6] + "." + getal[-6:len(getal)]

            return getal

        async def voegNieuweVerzekeringToeAanDB():
            sql = """INSERT INTO `tbl_insurances`(
                `id`, 
                `policy_nr`, 
                `agentID`, 
                `clientID`, 
                `insured`, 
                `insurance_typeID`, 
                `multiplier`, 
                `startDate`, 
                `endDate`) 
                VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, %s);"""
                
            mycursor.execute(sql, (
                HuidigeVerzekering.policy_nr, 
                HuidigeVerzekering.agentID, 
                HuidigeVerzekering.clientID, 
                HuidigeVerzekering.insured,
                HuidigeVerzekering.insurance_typeID,
                HuidigeVerzekering.multiplier,
                HuidigeVerzekering.startDate,
                HuidigeVerzekering.endDate
            ))

            mydb.commit()
            
            # Werd geklikt op het kruisje of timeout, dan zeggen we gewoon dat ie opnieuw mag.
            #dict_ = {
            #    "url": "",
            #    "title": "Daar ging wat mis",
            #    "description": f"Probeer het zo even opnieuw.\
            #    \n\nOnze excuses voor het ongemak.",
            #    "author": "",
            #    "items": {}
            #}

            #embed = await logs.return_embed(dict_, color=0xffffff)
            #message = await ctx.send(embed=embed)
            #toDeleteMessages.append(message)

        async def verzamelBonusmalus():
            # Verzamel bonusmalus      
            validValue = False
            while not validValue:
                dict_ = {
                    "url": "",
                    "title": "Ik mis nog wat gegevens",
                    "description": f"Wat is de nieuwe bonusmalus?",
                    "author": "",
                    "items": {}
                }

                embed = await logs.return_embed(dict_, color=0xffffff)
                message = await ctx.send(embed=embed)
                toDeleteMessages.append(message)
                message = await self.bot.wait_for('message', timeout=120.0, check=checkMessage)
                HuidigeVerzekering["multiplier"] = message.content

                dict_ = {
                    "url": "",
                    "title": "Kloppen deze gegevens?",
                    "description": f"De opgegeven bonusmalus:\
                        \n\n__**{HuidigeVerzekering['multiplier']}**__\
                        \n\nKlopt dit?",
                    "author": "",
                    "items": {}
                }
                
                result = await showConfirmationScreen(dict_)
            
                if result:
                    validValue = True
        
        async def verzamelDatum(type):
            if type == "begin":
                pass
            if type == "einde":
                pass

        async def toonHuidige(metConfirm):
            discordTarget = await cogs.functions.returnMember(ctx, str(HuidigeKlant.discordID))

            dict_ = {
                "url": "",
                "title": "Ter bevestiging",
                "description": f"Dit zijn de huidige gegevens\
                    \n__**Polisnummer:**__\
                    \n{HuidigeVerzekering.policy_nr}\
                    \n\
                    \n__**Klant:**__\
                    \n{discordTarget.mention}\
                    \n\
                    \n__**Verkoper:**__\
                    \n{ctx.author.mention}\
                    \n\
                    \n__**Type verzekering:**__\
                    \n{HuidigeVerzekering.insurance_type.insurable_type.sub_category.name}\
                    \n\
                    \n__**Verzekering's categorie:**__\
                    \n{HuidigeCategory.name}\
                    \n",
                "author": "",
                "items": {}
            }

            if HuidigeVerzekering.insurance_type.insurable_type.sub_category.short_name.lower() == "pv":
                dict_["description"] += f"\
                    \n__**Beroep:**__"
                    
            elif HuidigeVerzekering.insurance_type.insurable_type.sub_category.short_name == "vv":
                dict_["description"] += f"\
                    \n__**Type voertuig:**__"

            dict_["description"] += f"\
                \n{HuidigeInsurableType.name}\n"

            if HuidigeVerzekering.insurance_type.insurable_type.sub_category.short_name == "vv":
                dict_["description"] += f"\
                    \n__**Kenteken:**__\
                    \n{HuidigeVerzekering.insured}\
                    \n"                

            prijstmp = str('%.2f' % round(float((HuidigeVerzekering.amount_paid)), 2))
            prijstmp = plaatsDecimaalSeps(prijstmp.replace('.', ','))

            dict_["description"] += f"\
                \n__**Te betalen:**__\
                \n{prijstmp}\
                \n\
                \n__**Bonusmalus:**__\
                \n{HuidigeVerzekering.multiplier}\
                \n\
                \n__**Minimum bonusmalus:**__\
                \n{HuidigeInsuranceType.min_mp}\
                \n\
                \n__**Startdatum:**__\
                \n{datetime.date.fromtimestamp(HuidigeVerzekering.startDate).strftime('%d-%m-%y')}\
                \n\
                \n__**Einddatum:**__\
                \n{datetime.date.fromtimestamp(HuidigeVerzekering.endDate).strftime('%d-%m-%y')}"

            if metConfirm:
                result = await showConfirmationScreen(dict_)

                if not result:
                    dict_ = {
                        "url": "",
                        "title": "Welk gegeven wil je aanpassen?:",
                        "description": f"Klant\nVerkoper\nType verzekering\nVerzekerings categorie\nType verzekerbaargoed\nKenteken\nBonusmalus\nStartdatum\nEinddatum",
                        "author": "",
                        "items": {}
                    }

                    embed = await logs.return_embed(dict_, color=0xffffff)
                    message = await ctx.send(embed=embed)
                    toDeleteMessages.append(message)

                    message = await self.bot.wait_for('message', timeout=120.0, check=checkMessage)
                    toDeleteMessages.append(message)
                    tmp = message.content

                    if tmp == "klant":
                        await verzamelKlant()
                    elif tmp == "verkoper":
                        await verzamelWerknemer()
                    elif tmp == "type verzekering":
                        await verzamelSubCategory()
                    elif tmp == "verzekerings categorie":
                        await verzamelCategory()
                    elif tmp == "type verzekerbaargoed":
                        await verzamelInsurableType()
                    elif tmp == "kenteken":
                        await verzamelInsured()
                    elif tmp == "bonusmalus":
                        await verzamelBonusmalus()
                    elif tmp == "startdatum":
                        await verzamelDatum("start")
                    elif tmp == "einddatum":
                        await verzamelDatum("einde")
            else:
                embed = await logs.return_embed(dict_, color=0xffffff)
                message = await ctx.send(embed=embed)
                toDeleteMessages.append(message)

        def voegSaleToe():
            sql = """INSERT INTO `tbl_sales`(
                `id`,
                `agentID`,
                `amount`,
                `reason`,
                `timestamp`
                ) VALUES (NULL, %s, %s, %s, %s);"""

            mycursor.execute(sql, (
                HuidigeVerzekering.agentID,
                HuidigeVerzekering.amount_paid / 10,
                "Verzekering verkocht.",
                vandaag.timestamp()
            ))

            mydb.commit()

        async def verstuurBestanden():
            discordTarget = await cogs.functions.returnMember(ctx, str(HuidigeKlant.discordID))

            dict_ = {
                "url": "",
                "title": "De kopijen",
                "description": f"Beste klant\n\
                    \nNogmaals hartelijk bedankt voor uw aankoop.\
                    \n\nMocht er iets ontbreken, graag onmiddellijk contact opnemen met ons via het gekende systeem.\
                    \n\nMet vriendelijke groeten,\
                    \nSofia Sarafian\
                    \Secretaresse VKG",
                "author": "",
                "items": {}
            }

            if timedeltauitleg == None:
                timedeltauitleg = "7 dagen"

            bestands_een = generate_invoice_PDF(HuidigeKlant, HuidigeVerzekering, timedeltauitleg)
            bestands_twee = generate_conditions_PDF(HuidigeKlant, HuidigeVerzekering)
            embed = await logs.return_embed(dict_)
            await ctx.send(embed=embed)
            await ctx.send(files=[discord.File(bestands_een, bestands_een[4:]), discord.File(bestands_twee, bestands_twee[4:])])

            dict_ = {
                "url": "",
                "title": "De kopijen",
                "description": f"Beste klant\n\
                    \nNogmaals hartelijk bedankt voor uw aankoop.\
                    \nDe collega had mij vermeld dat ik deze documenten aan u moest doormailen.\
                    \n\nMocht er iets ontbreken, graag onmiddellijk contact opnemen met ons via het gekende systeem.\
                    \n\nMet vriendelijke groeten,\
                    \nSofia Sarafian\
                    \nSecretaresse VKG",
                "author": "",
                "items": {}
            }

            embed = await logs.return_embed(dict_)
            dmchannel = await discordTarget.create_dm()
            await dmchannel.send(embed=embed)
            await dmchannel.send(files=[discord.File(bestands_een, bestands_een[4:]), discord.File(bestands_twee, bestands_twee[4:])])

        # We verwachten
        # !verzekering
        # !verzekering nieuw discordtarget typeverzekering duur
        # !verzekering edit discordtarget polisnummer
        # !verzekering zie discordtarget
                
        toDeleteMessages.append(ctx.message)
        
        HuidigeKlant = await verzamelKlant()
        HuidigeWerknemer = await verzamelWerknemer()
        
        # Check perms
        if general.check_perms('basic', ctx.author):        
            if args:
                args = args.split()

            # Check commandtype
            # Als "nieuw", "new", "maak", "add", "toevoegen"
            if commandtype == "add" or commandtype == "new" or commandtype == "nieuw" or commandtype == "toevoegen" or commandtype == "maak":
                # Wat hebben we nodig?
                # HuidigeWerknemer hebben we
                # HuidigeKlant hebben we
                HuidigeVerzekering["agentID"] = HuidigeWerknemer.id
                HuidigeVerzekering["clientID"] = HuidigeKlant.id      
                # Check of args zijn ingevuld
                # typeverzekering = 1
                # duur = 2

                if args and len(args) >= 2 and isinstance(int(args[1]), int):
                    # We weten wie de klant is
                    # We weten wie de werknemer is
                    # We weten welk type verzekering
                    
                    HuidigeVerzekering["insurance_typeID"] = args[1]                                     
                    
                    myresult = getInsuranceTypes(1, HuidigeVerzekering["insurance_typeID"])
                    HuidigeInsuranceType = InsuranceType(myresult[0], myresult[1], myresult[2], myresult[3], myresult[4], myresult[5])
                    
                    #myresult = getInsurableTypes(HuidigeInsuranceType.insurable_typeID)
                    #HuidigeInsurableType = InsurableType(myresult[0], myresult[1], myresult[2], myresult[3])
                    HuidigeInsurableType = HuidigeInsuranceType.insurable_type

                    #myresult = getCategories(HuidigeInsuranceType.categoryID)
                    #HuidigeCategory = Category(myresult[0], myresult[1], myresult[2])
                    HuidigeCategory = HuidigeInsuranceType.category

                    #myresult = getSubCategories(HuidigeInsurableType.sub_categoryID)
                    #HuidigeSubCategory = SubCategory(myresult[0], myresult[1], myresult[2])
                    HuidigeSubCategory = HuidigeInsuranceType.insurable_type.sub_category

                    HuidigeVerzekering["insurance_typeID"] = HuidigeInsuranceType.id
                    HuidigeVerzekering["multiplier"] = HuidigeInsuranceType.default_mp
                    HuidigeVerzekering["amount_paid"] = HuidigeInsuranceType.price * HuidigeInsuranceType.default_mp

                else:
                    # We weten wie de klant is
                    # We weten wie de werknemer is
                    HuidigeSubCategory = await verzamelSubCategory()
                    HuidigeCategory = await verzamelCategory()
                    HuidigeInsurableType = await verzamelInsurableType()
                    await verzamelInsured()

                timespan = None
                length = None

                if args and len(args) >= 3:
                    timespan = args[2][-1]
                    length = args[2][:-1]

                    timedeltauitleg = returnTimeDeltaUitleg(timespan, length)

                await verzamelLength(timedeltauitleg)                       
                
                myresult = getInsuranceTypes(2, HuidigeCategory.id, HuidigeInsurableType.id)

                HuidigeInsuranceType = InsuranceType(
                    id=myresult[0],
                    categoryID=myresult[1],
                    insurable_typeID=myresult[2],
                    price=myresult[3],
                    min_mp=myresult[4],
                    default_mp=myresult[5]
                )

                HuidigeVerzekering["insurance_typeID"] = HuidigeInsuranceType.id
                HuidigeVerzekering["multiplier"] = HuidigeInsuranceType.default_mp
                HuidigeVerzekering["amount_paid"] = HuidigeInsuranceType.default_mp * HuidigeInsuranceType.price

                HuidigeVerzekering = Insurance(
                    agentID=HuidigeVerzekering["agentID"],
                    clientID=HuidigeVerzekering["clientID"],
                    insured=HuidigeVerzekering["insured"],
                    insurance_typeID=HuidigeVerzekering["insurance_typeID"],
                    multiplier=HuidigeVerzekering["multiplier"],
                    amount_paid=HuidigeVerzekering["amount_paid"],
                    startDate=HuidigeVerzekering["startDate"],
                    endDate=HuidigeVerzekering["endDate"]
                )

                await toonHuidige(True)
                await voegNieuweVerzekeringToeAanDB()

                await verstuurBestanden()
                voegSaleToe()                

            # Als "edit", "bewerk", "pasaan", "aanpassen", "verander"
            elif commandtype == "edit" or commandtype == "bewerk" or commandtype == "pasaan" or commandtype == "aanpassen" or commandtype == "verander":
                # Check of args zijn ingevuld                
                await verzamelPolis()
                await toonHuidige(True)

                sql = """UPDATE `tbl_insurances`
                    SET `agentID` = %s,
                    SET `clientID` = %s, 
                    SET `insured` = %s, 
                    SET `multiplier` = %s, 
                    SET `startDate` = %s, 
                    SET `endDate` = %s,
                    WHERE `policy_nr` = %s;"""

                mycursor.execute(sql, (
                    HuidigeVerzekering.agentID,
                    HuidigeVerzekering.clientID,
                    HuidigeVerzekering.insured,
                    HuidigeVerzekering.multiplier,
                    HuidigeVerzekering.startDate,
                    HuidigeVerzekering.endDate,
                    HuidigeVerzekering.policy_nr
                ))

                mydb.commit()

                await ctx.send("Verzekering werd aangepast.", delete_after=30)

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

                embed = await logs.return_embed(dict_, color=0xffffff)
                await ctx.send(embed=embed, delete_after=60)

            for message in toDeleteMessages:
                await message.delete()
        
async def setup(bot):
    await bot.add_cog(Insurances(bot))