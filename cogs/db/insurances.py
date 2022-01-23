import yaml
import discord
import settings
import mysql.connector
from dotenv.main import load_dotenv
from discord.ext import commands
from general_bot import bot_speaks

class insurances(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Add command
    # Edit command
    # Task loop die checkt of verzekeringen verlopen zijn

def setup(bot):
    bot.add_cog(insurances(bot))