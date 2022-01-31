import os
import discord
import general
import mysql.connector
from datetime import datetime
from dotenv.main import load_dotenv
from general_bot import bot_speaks

def make_log(log_dict):
    load_dotenv()
    mydb = mysql.connector.connect(
        host=os.getenv('DB_SERVERNAME'),
        user=os.getenv('DB_USERNAME'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME')
    )
    
    mycursor = mydb.cursor()
    sql = "INSERT INTO `tbl_discord_logs` (`id`, `mod`, `user`, `reason`, `unixtime`, `type`) VALUES (NULL, %s, %s, %s, %s, %s);"
    mycursor.execute(sql, (log_dict['mod'], log_dict['user'], log_dict['reason'], log_dict['unixtime'], log_dict['type']))
    mydb.commit()

async def make_discord_log(self, ctx, log_dict):
    home = "http://vkg.groningenrp.xyz"
    type = ""
    description = ""
    member = discord.utils.get(ctx.guild.members, id=log_dict['user'])
    mod = discord.utils.get(ctx.guild.members, id=log_dict['mod'])

    if log_dict['type'] == 0:
        type = "Warn gelogd"
        description = f"{member.mention} werd gewaarschuwd voor: {log_dict['reason']} door {mod.mention}"
        log_dict['perms'] = "administrative"
    elif log_dict['type'] == 1:
        type = "Kick gelogd"
        description = f"{member.mention} werd gekickt voor: {log_dict['reason']} door {mod.mention}"
        log_dict['perms'] = "administrative"
    elif log_dict['type'] == 2:
        type = "Ban gelogd"
        description = f"{member.mention} werd geband voor: {log_dict['reason']} door {mod.mention}"
        log_dict['perms'] = "administrative"
    elif log_dict['type'] == 3:
        type = "Unban gelogd"
        description = f"{member.mention} werd geunband voor: {log_dict['reason']} door {mod.mention}"
        log_dict['perms'] = "administrative"
    elif log_dict['type'] == 4:
        type = "Ticket werd gesloten"
        description = f"{member.mention} werd gesloten door {mod.mention}."
        log_dict['perms'] = "tickets"
    elif log_dict['type'] == 5:
        type = "Ticket werd geclaimt"
        description = f"{member.mention} werd geclaimd door {mod.mention}."
        log_dict['perms'] = "tickets"
    elif log_dict['type'] == 6:
        type = "Survey opgevangen"
        description = f"{log_dict['reason']}"
        log_dict['perms'] = "tickets"
    elif log_dict['type'] == 7:
        type = "Nieuwe klant"
        description = f"{log_dict['reason']}"
        log_dict['perms'] = "basic"
    elif log_dict['type'] == 8:
        type = "Wijziging klant"
        description = f"{log_dict['reason']}"
        log_dict['perms'] = "basic"
    elif log_dict['type'] == 9:
        type = "Wijziging kluis"
        description = f"{log_dict['reason']}"
        log_dict['perms'] = "kluis"
    elif log_dict['type'] == 10:
        type = "Wijziging kluis"
        description = f"{log_dict['reason']}"
        log_dict['perms'] = "repairkits"

    value = datetime.fromtimestamp(log_dict['unixtime'])
    embed = discord.Embed(title=type, description=description, url=home, color=0xff0000)
    embed.set_author(name="Verzekerings Kantoor Groningen")
    embed.set_footer(text=f'{self.bot.user.name} - {value:%d-%m-%y %H:%M:%S}')

    if "items" in log_dict:
        for k,v in log_dict['items'].items():
            embed.add_field(name=k, value=v, inline=False)

    channel = discord.utils.get(ctx.guild.channels, id=general.return_log_channel_id(log_dict['perms']))
    await channel.send(embed=embed)

async def make_embed(self, ctx, dict_):
    home = "http://vkg.groningenrp.xyz"
    
    if not dict_['url'] == None and not dict_['url'] == "":
        url = f"http://vkg.groningenrp.xyz/{dict_['url']}"
    else:
        url = home

    if not dict_['title'] == None and not dict_['title'] == "":
        title = dict_['title']
    else:
        title = "Verzekerings Kantoor Groningen"

    if not dict_['description'] == None and not dict_['description'] == "":
        description = dict_['description']
    else:
        description = ""

    embed=discord.Embed(title=f'{title}', description=f'{description}', url=url, color=0xff0000)

    if dict_['items'].items():
        for k,v in dict_['items'].items():
            embed.add_field(name=k, value=v, inline=False)

    embed.set_footer(text=self.bot.user.name)
    await ctx.send(embed=embed)

async def return_embed(dict_, color=0x1E90FF):
    home = "http://vkg.groningenrp.xyz"
    
    if not dict_['url'] == None and not dict_['url'] == "":
        url = f"http://vkg.groningenrp.xyz/{dict_['url']}"
    else:
        url = home
        
    if not dict_['title'] == None and not dict_['title'] == "":
        title = dict_['title']
    else:
        title = "Verzekerings Kantoor Groningen"
        
    if not dict_['description'] == None and not dict_['description'] == "":
        description = dict_['description']
    else:
        description = ""
        
    embed=discord.Embed(title=f'{title}', description=f'{description}', url=url, color=color)
    
    if dict_['items'].items():
        for k,v in dict_['items'].items():
            embed.add_field(name=k, value=v, inline=False)
        
    embed.set_footer(text="Sofia Sarafian")
    return embed

async def pm(self, ctx, user_id: int, embed):
    user = self.bot.get_user(user_id) or (await self.bot.fetch_user(user_id))
    try:
        await user.send(embed=embed)
    except:
        bot_speaks(self.bot, f'Could not PM user by ID {user_id}.')