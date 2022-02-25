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

class Agent():
    def __init__(self, id, fname, lname, discordID):
        self.agent_nummer = id
        self.voornaam = fname
        self.achternaam = lname
        self.discord_id = discordID

class Verzekerde():
    def __init__(self, id, klant, insurances):
        self.id = id if not None else None

        tmparray = {
            "voornaam": None,
            "achternaam": None,
            "geboortedatum": datetime.date(1900, 1, 1),
            "telefoon": None,
            "rijbewijs A": 0,
            "rijbewijs B": 0,
            "rijbewijs C": 0,
            "vliegbrevet": 0,
            "vaarbewijs": 0
        }

        self.klant = klant if not None else tmparray
        
        tmparray = [
            {
                "ba": 0,
                "hv": 0,
                "zv": 0,
            },
            {}
        ]

        self.insurances = insurances if not None else tmparray

    def GenereerNaam(self, verzekering = None):
        charlist = [
            0, 1, 2,
            3, 4, 5,
            6, 7, 8,
            9
        ]
        datumvandaag = datetime.today().strftime('%d%m%y')
        randomstring = f"{verzekering}{datumvandaag}" if not verzekering == None else ""
        iterable = 0
        while iterable < int(5):
            randomchar = random.randrange(0, 8)
            char = charlist[randomchar]
            randomstring += f"{char}"
            iterable += 1

        return randomstring 

    def VoegAutoVerzekeringToe(self, nummerplaat, type, insurance, agent):
        if not self.insurances[1][nummerplaat]:
            self.insurances[1][nummerplaat] = {
                "type_voertuig": insurance.insurable_name,
                "verzekeringen": {
                    "ba": None,
                    "om": None,
                    "fom": None
                }
            }
            
        verzekeringdict = {
            "verzekering_info": {
                "id": insurance.id, # Verzekerings ID
                "afkorting": insurance.concatnaam, # Geconcateneerde insurance type id
                "polis_nr": self.GenereerNaam(), # Verzekeringsnaam
                "type_id": insurance.categoryID, # Categorie id                
                "multiplier": insurance.mp,
                "kostprijs": insurance.betaald,
                "begin_datum": insurance.begintijd, # Startdate insurances
                "eind_datum": insurance.eindtijd # Enddate insurances
            },
            "medewerker": agent
        }
            
        self.insurances[1][nummerplaat]["verzekeringen"][type] = verzekeringdict
}

