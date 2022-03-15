from asyncio import wait_for
import os
from sqlite3 import Date
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

class temporary(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def verzekeringalpha(self, ctx, type: str, *, args):
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

        async def vraagGegeven(type):
            dict_ = {
                "url": "",
                "title": "Missende gegevens",
                "description": f"Ik mis een {type}.",
                "author": "",
                "items": None
            }

            await logs.return_embed(dict_)

        async def verkrijgGegeven(type):
            vraagGegeven(type)
            input = await self.bot.wait_for("message", timeout=120, check=checkMessage)
            if verifieerAntwoord(type, input):
                return input

        

        async def verifieerAntwoord(type, input):
            tmpbool = False
            if type == "klant":
                if returnMember(input):
                    tmpbool = True
            if type == "cat":
                if input in catlist:
                    tmpbool = True
            if type == "subcategorie":
                if input in subcatlist:
                    tmpbool = True
            if type == "duration":
                input = parse(input).date()
                if isinstance(input, datetime):
                    tmpbool = True
            return tmpbool

        if general.check_perms('basic', ctx.author):
            klant = None
            cat = None
            subcategorie = None
            duration = None
            args = None
            addList = ["add", "toevoegen", "voegtoe", "voeg_toe", "nieuw", "aanmaken"]                        
            if type in addList: # Nieuwe verzekering aanmaken
                if args:
                    args = list(args.split(' '))

                try:                    
                    if verifieerAntwoord("klant", args[0]):
                        klant = returnMember(args[0])
                except: 
                    klant = verkrijgGegeven("klant")   
                
                try:
                    if verifieerAntwoord("cat", args[1]):
                        cat = args[1]
                except:
                    cat = verkrijgGegeven("cat")
                
                try:
                    if verifieerAntwoord("subcategorie", args[2]):
                        subcategorie = args[2]
                except:
                    subcategorie = verkrijgGegeven("subcategorie")
                
                try:
                    if verifieerAntwoord("duration", args[3]):
                        duration = args[3]
                except:
                    duration = verkrijgGegeven("duration")

                verkrijgKlantGegevens(klant)

            editList = ["edit", "pasaan", "aanpassen", "verander"]
            if type in editList:
                print()

            seeList = ["see", "zie", "bekijk"]
            if type in seeList:
                print()

            verlengList = ["extend", "verleng"]
            if type in verlengList:
                print()

async def setup(bot):
    await bot.add_cog(temporary(bot))