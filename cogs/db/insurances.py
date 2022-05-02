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

        def getInsuranceTypes(insuranceID):
            # Insurance Type ophalen
            sql = "SELECT * FROM `tbl_insurance_types` WHERE `id` LIKE '%s';"
            mycursor = mydb.cursor()
            mycursor.execute(sql, (insuranceID,))
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
                startDate = datetime.datetime.today().strftime('%d-%m-%y')
                endDate = datetime.datetime.today() + datetime.timedelta(days=7)
                endDate = endDate.strftime('%d-%m-%y')
                HuidigeInsuranceType = None
                HuidigeInsurableType = None
                HuidigeCategory = None
                HuidigeSubCategory = None
                NieuweVerzekering = Insurance(self.bot, agent.discordID, client.discordID, insured, insurance_typeID, multiplier, amount_paid, startDate, endDate)
                
                # Check of args zijn ingevuld
                # typeverzekering = 1
                # duur = 2

                if args and len(args) >= 2 and cogs.functions.checkValue("isNumber", int(args[1])):
                    NieuweVerzekering.insurance_typeID = args[1]                                     
                    
                    myresult = getInsuranceTypes(NieuweVerzekering.insurance_typeID)
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

                            if isinstance(stuff[0], discord.Reaction):
                                if str(stuff[0].emoji) == '1️⃣':
                                    myresult = getSubCategories(1)
                                    HuidigeSubCategory = SubCategory(myresult[0][0], myresult[0][1], myresult[0][2])                                    
                                    
                                if str(stuff[0].emoji) == '2️⃣':
                                    myresult = getSubCategories(2)
                                    HuidigeSubCategory = SubCategory(myresult[0][0], myresult[0][1], myresult[0][2])                                    

                                if str(stuff[0].emoji) == '❌':                                    
                                    break

                            if isinstance(stuff[0], discord.Message):
                                if stuff.content == "pv" or stuff.content == "persoon":
                                    myresult = getSubCategories(1)
                                    HuidigeSubCategory = SubCategory(myresult[0][0], myresult[0][1], myresult[0][2])                                    
                            
                                if stuff.content == "vv" or stuff.content == "vervoer":
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
                
                choices = {
                    1: [1, 2, 5],
                    2: [1, 3, 4]
                }

                choiceslist = choices[HuidigeCategory.id]
                listcategoryclasses = []

                for item in choiceslist:
                    myresult = getCategories(item)
                    listcategoryclasses.append(Category(myresult[0][0], myresult[0][1], myresult[0][2]))

                dict_ = {
                    "url": "",
                    "title": "Ik mis nog wat gegevens",
                    "description": f"Om welke categorie gaat het?\
                        \nReageer met de korte of lange naam.",
                    "author": "",
                    "items": {}
                }

                

                for item in listcategoryclasses:


                embed = await logs.return_embed(dict_, color=0xffffff)
                message = await ctx.send(embed=embed)
                reaction = await self.bot.wait_for('message', timeout=120.0, check=checkMessage)

                timedelta = None
                timespan = None
                length = None
                timedeltauitleg = None

                if args and len(args) >= 3:
                    timespan = args[2][-1]
                    length = args[2][:-1]

                    if timespan == "w" or timespan == "d" or timespan == "m":
                        if timespan == "w":
                            timedelta = f"weeks={length}"

                            if length == 1:
                                timedeltauitleg = f"{length} week"
                            else:
                                timedeltauitleg = f"{length} weken"

                        if timespan == "d":
                            timedelta = f"days={length}"
                            
                            if length == 1:
                                timedeltauitleg = f"{length} dag"
                            else:
                                timedeltauitleg = f"{length} dagen"

                        if timespan == "m":
                            timedelta = f"months={length}"

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
                                timedelta = f"weeks={length}"

                                if length == 1:
                                    timedeltauitleg = f"{length} week"
                                else:
                                    timedeltauitleg = f"{length} weken"

                            if timespan == "d":
                                timedelta = f"days={length}"
                                
                                if length == 1:
                                    timedeltauitleg = f"{length} dag"
                                else:
                                    timedeltauitleg = f"{length} dagen"

                            if timespan == "m":
                                timedelta = f"months={length}"

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

                

            # Als "edit", "bewerk", "pasaan", "aanpassen", "verander"
            if commandtype == "edit" or commandtype == "bewerk" or commandtype == "pasaan" or commandtype == "aanpassen" or commandtype == "verander":
                # Check of args zijn ingevuld
                pass

            # Als "zie", "bekijk", "see"
            if commandtype == "zie" or commandtype == "bekijk" or commandtype == "see":
                # Check of args zijn ingevuld
                pass

            # Als geen is meegegeven
            if not commandtype:
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