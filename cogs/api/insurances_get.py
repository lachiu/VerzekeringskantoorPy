import yaml
import discord
import settings
from discord.ext import commands
from general_bot import bot_speaks

class insurances_get(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

def setup(bot):
    bot.add_cog(insurances_get(bot))