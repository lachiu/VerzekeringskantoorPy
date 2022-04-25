from mimetypes import init
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

class Employee():
    def __init__(self):
        self.value = None

class EmployeeClass(commands.cog):
    def __init__(self, bot):
        self.bot = bot

    async def setup(bot):
        await bot.add_cog(EmployeeClass(bot))