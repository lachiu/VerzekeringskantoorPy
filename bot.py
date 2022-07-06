import os
import discord
import mysql.connector
from cogs.db.tickets import ChannelButton
from logs import return_embed
from general_bot import bot_speaks
from dotenv.main import load_dotenv
from discord.ext import commands

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
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
            cogs[item[:-3]] = f"cogs.{subdir}.{item[:-3]}"

@bot.event
async def on_ready():
    #print(f"Inhoud van cogs: {cogs}")
    for key, item in cogs.items():
        #print(f"{key} - {item}")
        await bot.load_extension(item)

    vkgGuild = bot.get_guild(875098573262438420)
    bot.coglist = cogs
    bot.boss = vkgGuild.get_member(154244184587501568)
    bot.alertchannel = vkgGuild.get_channel(934615600263749663)
    bot.leveltwochannel = vkgGuild.get_channel(934644216259293184)
    bot.announcementchannel = vkgGuild.get_channel(918435465395314718)
    bot.ruleschannel =  vkgGuild.get_channel(918439427221635123)
    bot.ticketchannel = vkgGuild.get_channel(918435738662629386)
    bot.frontdoor = vkgGuild.get_channel(875098573547646991)
    bot.schooldocs = vkgGuild.get_channel(918438986719039518)
    bot.schoollevelthree = vkgGuild.get_channel(918438817789272064)
    bot.schoolleveltwo = vkgGuild.get_channel(918438831911473162)
    bot.schoollevelone = vkgGuild.get_channel(918438851284959253)
    bot.schoolemw = vkgGuild.get_channel(938242636572147723)
    bot.office = vkgGuild.get_channel(875541514598645780)
    bot.officelevelthree = vkgGuild.get_channel(918438248638984193)
    bot.officeleveltwo = vkgGuild.get_channel(918438230012076032)
    bot.officelevelone = vkgGuild.get_channel(918438337826660362)
    bot.administrativelog = vkgGuild.get_channel(932143290621505596)
    bot.devrole = vkgGuild.get_role(862078083586457630)   
    bot.jmrole = vkgGuild.get_role(875098573262438425)
    bot.directorrole = vkgGuild.get_role(875098573262438424)
    bot.superrole = vkgGuild.get_role(918434947247788063)
    bot.managerrole = vkgGuild.get_role(875098573262438423)
    bot.agentrole = vkgGuild.get_role(875098573262438422)
    bot.clientrole = vkgGuild.get_role(918435180778258464)
    bot.emwleidingrole = vkgGuild.get_role(991041772429934602)
    bot.emwrole = vkgGuild.get_role(938233602410434630)
    bot.mutedrole = vkgGuild.get_role(934945936185122876)    
    bot.anwbrole = vkgGuild.get_role(952837567387164693)
    bot.politierole = vkgGuild.get_role(952837478480506900)
    bot.amburole = vkgGuild.get_role(952837530473078785)
    bot.acgrole = vkgGuild.get_role(952837400718114816)
    bot.as24role = vkgGuild.get_role(952837605945389066)
    bot.pcarsrole = vkgGuild.get_role(952837653198430208)
    bot.vsgrole = vkgGuild.get_role(952857453723275264)
    bot.jjrole = vkgGuild.get_role(953562057066819585)
    bot.schoolannouncementchannel = vkgGuild.get_channel(989738970684457022)
    bot.insurancetypes = None
    bot.insurabletypes = None
    bot.categories = None
    bot.subcategories = None

    bot.x = False
    if not bot.x:
        bot.add_view(ChannelButton(bot))
        bot.x = True
    
    bot_speaks(bot, f'Ik ben helemaal klaar om aan de slag te gaan als {bot.user.name}.')

load_dotenv()
bot.run(os.getenv('TOKEN'))