import os
import yaml
import logs
import json
import random
import general
import discord
import settings
import datetime
import cogs.functions
import mysql.connector
from copy import copy
from mimetypes import init
from dateutil.parser import parse
from dotenv.main import load_dotenv
from discord.ext import commands
from general_bot import bot_speaks

from classes.insurance import Insurance
from classes.client import Client
from classes.employee import Employee

class Insurances(commands.cog):
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

        # We verwachten
        # !verzekering
        # !verzekering nieuw discordtarget typeverzekering duur
        # !verzekering edit discordtarget polisnummer
        # !verzekering zie discordtarget

        # Check perms
        if general.check_perms('basic', ctx.author):            
            if args:
                args = list(args.split(' '))
            
            # Werknemergegevens ophalen
            sql = "SELECT * FROM `tbl_agents` WHERE `discordID` LIKE '%s';"
            mycursor = mydb.cursor()
            mycursor.execute(sql, (ctx.author.id,))
            myresult = mycursor.fetchall()

            HuidigeWerknemer = Employee(
                myresult[0],
                myresult[1],
                myresult[2],
                myresult[3],
                myresult[4],
                myresult[5],
                myresult[6],
                myresult[7]
            )

            discordTarget = None
            gotClient = False
            while not gotClient:
                try:
                    discordTarget = await cogs.functions.returnMember(ctx, args[0])
                except:
                    dict_ = {
                        "url": "",
                        "title": "Er ging iets mis!",
                        "description": f"{ctx.author.mention}, probeer nog eens om de klant te taggen of de discord id door te geven.",
                        "author": "",
                        "items": {}
                    }

                    await ctx.make_embed(self, dict_, color=0xffffff)
                    
                    try:
                        args[0] = await self.bot.wait_for('message', timeout=120.0, check=cogs.functions.checkMessage)
                    except TimeoutError:
                        pass
                else:
                    gotClient = True

            # Klantgegevens ophalen
            sql = "SELECT * FROM `tbl_clients` WHERE `discordID` LIKE '%s';"
            mycursor = mydb.cursor()
            mycursor.execute(sql, (discordTarget.id,))
            myresult = mycursor.fetchall()

            HuidigeKlant = Client(
                myresult[0],
                myresult[1],
                myresult[2],
                myresult[3],
                myresult[4],
                myresult[5],
                myresult[6],
                myresult[7],
                myresult[8],
                myresult[9],
                myresult[10],
                myresult[11]
            )

            # Check commandtype
            # Als "nieuw", "new", "maak", "add", "toevoegen"
            if commandtype == "add" or commandtype == "new" or commandtype == "nieuw" or commandtype == "toevoegen" or commandtype == "maak":
                # Wat hebben we nodig?
                policy_nr = None
                agent = HuidigeWerknemer
                agentID = HuidigeWerknemer.discordID
                client = HuidigeKlant
                clientID = HuidigeKlant.discordID
                insured = None
                insurance_typeID = None
                multiplier = None
                amount_paid = None
                startDate = datetime.today().strftime('%d-%m-%y')
                endDate = datetime.today() + datetime.delta(days=7)
                endDate = endDate.strftime('%d-%m-%y')
                NieuweVerzekering = Insurance(self.bot, agentID, clientID, insured, insurance_typeID, multiplier, amount_paid, startDate, endDate)
                
                # Check of args zijn ingevuld
                # typeverzekering = 1
                # duur = 2

                if args[1] and cogs.functions.checkValue("isNumber", int(args[1])) and self.bot.insurancetypes[args[1]]:
                    insurance_typeID = args[1]
                     
                validValue = False
                while not validValue:
                    


                
                

            # Als "edit", "bewerk", "pasaan", "aanpassen", "verander"
                # Check of args zijn ingevuld

            # Als "zie", "bekijk", "see"
                # Check of args zijn ingevuld

            # Als geen is meegegeven
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


        # Anders niks
        
    async def setup(bot):
        await bot.add_cog(Insurances(bot))