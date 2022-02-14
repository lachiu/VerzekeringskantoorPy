import os
import random
import discord
import datetime
import general
import mysql.connector
from typing import List
from dateutil.parser import parse
from dotenv.main import load_dotenv
from discord.ext import commands

class fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def tic(self, ctx, input):
        if general.check_perms('dev', ctx.author):
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

            await ctx.send(randomstring)

            startDate = datetime.date.today()
            endDate = datetime.date.today() + datetime.timedelta(days=7)
            await ctx.send(f"Startdag: {startDate}")
            await ctx.send(f"Einddag: {endDate}")
        
def setup(bot):
    bot.add_cog(fun(bot))