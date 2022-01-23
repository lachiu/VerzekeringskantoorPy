import os
import html
import discord
import mysql.connector
from dotenv.main import load_dotenv
from discord.ext import commands
from general_bot import bot_speaks
#from permissions import check_perms

def check_perms():
    pass

class brands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['merk-add'])
    async def _brand_add_command(self, ctx, arg1: str, arg2: str):
        if check_perms('administrative', ctx):
            load_dotenv()
            mydb = mysql.connector.connect(
                host=os.getenv('DB_SERVERNAME'),
                user=os.getenv('DB_USERNAME'),
                password=os.getenv('DB_PASSWORD'),
                database=os.getenv('DB_NAME')
            )

            mycursor = mydb.cursor()
            sql = "INSERT INTO `tbl_brands`(`id`, `name`, `special`, `description`) VALUES (NULL,%s,NULL,%s);"
            val = (html.escape(arg1), html.escape(arg2))
            mycursor.execute(sql, val)
            mydb.commit()
            await ctx.send(f'{ctx.author.mention}, u heeft succesvul een nieuwe rij toegevoegd voor {arg1} met als beschrijving {arg2}')
            bot_speaks(self.bot, f'{ctx.author} heeft een nieuwe rij toegevoegd voor {arg1}')
        else:
            await ctx.send(f'{ctx.author.mention}, u bezit helaas niet over de permissies om een nieuw merk toe te voegen.\nGelieve contact op te nemen met de ACG manager of directeur indien u van mening bent dat dit een fout is.', delete_after=5)

    @commands.command(aliases=['merk-edit'])
    async def _brand_edit_command(self, ctx, var, arg1: str, arg2: str):
        if check_perms('administrative', ctx):
            load_dotenv()
            mydb = mysql.connector.connect(
                host=os.getenv('DB_SERVERNAME'),
                user=os.getenv('DB_USERNAME'),
                password=os.getenv('DB_PASSWORD'),
                database=os.getenv('DB_NAME')
            )

            mycursor = mydb.cursor()
            val = (html.escape(arg1), html.escape(arg2), html.escape(var))
            if isinstance(var, str):
                sql = f"UPDATE `tbl_brands` SET `{html.escape(arg1)}`='{html.escape(arg2)}' WHERE `name` = '{html.escape(var)}';"
            elif isinstance(var, int):
                sql = f"UPDATE `tbl_brands` SET `{html.escape(arg1)}`='{html.escape(arg2)}' WHERE `id` = '{html.escape(var)}';"

            mycursor.execute(sql)
            mydb.commit()
            await ctx.send(f'{ctx.author.mention}, u heeft succesvol de {arg1} van {var.upper()} aangepast naar {arg2}.')
            bot_speaks(self.bot, f'{ctx.author} heeft de {arg1} van {var} aangepast naar {arg2}.')
        else:
            await ctx.send(f'{ctx.author.mention}, u bezit helaas niet over de permissies om dit merk aan te passen.\nGelieve contact op te nemen met de ACG manager of directeur indien u van mening bent dat dit een fout is.', delete_after=5)

    @commands.command(aliases=['merk-see'])
    async def _brand_see_command(self, ctx, arg1: str):
        if check_perms('basic', ctx):
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
            special_value = myresult[0][2]
            description_value = myresult[0][3]

            link = arg1.replace(' ', '%20')

            embed=discord.Embed(title=arg1.upper(), url=f'https://acg.groningenrp.xyz/products_page.php?brand={link}', color=0xff0000)
            embed.add_field(name='id', value=id_value, inline=False)
            embed.add_field(name='name', value=name_value, inline=False)
            
            if special_value != None:
                embed.add_field(name='Goede naam', value=special_value, inline=False)

            embed.add_field(name='description', value=description_value, inline=False)
            embed.set_footer(text=self.bot.user.name)
            await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(brands(bot))