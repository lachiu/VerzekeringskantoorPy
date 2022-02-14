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
from copy import copy
from dateutil.parser import parse
from dotenv.main import load_dotenv
from discord.ext import commands
from general_bot import bot_speaks

front_end_namen = {
    "id": "badge nummer", 
    "policy_nr": "polisnummer",   
    "policy_name": "polisnaam",
    "discordID": "discord id",
    "fname": "voornaam",
    "lname": "achternaam",
    "dob": "geboortedatum",
    "insured": "nummerplaat",
    "multiplier": "bonusmalus",
    "amount_paid": "kostprijs",
    "insurance_typeID": "verzekeringstype",
    "startDate": "begin datum",
    "endDate": "eind datum"
}

back_end_namen = {
    "badge nummer": "id",
    "polisnummer": "policy_nr",
    "polisnaam": "policy_name",
    "discord id": "discordID",
    "voornaam": "fname",
    "achternaam": "lname",
    "geboortedatum": "dob",
    "nummerplaat": "insured",
    "bonusmalus": "multiplier",
    "kostprijs": "amount_paid",
    "verzekeringstype": "insurance_typeID",
    "begin datum": "startDate",
    "eind datum": "endDate"
}

class insurances(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def verzekering(self, ctx, commandtype: str, *, args = None):
        oldvalue = None
        newvalue = None        

        load_dotenv()
        mydb = mysql.connector.connect(
            host=os.getenv('DB_SERVERNAME'),
            user=os.getenv('DB_USERNAME'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME')
        )

        insurancedict_ = {
            "id": None,
            "policy_nr": None,
            "agent": {
                "id": None,
                "fname": None,
                "lname": None,
                "dob": None,
                "discordID": None
            },
            "client": {
                "id": None,
                "fname": None,
                "lname": None,
                "dob": None,
                "discordID": None
            },
            "insured": None,
            "insurance_typeID": None,
            "multiplier": None,
            "amount_paid": None,
            "startDate": None,
            "endDate": None
        }

        def returnrandstring(qty):
            randomstring = ""
            charlist = [
                0, 1, 2,
                3, 4, 5,
                6, 7, 8,
                9
            ]

            iterable = 0
            while iterable < int(input):
                randomchar = random.randrange(0, 8)
                char = charlist[randomchar]        
                randomstring += f"{char}"
                iterable += 1
            
            return randomstring

        async def returnmember(input):
            member = await commands.MemberConverter().convert(ctx, input)
            return member

        def checkreaction(reaction, user):
            return user == ctx.author and reaction.message.channel == ctx.channel

        def checkmessage(m):
            return m.channel == ctx.channel and m.author == ctx.author

        async def validateinput(type, input):
            print()
            
        async def addreactions(message, addcross = False):
            await message.add_reaction('👍')
            await message.add_reaction('👎')
            
            if addcross:
                await message.add_reaction('❌')

        def getinsurance(policy_nr):
            sql = """
            SELECT
            `tbl_insurances`.`id` as 'policy_nr',
            CONCAT(UPPER(`tbl_sub_categories`.`short_name`), UPPER(`tbl_categories`.`short_name`), UPPER(`tbl_insurable_types`.`short_name`), FROM_UNIXTIME(`tbl_insurances`.`startDate`, '%d%m%y'), `tbl_insurances`.`policy_nr`) as 'policy_name',
            CONCAT('{\n',
                GROUP_CONCAT(
                    'id: ', `tbl_agents`.`id`, ',\n',
                    'fname: ', `tbl_agents`.`fname`, ',\n',
                    'lname: ', `tbl_agents`.`fname`, ',\n',
                    'fname: ', `tbl_agents`.`lname`, ',\n',
                    'dob: ', `tbl_agents`.`dob`, ',\n',
                    'discordID: ', `tbl_agents`.`discordID`, '\n}'
                )) as 'agent',
            CONCAT('{\n',
                GROUP_CONCAT(
                    'id: ', `tbl_clients`.`id`, ',\n',
                    'fname: ', `tbl_clients`.`fname`, ',\n',
                    'lname: ', `tbl_clients`.`fname`, ',\n',
                    'fname: ', `tbl_clients`.`lname`, ',\n',
                    'dob: ', `tbl_clients`.`dob`, ',\n',
                    'discordID: ', `tbl_clients`.`discordID`, '\n}'
                )) as 'client',
            `tbl_insurances`.`insured`,
            `tbl_insurances`.`insurance_typeID`,
            `tbl_insurances`.`multiplier`,
            `tbl_insurances`.`amount_paid`,
            FROM_UNIXTIME(`tbl_insurances`.`startDate`, '%d-%m-%Y') as 'startDate',
            FROM_UNIXTIME(`tbl_insurances`.`endDate`, '%d-%m-%Y') as 'endDate'
            FROM `tbl_insurances`
                INNER JOIN
                `tbl_agents`
                ON `tbl_insurances`.`agentID` = `tbl_agents`.`id`
                INNER JOIN
                `tbl_clients`
                ON `tbl_insurances`.`clientID` = `tbl_clients`.`id`
                INNER JOIN
				`tbl_insurance_types`
				ON `tbl_insurances`.`insurance_typeID` = `tbl_insurance_types`.`id`
				INNER JOIN                
				`tbl_categories`
				ON `tbl_insurance_types`.`categoryID` = `tbl_categories`.`id`
                INNER JOIN
				`tbl_insurable_types`
				ON `tbl_insurance_types`.`insurable_typeID` = `tbl_insurable_types`.`id`
				INNER JOIN
				`tbl_sub_categories`
				ON `tbl_insurable_types`.`subcategoryID` = `tbl_sub_categories`.`id`
            GROUP BY `tbl_insurances`.`id` WHERE `tbl_insurances`.`policy_nr` LIKE %s;"""
            mycursor = mydb.cursor()
            mycursor.execute(sql, (policy_nr,))
            myresult = mycursor.fetchall()
            insurancedict_["id"] = myresult[0][0]
            insurancedict_["policy_name"] = myresult[0][1]
            insurancedict_["agent"] = json.json_load(myresult[0][2])
            insurancedict_["client"] = json.json_load(myresult[0][3])
            insurancedict_["insured"] = myresult[0][4]
            insurancedict_["insurance_typeID"] = int(myresult[0][5])
            insurancedict_["multiplier"] = int(myresult[0][6])
            insurancedict_["amount_paid"] = int(myresult[0][7])
            insurancedict_["startDate"] = datetime.date(myresult[0][8])
            insurancedict_["endDate"] = datetime.date(myresult[0][9])

        async def requestvalue(type):
            dict_ = None
            if type in insurancedict_ and not type == "agent" and not type == "client":
                dict_ = {
                    "url": "",
                    "title": "Benodigd gegeven",
                    "description": f"{ctx.author.mention}, gelieve de {front_end_namen[type]} op te geven.",
                    "author": "",
                    "items": {}
                }



                if type == "startDate" or type == "endDate":
                    dict_["description"] = dict_["description"] + \
                        f"Dit dient uiteraard een geldige datum te zijn. \
                        Ook mag deze niet in het verleden liggen."
            else:
                dict_ = {
                    "url": "",
                    "title": "Probleempje",
                    "description": f"{ctx.author.mention}, {type} bestaat niet.",
                    "author": "",
                    "items": {}
                }

                await logs.make_embed(self, ctx, dict_)

            # Wat voor verzekering
            # Wat word er verzekerd
            # Einddatum

        async def changevalue(type, input = None):
            succesfullychanged = False
            tmpvalue = None
            tmpinput = None
            while not succesfullychanged:
                oldvalue = insurancedict_[type]

                if input == None:
                    try:
                        await requestvalue(type)
                        message = await self.bot.wait_for('message', timeout=120.0, check=checkmessage)
                    except TimeoutError:
                        pass
                    else:
                        tmpinput = message.content
                else:
                    tmpinput = input

                if await validateinput(type, tmpinput):
                    if type == "startDate" or type == "endDate":
                        tmpvalue = parse(tmpinput).date()
                    else:
                        tmpvalue = tmpinput
                else:
                    if type == "startDate":
                        tmpvalue = datetime.date.today()
                    elif type == "endDate":
                        tmpvalue = datetime.date.today() + datetime.timedelta(days=7)

                newvalue = tmpvalue

                if input == None:
                    dict_ = {
                        "url": "",
                        "title": f"{front_end_namen[type]} aanpassen",
                        "description": f"{ctx.author.mention}, zie hier de aanpassing:",
                        "author": "",
                        "items": {
                            f"Oude waarde van {front_end_namen[type]}": oldvalue,
                            f"Nieuwe waarde van {front_end_namen[type]}": newvalue
                        }
                    }

                    embed = await logs.return_embed(dict_, 0xFF0000)
                    message = await ctx.send(embed=embed)
                    await addreactions(message, True)

                    try:
                        reaction = await self.bot.wait_for('reaction_add', timeout=120.0, check=checkreaction)
                    except TimeoutError:
                        pass

                    if str(reaction[0].emoji) == '👍':                
                        succesfullychanged = True                        

                    if str(reaction[0].emoji) == '❌':
                        break
                else:
                    succesfullychanged = True

                insurancedict_[type] = tmpvalue

        def toonhuidige():
            tmpitems = {}
            tmpvalue = None
            for key,value in insurancedict_.items():
                if key == "id" or key == "policy_nr" or key == "insurance_typeID" or key == "multiplier":
                    tmpvalue = value
                if key == "agent" or key == "client":
                    tmpvalue = value["fname"] + " " + value["lname"] + " | " + returnmember(value["discordID"]).mention
                if key == "insured":
                    if value == None:
                        tmpvalue = ":white_check_mark:"
                    else:
                        tmpvalue = value
                if key == "amount_paid":
                    tmpvalue = f"€ {format(value, '8_.2f')}"
                if key == "startDate" or key == "endDate":
                    tmpvalue = value.strftime("%d-%m-%Y")

                tmpitems[front_end_namen[key]] = tmpvalue

            dict_ = {
                "url": "",
                "title": "Huidige verzekering",
                "description": f"{ctx.author.mention}, dit zijn de huidige gegevens.",
                "author": "",
                "items": tmpitems
            }

            return dict_

        async def keuzemenu():
            print()

        async def verzekeringskeuzemenu():
            sql = "SELECT * FROM `tbl_categories`;"
            mycursor = mydb.cursor()
            mycursor.execute(sql)
            myresult = mycursor.fetchall()

            verzekeringsoortenkort = []
            verzekeringsoortenlang = []
            tmpitems = []
            for row in myresult:
                tmpdict = {
                    "kortenaam": row[1],
                    "naam": row[2]
                }
                tmpitems.append(tmpdict)
                verzekeringsoortenkort.append(row[1])
                verzekeringsoortenlang.append(row[2])

            validchoice = True
            value = None
            while validchoice:
                dict_ = {
                    "url": "",
                    "title": "Keuzemenu",
                    "description": f"{ctx.author.mention}, welke verzekering wilt u kieze?\n",
                    "author": "",
                    "items": None
                }
                
                tmpdict = {}                
                for value in tmpitems:
                    tmpdict[f"{value['naam']}"] = value["kortenaam"]
                    
                dict_["items"] = tmpdict

                await logs.make_embed(self, ctx, dict_)
                message = await self.bot.wait_for('message', timeout=120.0, check=checkmessage)
                answer = message.content
                if answer in verzekeringsoortenkort or answer in verzekeringsoortenlang:
                    subcattmp = None
                    if answer == "ba" or answer == "burgerlijke aansprakelijkheid" or answer == "zv" or answer == "zorg verzekering":
                        subcattmp = 1
                    if answer == "om" or answer == "omnium" or answer == "fom" or answer == "full omnium":
                        subcattmp = 2
                    
                    if not subcattmp == None:
                        sql = "SELECT * FROM `tbl_insurable_types` WHERE `subcategoryID` LIKE %s;"
                        mycursor = mydb.cursor()
                        mycursor.execute(sql, (subcattmp,))
                        myresult = mycursor.fetchall()
                        
                        naamkort = []
                        naamlang = []
                        tmpitems = []
                        for row in myresult:
                            tmpdict = {
                                "kortenaam": row[1],
                                "naam": row[2]
                            }

                            tmpitems.append(tmpdict)
                            naamkort.append(row[1])
                            naamlang.append(row[2])
                  
                        dict_ = {
                            "url": "",
                            "title": "Keuzemenu",
                            "description": f"{ctx.author.mention}",
                            "author": "",
                            "items": tmpdict
                        }

                        if subcattmp == 1:
                            dict_["description"] += ", gelieve aan te geven welke baan meneer/mevrouw heeft."
                        if subcattmp == 2:
                            dict_["description"] += ", gelieve het type voertuig aan te geven."
                        
                        validchoicend = True
                        answersub = None
                        while validchoicend:
                            await logs.make_embed(self, ctx, dict_)
                            message = await self.bot.wait_for('message', timeout=120.0, check=checkmessage)
                            answersub = message.content

                            if answersub in naamkort or answersub in naamlang:                                
                                # Selecteer opgegeven ding in db
                                # Haal multiplier, prijs op
                                # 

                                if subcattmp == 2:
                                    # Vraag ook nummerplaat
                                    print()

                                validchoicend = False
                                validchoice = False

                        dict_ = {
                            "url": "",
                            "title": "Keuzemenu",
                            "description": f"{ctx.author.mention}, gelieve het kenteken op te geven.",
                            "author": "",
                            "items": None
                        }

                        await logs.make_embed(self, ctx, dict_)
              
            sql = "SELECT * FROM `tbl_categories`;"
            mycursor = mydb.cursor()
            mycursor.execute(sql)
            myresult = mycursor.fetchall()

        async def verificatiemenu():
            surebool = False
            while not surebool:
                surebool = True

        if general.check_perms('administrative', ctx.author):
            if commandtype == "add" or commandtype == "new" or commandtype == "nieuw" or commandtype == "toevoegen":


                print()

            if commandtype == "bekijken" or commandtype == "zie" or commandtype == "see":
                # Kies tussen:
                    # Het verzekerde
                    # Bekijk laatste 5 producten van een klant

                # Als administrator:
                    # Bekijk laatste 10 verkochte producten van werknemer
                    # Bekijk laatste 10 verkochte producten op basis van begin of einddatum
                    print()

            if commandtype == "ziehuidig":
                print()

def setup(bot):
    bot.add_cog(insurances(bot))