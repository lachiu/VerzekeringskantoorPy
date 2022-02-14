import os
import logs
import time
import yaml
import datetime
import discord
import general
import settings
import mysql.connector
from copy import copy
from dateutil.parser import parse
from dotenv.main import load_dotenv
from discord.ext import commands
from general_bot import bot_speaks

templatedict_ = {
    "url": "",
    "title": "",
    "description": f"",
    "author": "",
    "items": {}
}

klanttemplatedict_ = templatedict_
klanttemplatedict_["items"] = {
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

nettenamen = {
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

nettekeys = {
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

licenses = [
    "licenseA",
    "licenseB",
    "licenseC",
    "flight", 
    "vaarbewijs"
]

class clients(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def klant(self, ctx, type: str, *, args = None):
        if general.check_perms('basic', ctx.author):
            klantdict_ = klanttemplatedict_
            load_dotenv()
            mydb = mysql.connector.connect(
                host=os.getenv('DB_SERVERNAME'),
                user=os.getenv('DB_USERNAME'),
                password=os.getenv('DB_PASSWORD'),
                database=os.getenv('DB_NAME')
            )
            mycursor = mydb.cursor()
            def checkreaction(reaction, user):
                return user == ctx.author and reaction.message.channel == ctx.channel

            def checkmessage(m):
                return m.channel == ctx.channel and m.author == ctx.author

            def hasspecialchar(input):
                list = input.split()
                specialcharlist = ["@", ";", "!", "?", ",", "#",
                    "~", "$", "%", "&", "*", "(", ")", "^", "-",
                    "=", "+", "`", "¬", "¦", "|"] 

                tmpbool = False
                for char in list:
                    for specialchar in specialcharlist:
                        if char == specialchar:
                            tmpbool = True

                return tmpbool
                
            def validinput(type, input):
                if type == "fivemID":
                    if len(input) == 40:
                        return input
                    else:
                        return None

                if type == "discordID":
                    try:
                        return input.id
                    except:
                        return None

                if type == "fname" or type == "lname":
                    if not input == "" and not input == None:
                        return input
                    else:
                        return None

                if type == "dob":
                    try:
                        input = parse(input)
                        input = input.date()
                    except:
                        return datetime.date(1900, 1, 1)
                    finally:
                        return input
                
                if type == "licenseA" or type == "licenseB" or type == "licenseC" or type == "flight" or type == "vaarbewijs":
                    if input == "ja" or input == "1":
                        return 1
                    elif input == "nee" or input == "0":
                        return 0

            def beautify_dict(input_dict):
                beautifuldict = copy(nettekeys)

                for key,value in input_dict["items"].items():
                    if key == "fivemID" or key == "discordID":
                        if value == None:
                            value = ":no_entry_sign:"

                    if key == "dob":
                        try: 
                            value = value.strftime("%d-%m-%Y")
                        except:
                            value = datetime.date(1900, 1, 1)
                            value = value.strftime("%d-%m-%Y")

                    if key == "fname" or key == "lname":
                        if value == None:
                            value = ":no_entry_sign:"

                    for license in licenses:
                        if key == license:
                            if value == 0 or value == None:
                                value = ":x:"
                            elif value == 1:
                                value = ":white_check_mark:"
                    
                    beautifuldict[nettenamen[key]] = value

                input_dict["items"] = beautifuldict
                return input_dict

            async def paskeyaan(self, ctx, type):
                validtype = False
                dict_ = copy(templatedict_)
                dict_["title"] = "We missen gegevens"
                dict_["items"] = {}
                if type == "fivemID":
                    validtype = True
                    dict_["description"] = "Gelieve een geldige fivem licentie te geven, indien u die niet hebt \
                        reageert u geen of leeg."
                    
                if type == "discordID":
                    validtype = True
                    dict_["description"] = "Gelieve een geldige discord id te geven of persoon te taggen, indien u die niet hebt \
                        reageert u geen of leeg."

                woord = ""
                if type == "fname" or type == "lname":
                    validtype = True                    
                    if type == "fname":
                        woord = "voornaam"
                    elif type == "lname":
                        woord = "achternaam"
                    dict_["description"] = f"Gelieve een geldige {woord} te geven. \
                        \nIndien meerdere vult u dat ook gewoon in."

                if type == "dob":
                    validtype = True
                    dict_["description"] = "Gelieve een geldige geboortedatum te geven."

                if type == "licenseA" or type == "licenseB" or type == "licenseC" or type == "flight" or type == "vaarbewijs":
                    validtype = True
                    dict_["description"] = f"Gelieve aan te geven of meneer/mevrouw \
                        in het bezit is van een geldig {nettenamen[key]}. \
                        \nAntwoorden dient te gebeuren met ja of nee."
                    
                if validtype:
                    invalidinput = True
                    firstattempt = False
                    while invalidinput:
                        try:
                            await logs.make_embed(self, ctx, dict_)
                            reaction_message = await self.bot.wait_for('message', timeout=120.0, check=checkmessage)
                        except TimeoutError:
                            if not firstattempt:
                                firstattempt = True
                                pass
                        else:                            
                            if type == "dob" and not klantdict_["items"]["dob"] == datetime.date(1950, 1, 1):
                                invalidinput = False
                            elif not "reaction_message" == "" and type == "fname" or type == "lname":
                                invalidinput = False
                            elif type == "fivemID":
                                invalidinput = False
                            elif type == "discordID":
                                invalidinput = False
                            elif type == "licenseA" or type == "licenseB" or type == "licenseC" or type == "flight" or type == "vaarbewijs":
                                invalidinput = False

                            if type == "discordID":
                                try:
                                    member = await commands.MemberConverter().convert(ctx, reaction_message.content)
                                except:
                                    member = None
                                finally:
                                    klantdict_["items"][type] = validinput(type, member)                                
                            else:
                                klantdict_["items"][type] = validinput(type, reaction_message.content)

            if type == "new" or type == "nieuw" or type == "add":
                klantdict_["title"] = "Nieuwe klant aanmaken"
                klantdict_["description"] = "Dit zijn de opgegeven gegevens. \
                    \nIk kom zo bij u terug mocht een van de gegevens niet kloppen."
                                
                if args:
                    index = 0
                    values = list(nettenamen.keys())
                    args = list(args.split(' '))
                    for arg in args:                        
                        key = values[index]

                        if key == "fname" or key == "lname":
                            arg = arg.replace("_", " ")

                        if key == "discordID":
                            try:
                                arg = await commands.MemberConverter().convert(ctx, arg)
                            except:
                                arg = None
                        
                        arg = validinput(key, arg)
                        klantdict_["items"][key] = arg
                        index = index + 1

                    await logs.make_embed(self, ctx, beautify_dict(copy(klantdict_)))

                invalidinput = True
                while invalidinput:
                    dict_ = copy(templatedict_)
                    dict_["title"] = "Nieuwe klant aanmaken"
                    dict_["description"] = "Dit zijn de huidige gegevens. \
                        \nKloppen deze gegevens?"

                    if args:
                        dict_["items"] = {}
                        tmpdict = copy(dict_)
                    else:
                        tmpdict = beautify_dict(copy(dict_))
                                         
                    embed = await logs.return_embed((tmpdict))
                    message = await ctx.send(embed=embed)          
                    await message.add_reaction('👍')
                    await message.add_reaction('👎')                   
                    reaction = await self.bot.wait_for('reaction_add', timeout=120.0, check=checkreaction)

                    if str(reaction[0].emoji) == '👍':
                        invalidinput = False
                    else:                        
                        tochangekey = ""
                        oldvalue = ""
                        newvalue = ""                        
                        received_answer = False
                        while not received_answer:
                            dict_ = copy(templatedict_)
                            dict_["title"] = "Nieuwe klant aanmaken"
                            dict_["description"] = "Welk gegeven wilt u aanpassen?"
                            for key,value in beautify_dict(copy(klantdict_))["items"].items():
                                dict_["description"] = f"{dict_['description']}\
                                    \n**{key}**"

                            dict_["items"] = {}
                            await logs.make_embed(self, ctx, dict_)
                            try:
                                tochangekey = await self.bot.wait_for('message', timeout=120.0, check=checkmessage)
                                tochangekey = copy(nettekeys[tochangekey.content])
                            except:
                                received_answer = True                                
                            else:
                                try:                         
                                    oldvalue = klantdict_["items"][tochangekey]                                
                                    await paskeyaan(self, ctx, tochangekey)
                                    newvalue = klantdict_["items"][tochangekey] 
                                except:
                                    await ctx.send("Oei, daar ging iets mis. Dat proberen we opnieuw.", delete_after=10)                                       
                                else:
                                    dict_ = copy(templatedict_)
                                    dict_["title"] = "Uw wijziging:"
                                    dict_["description"] = "U staat op het punt deze wijziging door te voeren:"

                                    if oldvalue == None or oldvalue == 0:
                                        oldvalue = ":x:"
                                    elif oldvalue == 1:
                                        oldvalue = ":white_check_mark:"
                                    
                                    if newvalue == None or newvalue == 0:
                                        newvalue = ":x:"
                                    elif newvalue == 1:
                                        newvalue = ":white_check_mark:"

                                    dict_["items"] = {
                                        f"Oude waarde van {nettenamen[tochangekey]}:": oldvalue,
                                        f"Nieuwe waarde van {nettenamen[tochangekey]}:": newvalue
                                    }

                                    await logs.make_embed(self, ctx, dict_)
                                    
                                    dict_ = copy(templatedict_)
                                    dict_["description"] = "Bent u tevreden met deze aanpassing?"
                                    dict_["items"] = copy(klantdict_["items"])
                                    embed = await logs.return_embed(beautify_dict(copy(dict_)))
                                    message = await ctx.send(embed=embed)
                                    await message.add_reaction('👍')
                                    await message.add_reaction('👎')          
                                    await message.add_reaction('❌')               
                                    reaction = await self.bot.wait_for('reaction_add', timeout=120.0, check=checkreaction)

                                    if str(reaction[0].emoji) == '👍':
                                        received_answer = True
                                    elif str(reaction[0].emoji) == '❌' or str(reaction[0].emoji) == '👎' :
                                        klantdict_["items"][tochangekey] = oldvalue

                validsqlinsert = False
                if not klantdict_["items"]["discordID"] == None:
                    validsqlinsert = True
                
                oldvalue = ""
                newvalue = ""
                while not validsqlinsert:
                    tmpdict = copy(templatedict_)
                    tmpdict["title"] = "Er ging iets mis!"
                    tmpdict["description"] = f"Ik kan geen klant toevoegen zonder discord id.\
                        \n\
                        \n:one: | Discord id\
                        \n:x:   | Annuleren"
                    tmpdict["items"] = {}
                    embed = await logs.return_embed(tmpdict)
                    message = await ctx.send(embed=embed)
                    await message.add_reaction("1️⃣")
                    await message.add_reaction('❌')
                    reaction = await self.bot.wait_for('reaction_add', timeout=120.0, check=checkreaction)
                    
                    if str(reaction[0].emoji) == '1️⃣':
                        goedaangepast = False
                        while not goedaangepast:
                            try:
                                oldvalue = klantdict_["items"]["discordID"]
                                await paskeyaan(self, ctx, "discordID")
                                newvalue = klantdict_["items"]["discordID"]
                            except:
                                await ctx.send(f"{ctx.author.mention}, oei daar ging iets mis. Probeer zo opnieuw.", delete_after=10)
                            else:
                                dict_ = copy(templatedict_)
                                dict_["title"] = "Uw wijziging:"
                                dict_["description"] = "U staat op het punt deze wijziging door te voeren:"
                                dict_["items"] = {
                                    f"Oude waarde van {nettenamen['discordID']}:": oldvalue,
                                    f"Nieuwe waarde van {nettenamen['discordID']}:": newvalue
                                }

                                embed = await logs.return_embed(dict_)
                                message = await ctx.send(embed=embed)
                                await message.add_reaction('👍')
                                await message.add_reaction('👎')
                                reaction = await self.bot.wait_for('reaction_add', timeout=120.0, check=checkreaction)

                                if str(reaction[0].emoji) == '👍':
                                    goedaangepast = True
                        validsqlinsert = True

                    elif str(reaction[0].emoji) == '❌':
                        dict_ = copy(templatedict_)
                        dict_["title"] = "Foutje"
                        dict_["description"] = "Probeer even opnieuw."
                        await logs.make_embed(self, ctx, dict_)

                validsqlinsertCheckTwo = False
                while not validsqlinsertCheckTwo:
                    tmpdict = copy(templatedict_)
                    tmpdict["title"] = "Er ging iets mis!"
                    tmpdict["description"] = f"Ik kan geen klant toevoegen zonder voornaam en achternaam.\
                        \nBeide dienen toegevoegd te worden.\
                        \nWelke van de 2 wil je nu toevoegen?\
                        \n\
                        \n:one: | Voornaam\
                        \n:two: | Achternaam\
                        \n:x:   | Annuleren"
                    tmpdict["items"] = {}
                    embed = await logs.return_embed(tmpdict)
                    message = await ctx.send(embed=embed)
                    await message.add_reaction("1️⃣")
                    await message.add_reaction("2️⃣")
                    await message.add_reaction('❌')
                    reaction = await self.bot.wait_for('reaction_add', timeout=120.0, check=checkreaction)

                    if str(reaction[0].emoji) == '1️⃣':
                        goedaangepast = False
                        while not goedaangepast:
                            try:
                                oldvalue = klantdict_["items"]["fname"]
                                await paskeyaan(self, ctx, "fname")
                                newvalue = klantdict_["items"]["fname"]
                            except:
                                await ctx.send(f"{ctx.author.mention}, oei daar ging iets mis. Probeer zo opnieuw.", delete_after=10)
                            else:
                                dict_ = copy(templatedict_)
                                dict_["title"] = "Uw wijziging:"
                                dict_["description"] = "U staat op het punt deze wijziging door te voeren:"
                                dict_["items"] = {
                                    f"Oude waarde van {nettenamen['fname']}:": oldvalue,
                                    f"Nieuwe waarde van {nettenamen['fname']}:": newvalue
                                }

                                embed = await logs.return_embed(dict_)
                                message = await ctx.send(embed=embed)
                                await message.add_reaction('👍')
                                await message.add_reaction('👎')
                                reaction = await self.bot.wait_for('reaction_add', timeout=120.0, check=checkreaction)

                                if str(reaction[0].emoji) == '👍':
                                    if klantdict_["items"]["lname"] == None:
                                        goedaangepast = False
                                    else:
                                        goedaangepast = True

                    elif str(reaction[0].emoji) == '2️⃣':
                        goedaangepast = False
                        while not goedaangepast:
                            try:
                                oldvalue = klantdict_["items"]["lname"]
                                await paskeyaan(self, ctx, "lname")
                                newvalue = klantdict_["items"]["lname"]
                            except:
                                await ctx.send(f"{ctx.author.mention}, oei daar ging iets mis. Probeer zo opnieuw.", delete_after=10)
                            else:
                                dict_ = copy(templatedict_)
                                dict_["title"] = "Uw wijziging:"
                                dict_["description"] = "U staat op het punt deze wijziging door te voeren:"
                                dict_["items"] = {
                                    f"Oude waarde van {nettenamen['lname']}:": oldvalue,
                                    f"Nieuwe waarde van {nettenamen['lname']}:": newvalue
                                }

                                embed = await logs.return_embed(dict_)
                                message = await ctx.send(embed=embed)
                                await message.add_reaction('👍')
                                await message.add_reaction('👎')
                                reaction = await self.bot.wait_for('reaction_add', timeout=120.0, check=checkreaction)

                                if str(reaction[0].emoji) == '👍':
                                    if klantdict_["items"]["fname"] == None:
                                        goedaangepast = False
                                    else:
                                        goedaangepast = True

                    elif str(reaction[0].emoji) == '❌':
                        dict_ = copy(templatedict_)
                        dict_["title"] = "Foutje"
                        dict_["description"] = "Probeer even opnieuw."
                        await logs.make_embed(self, ctx, dict_)

                    fname = klantdict_["items"]["fname"]
                    lname = klantdict_["items"]["lname"]
                    tocheck = [fname, lname]
                    for item in tocheck:
                        if not item == None and \
                            not item == "" and \
                            not hasspecialchar(item):
                            validsqlinsertCheckTwo = True

                log_dict = {
                    "mod": ctx.author.id,
                    "user": ctx.author.id,
                    "reason": f"{self.bot.boss.mention}, er werd een nieuwe klant toegevoegd \
                    door {ctx.author.mention}, dit zijn de gegevens van meneer/mevrouw.",
                    "unixtime": int(time.time()),
                    "perms": "basic",
                    "type": 7   
                }

                log_dict["items"] = copy(klantdict_["items"])
                await logs.make_discord_log(self, ctx, beautify_dict(log_dict))
                items = klantdict_["items"]
                sql = "INSERT INTO `tbl_clients`(`id`, `fivemID`, `discordID`, `fname`, `lname`, `dob`, `licenseA`, `licenseB`, `licenseC`, `flight`, `vaarbewijs`) VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
                mycursor.execute(sql, (items["fivemID"], items["discordID"], items["fname"], items["lname"], items["dob"], items["licenseA"], items["licenseB"], items["licenseC"], items["flight"], items["vaarbewijs"]))
                mydb.commit()

            if type == "edit" or type == "verander" or type == "aanpassen"or type == "pasaan":
                member = None
                fivemID = None
                fname = None
                lname = None
                dob = None

                if args:
                    args = list(args.split(' '))
                    for arg in args:
                        try:
                            member = await commands.MemberConverter().convert(ctx, arg)
                        except:
                            try:
                                fivemID = validinput("fivemID", arg)
                            except:
                                try:
                                    fname = validinput("fname", arg)
                                    lname = validinput("lname", arg)
                                    dob = validinput("dob", arg)
                                except:
                                    pass
                
                else:
                    dict_ = copy(templatedict_)
                    dict_["title"] = "Klant opzoeken"
                    dict_["description"] = "Ik moet wel wat gegevens hebben om een klant op te zoeken.\
                        \nU kan kiezen tussen:\
                        \n\
                        \n**fivem licentie**\
                        \nof\
                        \n**discord gebruiker**\
                        \nof\
                        \n**voornaam** en\
                        \n**achternaam** en \
                        \n**geboortedatum**"
                    await logs.make_embed(self, ctx, dict_)
                        
            if type == "ziehuidig":
                try:                
                    await logs.make_embed(self, ctx, beautify_dict(copy(klantdict_)))
                except: 
                    pass
            
            
            #sql = ";"
            #mycursor = mydb.cursor()
            #mycursor.execute(sql, ("",))
            #myresult = mycursor.fetchone()
            # type is new/nieuw 
            # type is edit/verander/aanpassen/pasaan
            # type is blacklist
            # type is 

            # Edit command
            # Update command voor rijbewijzen

def setup(bot):
    bot.add_cog(clients(bot))