class insurances(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def verzekeringdelta(self, ctx, commandtype: str, *, args = None):
        agent = None
        oudewaarde = None
        nieuwewaarde = None
        klant = None
        cat = None
        subcategorie = None
        duration = None

        load_dotenv()
        mydb = mysql.connector.connect(
            host=os.getenv('DB_SERVERNAME'),
            user=os.getenv('DB_USERNAME'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME')
        )

        catlist = []
        sql = "SELECT `short_name` FROM `tbl_categories`;"
        mycursor = mydb.cursor()
        mycursor.execute(sql)
        myresult = mycursor.fetchall()
        for result in myresult:
            catlist.append(result)

        subcatlist = []
        sql = "SELECT `short_name` FROM `tbl_insurable_types`;"
        mycursor = mydb.cursor()
        mycursor.execute(sql)
        myresult = mycursor.fetchall()
        for result in myresult:
            subcatlist.append(result)

        async def returnMember(input):
            member = await commands.MemberConverter().convert(ctx, input)
            return member

        def checkReaction(reaction, user):
            return user == ctx.author and reaction.message.channel == ctx.channel

        def checkMessage(m):
            return m.channel == ctx.channel and m.author == ctx.author
        
        async def addReactions(message, addcross = False):
            await message.add_reaction('👍')
            await message.add_reaction('👎')
            
            if addcross:
                await message.add_reaction('❌')

        def getAgent(discordid):
            sql = "SELECT * FROM `tbl_agents` WHERE `discordID` LIKE '%s' AND `enabled` LIKE 1 LIMIT 1;"
            mycursor = mydb.cursor()
            mycursor.execute(sql, (discordid,))
            myresult = mycursor.fetchall()
            agent = Agent(myresult[0][0], myresult[0][3], myresult[0][4], myresult[0][6])

        def getClient(discordid):
            sql = '''
            SELECT
            `tbl_clients`.`id` as 'id',
            `tbl_clients`.`fname` as 'voornaam',
            `tbl_clients`.`lname` as 'achternaam',
            `tbl_clients`.`dob` as 'geboortedatum',
            `tbl_clients`.`phone` as 'telefoon',
            `tbl_clients`.`licenseA` as 'rijbewijs A',
            `tbl_clients`.`licenseB` as 'rijbewijs B',
            `tbl_clients`.`licenseC` as 'rijbewijs C',
            `tbl_clients`.`flight` as 'vliegbrevet',
            `tbl_clients`.`vaarbewijs` as 'vaarbewijs'
            WHERE `tbl_clients`.`discordID` LIKE '%s' LIMIT 1;''' 
            mycursor = mydb.cursor()
            mycursor.execute(sql, (discordid,))
            myresult = mycursor.fetchall()
            klantid = myresult[0][0]
            #def __init__(self, id, discordID, fname, lname, dob, insurances):
            klantarray = {
                "voornaam": myresult[0][1],
                "achternaam": myresult[0][2],
                "geboortedatum": myresult[0][3],
                "telefoon": myresult[0][4],
                "rijbewijs A": myresult[0][5],
                "rijbewijs B": myresult[0][6],
                "rijbewijs C": myresult[0][7],
                "vliegbrevet": myresult[0][8],
                "vaarbewijs": myresult[0][9]
            }
            klant = Verzekerde(klantid, klantarray, insurances)

        async def VeranderWaarde(key, input):
            if key == "klant":
                klant = await returnMember(input)

            elif key == "cat":
                cat = input

            elif key == "subcategorie":
                subcategorie = input

            elif key == "duration":
                duration = input

        async def VerificatieMenu(key, waarde = None):
            items = {}
            if waarde == None:
                items = {
                    f"Oude waarde van {key}": oudewaarde,
                    f"Nieuwe waarde van {key}": nieuwewaarde
                }
            else:
                items = {
                    key: waarde
                }

            dict_ = {
                "url": "",
                "title": "Verificatie",
                "description": "Klopt dit?",
                "author": "",
                "items": items
            }

            embed = await logs.return_embed(dict_)
            message = await ctx.send(embed=embed)
            await addReactions(message, True)

        async def VerifyInput(key, input):
            tmpbool = False
            if key == "klant":
                try:
                    await returnMember(input)
                except:
                    return False
                else:
                    return True
            if key == "cat":
                if input in catlist:
                    return True
                else:
                    return False
            if key == "subcategorie":
                if input in subcatlist:
                    return True
                else:
                    return False
            if key == "duration":
                if isinstance(input, int):
                    return True
                else:
                    try:
                        if isinstance(int(input), int):
                            return True
                        else:
                            return False
                    except:
                        return False

        async def VraagWaarde(self, ctx, waarde):
            dict_ = {
                "url": "",
                "title": "Ontbrekende gegevens",
                "description": "",
                "author": "",
                "items": {}
            }

            if waarde == "klant":
                # discord tag, id
                oudewaarde = klant
                dict_["description"] = "Gelieve de klant zijn/haar Discord te geven.\
                    Dit kan via een tag (@naam), ID of via de naam zelf in te geven."

            elif waarde == "cat":
                # job naam / voertuig type
                oudewaarde = cat
                dict_["description"] = "Gelieve te kiezen tussen een van de volgende opties:"
                for item in catlist:
                    dict_["description"] += f"\n{item}"

            elif waarde == "subcategorie":
                # subcategorie
                oudewaarde = subcategorie
                dict_["description"] = "Gelieve te kiezen tussen een van de volgende opties:"
                for item in subcatlist:
                    dict_["description"] += f"\n{item}"

            elif waarde == "duration":
                # Aantal weken dat de verzekering loopt
                oudewaarde = duration
                dict_["description"] = "Gelieve het aantal weken op te geven van de duur van de verzekering.\
                    Dit kan d.m.v. het reageren met een getal (als in x weken)."

            invalidInput = True
            while invalidInput:
                await logs.make_embed(self, ctx, dict_)
                message = await self.bot.wait_for('message', timeout=120.0, check=checkMessage)
                if VerifyInput(waarde, message.content):
                    nieuwewaarde = message.content
                    VerificatieMenu(waarde)
                    
                    try:
                        reaction = await self.bot.wait_for('reaction_add', timeout=120.0, check=checkReaction)
                    except TimeoutError:
                        pass
                    else:
                        if str(reaction[0].emoji) == '👍':                
                            invalidInput = True
                            await VeranderWaarde(waarde, nieuwewaarde)

                        elif str(reaction[0].emoji) == '❌':
                            break
                
        if general.check_perms('basic', ctx.author):
            getAgent(ctx.author.id)

            if commandtype == "add" or commandtype == "new" or commandtype == "nieuw" or commandtype == "toevoegen":
                # Variabelen declareren                
                # Check of er variabelen meegegeven zijn
                if args:
                    # klant, adhv discord id / tag
                    # cat: job naam / voertuig type
                    # subcategorie (ba, hv, zv, om, fom)                    
                    # optioneel: aantal weken 
                    args = list(args.split(' '))

                    try:
                        klant = args[0]
                    except: 
                        pass    
                    
                    try:
                        cat = args[1]
                    except:
                        pass
                    
                    try:
                        subcategorie = args[2]
                    except:
                        pass
                    
                    try:
                        duration = args[3]
                    except:
                        pass
                
                tmpdict = {
                    "klant": klant, 
                    "cat": cat, 
                    "subcategorie": subcategorie, 
                    "duration": duration
                }

                for key,value in tmpdict.items():
                    if value == None:
                        await VraagWaarde(self, ctx, key)

                # Klantgegevens ophalen
                getClient(klant.id)

                # Meegegeven variabelen
                    # Variabelen aanvullen


                # Niet meegegeven variabelen
                    # Waarden opvragen

                # Toon huidige
                # Vraag bevestiging
                    # Bevestigd
                        # Dan voegen we toe aan DB 
                    # Geweigerd
                        # Vraag wat gewijzigd moet worden
                        # Repeat
                startDate = datetime.date.today()
                endDate = datetime.date.today() + datetime.timedelta(days=7)

            if commandtype == "edit" or commandtype == "pasaan" or commandtype == "aanpassen":
                # Variabelen declareren

                # Check of variabelen meegegeven zijn
                # Meegegeven variabelen
                    # Variabelen aanvullen
                
                # Niet meegegeven variabelen
                    # Waarden opvragen

                # Toon huidige
                
                # Wacht enkele seconden
                
                # Vraag naar nieuwe waarde van aan te passen waarde
                
                # Toon huidige na aanpassing
                # Vraag bevestiging
                    # Bevestigd
                        # Dan passen we aan in DB
                    # Geweigerd
                        # Vraag wat gewijzigd moet worden
                        # Repeat

            if commandtype == "bekijken" or commandtype == "zie" or commandtype == "see":
                #if general.check_perms('administrative', ctx.author):
                    print()
                    # Kies tussen:
                        # Het verzekerde
                        # Bekijk laatste 5 producten van een klant
                    print()
                    # Als administrator:
                        # Bovenstaande
                        # Bekijk laatste 10 verkochte producten van werknemer
                        # Bekijk laatste 10 verkochte producten op basis van begin of einddatum                    

            if commandtype == "ziehuidig":
                print()

def setup(bot):
    bot.add_cog(insurances(bot))