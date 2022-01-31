import os
import discord
import datetime
import mysql.connector
from typing import List
from dotenv.main import load_dotenv
from discord.ext import commands

class fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=[])
    async def tic(self, ctx, input: str):
        input = datetime.datetime.strptime(input, '%Y-%m-%d').date()
        await ctx.send(f"{input} is {isinstance(input, datetime.date)}")
        
def setup(bot):
    bot.add_cog(fun(bot))