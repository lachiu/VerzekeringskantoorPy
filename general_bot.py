import discord
import datetime
from discord.ext import commands

def bot_speaks(bot, txt):
    bot_name = bot.user.name
    return print(f'{datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")} | {bot_name}: {txt}')