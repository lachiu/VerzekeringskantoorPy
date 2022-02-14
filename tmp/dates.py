import os
import html
import discord
import mysql.connector
import datetime
from dotenv.main import load_dotenv
from discord.ext import commands
from general_bot import bot_speaks
from permissions import check_perms

class dates(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['date-see'])
    async def _dates_see_command(self, ctx, arg1: str):
        if check_perms('basic', ctx.author):
            load_dotenv()
            mydb = mysql.connector.connect(
                host=os.getenv('DB_SERVERNAME'),
                user=os.getenv('DB_USERNAME'),
                password=os.getenv('DB_PASSWORD'),
                database=os.getenv('DB_NAME')
            )
            mycursor = mydb.cursor()
            mycursor.execute(f"SELECT * FROM `tbl_brands` WHERE `name` = '{html.escape(arg1)}';")
            myresult = mycursor.fetchall()
            id_value = myresult[0][0]
            name_value = myresult[0][1]
            gname_value = myresult[0][2]
            description_value = myresult[0][3]

            link = arg1.replace(' ', '%20')

            embed=discord.Embed(title=arg1.upper(), url=f'https://acg.groningenrp.xyz/products_page.php?brand={link}', color=0xff0000)
            embed.add_field(name='id', value=id_value, inline=False)
            embed.add_field(name='name', value=name_value, inline=False)
            
            if gname_value != None:
                embed.add_field(name='gname', value=gname_value, inline=False)

            embed.add_field(name='description', value=description_value, inline=False)
            embed.set_footer(text=self.bot.user.name)
            await ctx.send(embed=embed)


    @commands.command(aliases=['date-fix'])
    async def _dates_add_fix(self, ctx):
        if check_perms('dev', ctx.author):
            enabled = False
            if (enabled):
                load_dotenv()
                mydb = mysql.connector.connect(
                    host=os.getenv('DB_SERVERNAME'),
                    user=os.getenv('DB_USERNAME'),
                    password=os.getenv('DB_PASSWORD'),
                    database=os.getenv('DB_NAME')
                )

                mycursor = mydb.cursor()
                await ctx.send("Ik begin.")
                start_date = datetime.date(2021, 1, 1)
                end_date = datetime.date(2021, 10, 7)
                delta = datetime.timedelta(days=1)

                while start_date <= end_date:
                    qry = "INSERT INTO `tbl_dates`(`id`, `date`) VALUES (null, %s);"
                    mycursor.execute(qry, (start_date,))
                    start_date += delta

                mydb.commit()
                await ctx.send("Ik ben klaar.")
            
def setup(bot):
    bot.add_cog(dates(bot))