import os
import random
import discord
import datetime
from cogs.functions import returnMember
import general
import mysql.connector
from typing import List
from dateutil.parser import parse
from dotenv.main import load_dotenv
from discord.ext import commands

from logs import return_embed

class fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def tic(self, ctx):
        if general.check_perms('dev', ctx.author):
            discordTarget = await returnMember(ctx, str(704034646421405725))
            dmchannel = await discordTarget.create_dm()

            dict_ = {
                "url": "",
                "title": "De kopijen",
                "description": f"Beste klant\n\
                    \nNogmaals hartelijk bedankt voor uw aankoop.\
                    \nDe collega had mij vermeld dat ik deze documenten aan u moest doormailen.\
                    \n\nMocht er iets ontbreken, graag onmiddellijk contact opnemen met ons via het gekende systeem.\
                    \n\nMet vriendelijke groeten,\
                    \nSofia Sarafian\
                    \nSecretaresse VKG",
                "author": "",
                "items": {}
            }

            embed = await return_embed(dict_)

            await dmchannel.send(embed=embed)
            await dmchannel.send(files=[discord.File("pdf/factuur_vkg_fomsuper06072242207.pdf", "factuur_vkg_fomsuper06072242207.pdf"), discord.File("pdf/voorwaarden.pdf", "voorwaarden.pdf")])
            
        
async def setup(bot):
    await bot.add_cog(fun(bot))