import os
import discord
import mysql.connector
from typing import List
from dotenv.main import load_dotenv
from discord.ext import commands

class fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=[])
    async def tic(self, ctx):
        message = await ctx.send("Hey damens")
        await message.add_reaction("1️⃣")
        
def setup(bot):
    bot.add_cog(fun(bot))