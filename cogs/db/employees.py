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
from mimetypes import init
from dateutil.parser import parse
from dotenv.main import load_dotenv
from discord.ext import commands
from general_bot import bot_speaks

class Employees(commands.cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def werknemer(self, ctx, commandtype: str, *, args = None):
        pass

    async def setup(bot):
        await bot.add_cog(Employees(bot))