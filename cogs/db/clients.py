import os
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

front_end_namen = {
    "fivemID": "fivem licentie",
    "discordID": "discord id",
    "fname": "voornaam",
    "lname": "achternaam",
    "dob": "geboortedatum",
    "licenseA": "rijbewijs categorie A",
    "licenseB": "rijbewijs categorie B",
    "licenseC": "rijbewijs categorie C",
    "flight": "vliegbrevet",
    "vaarbewijs": "vaarbewijs"
}

back_end_namen = {
    "fivem licentie": "fivemID",
    "discord id": "discordID",
    "voornaam": "fname",
    "achternaam": "lname",
    "geboortedatum": "dob",
    "rijbewijs categorie A": "licenseA",
    "rijbewijs categorie B": "licenseB",
    "rijbewijs categorie C": "licenseC",
    "vliegbrevet": "flight",
    "vaarbewijs": "vaarbewijs"
}

class clients(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def klant(self, ctx, commandtype: str, *, args = None):
        oldvalue = None
        newvalue = None
        clientID = None

        templateklantdict_ = {
            "fivemID": None,
            "discordID": None,
            "fname": None,
            "lname": None,
            "dob": None,
            "licenseA": 0,
            "licenseB": 0,
            "licenseC": 0,
            "flight": 0,
            "vaarbewijs": 0
        }
        klantdict_ = copy(templateklantdict_)
        
        def hasspecialchars(input):
            tmpbool = False
            input = input.split()
            specialcharlist = [
                "@", "¬", "¦",
                ";", "!", "|",
                "?", ",", "`", 
                "#", "=", "+",
                "~", "$", "-",
                "%", "&", "*", 
                "(", ")", "^",
                "[", "]", "_",
                "{", "}", "'",
                "\\", "/", "."
            ]

            for char in input:
                for specialchar in specialcharlist:
                    if char == specialchar:
                        tmpbool = True
            
            return tmpbool

        async def returnmember(input):
            member = await commands.MemberConverter().convert(ctx, input)
            return member

        def getclient(discordid):
            sql = "SELECT * FROM `tbl_clients` WHERE `discordID` LIKE %s LIMIT 1;"
            mycursor.execute(sql, (discordid,))
            myresult = mycursor.fetchall()
            clientID = myresult[0][0]
            klantdict_ = {
                "fivemID": myresult[0][1],
                "discordID": myresult[0][2],
                "fname": myresult[0][3],
                "lname": myresult[0][4],
                "dob": myresult[0][5],
                "licenseA": myresult[0][6],
                "licenseB": myresult[0][7],
                "licenseC": myresult[0][8],
                "flight": myresult[0][9],
                "vaarbewijs": myresult[0][10]
            }

        def checkreaction(reaction, user):
            return user == ctx.author and reaction.message.channel == ctx.channel

        def checkmessage(m):
            return m.channel == ctx.channel and m.author == ctx.author

        async def validateinput(type, input):
            if type == "fivemID" and input == None or input == "geen" or input == "leeg" or len(input) == 40:
                return True
            elif type == "discordID" and len(input) == 18:
                return True               
            elif type == "fname" or type == "lname" and not input == "" and not input == None and not hasspecialchars(input):
                return True
            elif type == "dob" and isinstance(parse(input).date(), datetime.date):
                return True
            elif type == "licenseA" or \
                type == "licenseB" or \
                type == "licenseC" or \
                type == "flight" or \
                type == "vaarbewijs":
                if input == "1" or input == "0" or input == 1 or input == 0:
                    return True
            else:
                return False
            
        async def addreactions(message, addcross = False):
            await message.add_reaction('👍')
            await message.add_reaction('👎')
            
            if addcross:
                await message.add_reaction('❌')

        async def changevalue(type, input = None):
            succesfullychanged = False
            tmpvalue = None
            tmpinput = None
            while not succesfullychanged:
                oldvalue = klantdict_[type]
                
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
                    if type == "discordID":
                        tmpvalue = await returnmember(tmpinput)                 
                        tmpvalue = tmpvalue.id
                    elif type == "dob":
                        tmpvalue = parse(tmpinput).date()
                    elif type == "licenseA" or \
                        type == "licenseB" or \
                        type == "licenseC" or \
                        type == "flight" or \
                        type == "vaarbewijs":
                        if tmpinput == "1":
                            tmpvalue = 1
                        elif tmpinput == "0":
                            tmpvalue = 0
                    else:
                        tmpvalue = tmpinput
                else:
                    if type == "fivemID" or type == "discordID":
                        if tmpinput == "geen" or tmpinput == "leeg":
                            tmpvalue = None
                    elif type == "dob":
                        tmpvalue = datetime.date(1900, 1, 1)
                    elif type == "licenseA" or \
                        type == "licenseB" or \
                        type == "licenseC" or \
                        type == "flight" or \
                        type == "vaarbewijs":
                        tmpvalue = 0

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
                        klantdict_[type] = tmpvalue

                    if str(reaction[0].emoji) == '❌':
                        break
                else:
                    succesfullychanged = True
                
                klantdict_[type] = tmpvalue

        async def requestvalue(type):
            dict_ = None
            if type in klantdict_:
                dict_ = {
                    "url": "",
                    "title": "Benodigd gegeven",
                    "description": f"{ctx.author.mention}, gelieve de {front_end_namen[type]} op te geven.",
                    "author": "",
                    "items": {}
                }

                if type == "fivemID" or type == "discordID":
                    dict_["description"] = dict_["description"] + \
                        " Indien u die niet hebt reageert u 'geen' of 'leeg'."

                if type == "dob":
                    dict_["description"] = dict_["description"] + \
                        " Dit dient uiteraard een geldige geboortedatum te zijn."

                if type == "licenseA" or \
                    type == "licenseB" or \
                    type == "licenseC" or \
                    type == "flight" or \
                    type == "vaarbewijs":
                    dict_["description"] = dict_["description"] + \
                        f" Indien meneer/mevrouw geen geldig {front_end_namen[type]} heeft \
                            antwoordt u met nee, anders met ja."

                await logs.make_embed(self, ctx, dict_)    

            else:
                dict_ = {
                    "url": "",
                    "title": "Probleempje",
                    "description": f"{ctx.author.mention}, {type} bestaat niet.",
                    "author": "",
                    "items": {}
                }

                await logs.make_embed(self, ctx, dict_)

        def toonhuidige():
            tmpitems = {}
            tmpvalue = None
            licenses = [
                "licenseA",
                "licenseB",
                "licenseC",
                "flight", 
                "vaarbewijs"
            ]

            for key,value in klantdict_.items():
                if key == "fivemID" or key == "discordID":
                    if value == None or value == "geen" or value == "leeg":
                        tmpvalue = ":no_entry_sign:"
                    else:
                        tmpvalue = value

                if key == "dob":
                    try: 
                        tmpvalue = value.strftime("%d-%m-%Y")
                    except:
                        tmpvalue = datetime.date(1900, 1, 1)
                        tmpvalue = value.strftime("%d-%m-%Y")

                if key == "fname" or key == "lname":
                    if value == None:
                        tmpvalue = ":no_entry_sign:"
                    else:
                        tmpvalue = value

                for license in licenses:
                    if key == license:
                        if value == 0 or value == None:
                            tmpvalue = ":x:"
                        elif value == 1:
                            tmpvalue = ":white_check_mark:"

                tmpitems[front_end_namen[key]] = tmpvalue

            dict_ = {
                "url": "",
                "title": "Huidige klant",
                "description": f"{ctx.author.mention}, dit zijn de huidige gegevens.",
                "author": "",
                "items": tmpitems
            }

            return dict_

        async def keuzemenu():
            validchoice = False
            value = None

            while not validchoice:
                dict_ = {
                    "url": "",
                    "title": "Keuzemenu",
                    "description": f"{ctx.author.mention}, wat had u graag willen aanpassen?\n",
                    "author": "",
                    "items": {}
                }

                dict_["description"] = dict_["description"] + ""
                    
                for key,value in templateklantdict_.items():
                    dict_["description"] = dict_["description"] + f"\n**{front_end_namen[key]}**"

                await logs.make_embed(self, ctx, dict_)
                message = await self.bot.wait_for('message', timeout=120.0, check=checkmessage)
                
                try:
                    value = back_end_namen[message.content]
                except:
                    pass
                else:
                    validchoice = True

            return value                    

        async def verificatiemenu():
            surebool = False
            while not surebool:
                dict_ = toonhuidige()
                dict_["description"] = dict_["description"] + " Kloppen deze gegevens?"
                embed = await logs.return_embed(dict_)
                message = await ctx.send(embed=embed)
                await addreactions(message)

                try:
                    reaction = await self.bot.wait_for('reaction_add', timeout=120.0, check=checkreaction)
                except TimeoutError:
                    pass

                if str(reaction[0].emoji) == '👍':                
                    surebool = True
                else:
                    try:
                        keuze = await keuzemenu()
                        await changevalue(keuze)
                    except:
                        pass
                    else:
                        surebool = True

        if general.check_perms('basic', ctx):
            load_dotenv()
            mydb = mysql.connector.connect(
                host=os.getenv('DB_SERVERNAME'),
                user=os.getenv('DB_USERNAME'),
                password=os.getenv('DB_PASSWORD'),
                database=os.getenv('DB_NAME')
            )
            mycursor = mydb.cursor()

            if commandtype == "add" or commandtype == "new" or commandtype == "nieuw" or commandtype == "toevoegen":
                # Add command
                # Als args meegegeven zijn:
                if args:
                    index = 0
                    klantgegevens = list(klantdict_.keys())
                    args = list(args.split(' '))
                    for arg in args:
                        key = klantgegevens[index]
                        await changevalue(key, arg)
                        index = index + 1

                for key,value in templateklantdict_.items():
                    if not key == "licenseA" and not key == "licenseB" and not key == "licenseC" and \
                        not key == "flight" and not key == "vaarbewijs":
                        if value == klantdict_[key]:
                            await changevalue(key)

                await verificatiemenu()
                
                # Check of bestaat
                try:
                    getclient(klantdict_["discordID"])
                except:
                    # Toevoegen aan db
                    sql = "INSERT INTO `tbl_clients`(`id`, `fivemID`, `discordID`, `fname`, `lname`, `dob`, `licenseA`, `licenseB`, `licenseC`, `flight`, `vaarbewijs`) VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
                    mycursor.execute(sql, (klantdict_["fivemID"], klantdict_["discordID"], klantdict_["fname"], klantdict_["lname"], klantdict_["dob"], klantdict_["licenseA"], klantdict_["licenseB"], klantdict_["licenseC"], klantdict_["flight"], klantdict_["vaarbewijs"]))
                    mydb.commit()

                    dict_ = {
                        "url": "",
                        "title": "Succes",
                        "description": f"{ctx.author.mention}, de nieuwe klant werd toegevoegd.",
                        "author": "",
                        "items": {}
                    }

                    await logs.make_embed(self, ctx, dict_)
                else:
                    member = ctx.guild.get_member(int(klantdict_["discordID"]))
                    dict_ = {
                        "url": "",
                        "title": "Probleempje",
                        "description": f"{ctx.author.mention}, {member.mention} is al een klant.",
                        "author": "",
                        "items": {}
                    }

                    await logs.make_embed(self, ctx, dict_) 

            # Edit command
            if commandtype == "edit" or commandtype == "aanpassen" or commandtype == "pasaan" or commandtype == "verander":
                # Selecteer de klant/gebruiker
                member = None
                keuze = None
                nieuwewaarde = None

                if args:
                    args = list(args.split(' '))
                    
                    try:
                        member = await returnmember(args[0])
                        klantdict_["discordID"] = str(member.id)
                    except:
                        pass                        
                        
                    try:
                        keuze = args[1]
                    except:
                        keuze = None

                    try:
                        nieuwewaarde = args[2]
                    except:
                        nieuwewaarde = None

                if klantdict_["discordID"] == None:
                    await changevalue("discordID")
                
                try:
                    getclient(klantdict_["discordID"])
                except:
                    await ctx.send("Die persoon is geen klant bij ons of heeft zijn discord niet gelinkt.", delete_after=20)

                await logs.make_embed(self, ctx, toonhuidige())
                # Keuze is of gegeven of niet
                if not keuze == None:
                    # Geef aan wat je wilt aanpassen indien niet opgegeven
                    try:
                        keuze = back_end_namen[keuze]
                    except:
                        pass
                    else:
                        try:
                            if front_end_namen[keuze]:
                                keuze = keuze
                        except:
                            keuze = await keuzemenu()
                else:
                    keuze = await keuzemenu()
                
                if not nieuwewaarde == None:
                    await changevalue(keuze, nieuwewaarde)
                else:
                    await changevalue(keuze)

                await verificatiemenu()
                
                # Update sql
                sql = "UPDATE `tbl_clients` SET `fivemID`=%s, `discordID`=%s, `fname`=%s,\
                    `lname`=%s,`dob`=%s,`licenseA`=%s,`licenseB`=%s,`licenseC`=%s,\
                    `flight`=%s,`vaarbewijs`=%s WHERE `id` LIKE %s;"
                mycursor.execute(sql, (
                    klantdict_["fivemID"],
                    klantdict_["discordID"],
                    klantdict_["fname"],
                    klantdict_["lname"],
                    klantdict_["dob"],
                    klantdict_["licenseA"],
                    klantdict_["licenseB"],
                    klantdict_["licenseC"],
                    klantdict_["flight"],
                    klantdict_["vaarbewijs"],
                    clientID))
                mydb.commit()
                
                dict_ = {
                    "url": "",
                    "title": "Succesvol aangepast",
                    "description": f"{ctx.author.mention}, de gegevens werden aangepast.",
                    "author": "",
                    "items": {}
                }

                await logs.make_embed(self, ctx, dict_)

            if commandtype == "bekijken" or commandtype == "zie" or commandtype == "see":
                if general.check_perms('basic', ctx):
                    member = None

                    if args:
                        args = list(args.split(' '))

                        try:
                            member = await returnmember(args[0])
                            klantdict_["discordID"] = str(member.id)
                        except:
                            pass
                    
                    if klantdict_["discordID"] == None:
                        await changevalue("discordID")
                    
                    try:
                        getclient(klantdict_["discordID"])
                    except:
                        await ctx.send("Die persoon is geen klant bij ons of heeft zijn discord niet gelinkt.", delete_after=20)
                        
                    await ctx.send(klantdict_)
                    await logs.make_embed(self, ctx, toonhuidige())

            if commandtype == "ziehuidig":
                if general.check_perms('basic', ctx):
                    try:
                        await logs.make_embed(self, ctx, toonhuidige())                
                    except:
                        pass

def setup(bot):
    bot.add_cog(clients(bot))