import yaml
import discord
import settings
from discord.ext import commands
from general_bot import bot_speaks

class employees(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Add command
    # Edit command
    # Update command (permissielevel db)

def setup(bot):
    bot.add_cog(employees(bot))