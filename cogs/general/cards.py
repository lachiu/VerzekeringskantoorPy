import yaml
import logs
import discord
import settings
import mysql.connector
import general
from discord.ext import commands
from dotenv.main import load_dotenv
from general_bot import bot_speaks

class cards(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['kaart'])
    async def card(self, ctx, type = None):
        dict_ = {
            "url": "",
            "title": "Verzekerings Kantoor Groningen",
            "description": f"",
            "author": "",
            "items": {}
        }

        if general.check_perms('basic', ctx.author):
            if general.isTicket(ctx.channel.category_id):
                await ctx.message.delete()
                validType = False
                if type == "ba":
                    # Burgerlijke aansprakelijkheid
                    dict_["description"] = "Deze verzekering vergoed de andere partij aan materiële schade en medische kosten.\
                        \nSchade aan je eigen voertuig word niet vergoed."                    
                    validType = True

                elif type == "omnium":
                    # Omnium of full omnium
                    dict_["description"] = "Deze verzekering vergoed schade aan uw eigen voertuig.\
                        \nNiet aan anderen. Full omnium dekt RwS- en takelkosten."                    
                    validType = True

                elif type == "hv":
                    # Handelsverzekering
                    dict_["description"] = "Deze verzekering is uitsluitend voor officiele bedrijven,\
                        dus zij met een KvK nummer van de gemeente.\
                        \nDit is een verzekering die geldt per 3 voertuigen per persoon werkzaam bij een officieel bedrijf.\
                        \nDeze verzekering levert BA en omnium."                    
                    validType = True

                elif type == "zv":
                    # Zorgverzekering
                    dict_["description"] = "Deze verzekering dekt uitsluitend de kosten gemaakt in een \
                        zorginstelling/ziekenhuis. Materiële schade word hiermee niet vergoed."                    
                    validType = True

                elif type == "vw" or type == "voorwaarden":
                    # Voorwaarden
                    schadebetalen = "Schade die veroorzaakt word door volgende gevallen word niet vergoed:\
                    \n- indien u voor de wegen en verkeerswetgeving strafbaar bent:\
                    \n-- 0.2 promille bij jonge bestuurder, 0.5 bij ervaren bestuurder\
                    \n-- onder invloed van andere verboden middelen\
                    \n-- gevaarlijk rijgedrag\
                    \n-- schade ten gevolge van vluchtmisdrijf\
                    \n-- rijden zonder geldig rijbewijs\
                    \n-- rijden zonder geldig kenteken\
                    \n- opzettelijk veroorzaakte schade\
                    \n- gemaakt door jouw voertuig ten gevolge van:\
                    \n-- het onbeheerd achterlaten op de openbare weg \
                    \n-- achterlaten op een openbare plaats terwijl die niet slotvast is\
                    \n-- de sleutels in enige nabijheid te bewaren"
                    type = "voorwaarden"
                    dict_["description"] += schadebetalen
                    validType = True

                elif type == "vv" or type == "voertuigen":
                    dict_["items"] = {
                        "Lichte Motor": "bv.: Vespa",
                        "Zware Motor": "bv.: Kawasaki ZX10",
                        "Oldtimer": "bv.: Volkswagen Type 262",
                        "Lichte Vracht": "bv.: Ford Speedo",
                        "Personenwagen": "bv.: Peugeot 206",
                        "Vrachtwagen": "bv.: Brabus 6x6",
                        "Supercar": "bv.: Nissan GTR",
                        "Lichte Boot": "bv.: Jetski",
                        "Zware Boot": "bv.: Longfin",
                        "Helicopter": "bv.: Swift",
                        "Vliegtuig": "bv.: Miljet"
                    }                
                    validType = True

                else:
                    dict_["description"] = "De mogelijke keuzes zijn:"     
                    dict_["items"] = {
                        "Burgerlijke aansprakelijkheid.\nVoor auto of persoon": "ba",
                        "Omnium of Full omnium": "omnium",
                        "Handelsverzekering": "hv",
                        "Zorgverzekering": "zv",
                        "Voorwaarden": "vw",
                        "Voertuigen": "vv"
                    }
                
                    embed = await logs.return_embed(dict_)
                    await ctx.send(embed=embed, delete_after=60)
                    
                if validType:
                    dict_["title"] = dict_["title"] + f" | {type.upper()}"
                    await logs.make_embed(self, ctx, dict_)                                                                
            else:
                await ctx.send(f"{ctx.author.mention}, u dient dit command uit te voeren in een ticket.", delete_after=10)

async def setup(bot):
    await bot.add_cog(cards(bot))