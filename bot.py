import os
import discord
import mysql.connector
from logs import return_embed
from general_bot import bot_speaks
from dotenv.main import load_dotenv
from discord.ext import commands

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

dirs = []
directory_contents = os.listdir("cogs")
for item in directory_contents:
    #print(f"Items in cogs: {os.path.relpath(item)}")
    if not item.endswith(".py"):
        dirs.append(item)
        
cogs = {}
for subdir in dirs:
    subdir_contents = os.listdir(os.path.join("cogs", subdir))
    #print(f"Lijst van content van {subdir}: {subdir_contents}")
    for item in subdir_contents:
        if item.endswith(".py"):
            cogs[item] = f"cogs.{subdir}.{item[:-3]}"

#print(f"Inhoud van cogs: {cogs}")
for key, item in cogs.items():
    #print(f"{key} - {item}")
    bot.load_extension(item)    

@bot.event
async def on_ready():
    bot_speaks(bot, f'Ik ben helemaal klaar om aan de slag te gaan als {bot.user.name}.')
    vkgGuild = bot.get_guild(875098573262438420)
    bot.boss = discord.utils.get(vkgGuild.members, id=154244184587501568)
    bot.alertchannel = discord.utils.get(vkgGuild.channels, id=934615600263749663)
    bot.leveltwochannel = discord.utils.get(vkgGuild.channels, id=934644216259293184)
    bot.announcementchannel = discord.utils.get(vkgGuild.channels, id=918435465395314718)
    bot.ruleschannel = discord.utils.get(vkgGuild.channels, id=918439427221635123)
    bot.ticketchannel = discord.utils.get(vkgGuild.channels, id=918435738662629386)
    bot.frontdoor = discord.utils.get(vkgGuild.channels, id=875098573547646991)
    bot.schooldocs = discord.utils.get(vkgGuild.channels, id=918438986719039518)
    bot.schoollevelthree = discord.utils.get(vkgGuild.channels, id=918438817789272064)
    bot.schoolleveltwo = discord.utils.get(vkgGuild.channels, id=918438831911473162)
    bot.schoollevelone = discord.utils.get(vkgGuild.channels, id=918438851284959253)
    bot.office = discord.utils.get(vkgGuild.channels, id=875541514598645780)
    bot.officelevelthree = discord.utils.get(vkgGuild.channels, id=918438248638984193)
    bot.officeleveltwo = discord.utils.get(vkgGuild.channels, id=918438230012076032)
    bot.officelevelone = discord.utils.get(vkgGuild.channels, id=918438337826660362)

load_dotenv()
bot.run(os.getenv('TOKEN'))