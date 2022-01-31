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
        if general.check_perms('basic', ctx):
            if general.isTicket(ctx.channel.category_id):
                dict_ = {
                    "url": "",
                    "title": "",
                    "description": f"",
                    "author": "",
                    "items": {}
                }
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
            
                dict_["title"] = "Verzekerings Kantoor Groningen"
                if type == None:                    
                    dict_["description"] = "De mogelijke keuzes zijn:"
                    dict_["items"] = {
                        "ba": "Burgerlijke aansprakelijkheid.\nVoor auto of persoon",
                        "omnium": "Omnium of Full omnium",
                        "hv": "Handelsverzekering",
                        "zv": "Zorgverzekering"
                    }

                    embed = await logs.return_embed(dict_)
                    await ctx.send(embed=embed, delete_after=60)
                else:
                    dict_["title"] = dict_["title"] + f" | {type.upper()}"
                    if type == "ba":
                        # Burgerlijke aansprakelijkheid
                        dict_["description"] = "Deze verzekering is wettelijk verplicht, \
                            deze vergoed het slachtoffer aan materiële schade.\
                            \nHeeft u overigens nodig voor zowel u als persoon als uw voertuig(en).\
                            \nSchade aan je eigen voertuig word niet vergoed via jouw eigen BA verzekering.\
                            \n\nEr zijn wel enkele uitzonderingen."

                    elif type == "omnium":
                        # Omnium of full omnium
                        dict_["description"] = "Deze verzekering vergoed schade aan uw eigen voertuig.\
                            \nNiet aan anderen. Full omnium dekt ook stormschade.\
                            \n\nEr zijn wel enkele uitzonderingen."

                    elif type == "hv":
                        # Handelsverzekering
                        dict_["description"] = "Deze verzekering is uitsluitend voor officiele bedrijven,\
                            dus zij met een KvK nummer van de gemeente.\
                            \nDit is een verzekering die automatisch geldt voor alle voertuigen van dat bedrijf.\
                            \nDeze verzekering levert BA en omnium.\
                            \n\nEr zijn wel enkele uitzonderingen."

                    elif type == "zv":
                        # Zorgverzekering
                        dict_["description"] = "Deze verzekering dekt uitsluitend de kosten gemaakt in een \
                            zorginstelling/ziekenhuis. Materiële schade word hiermee niet vergoed.\
                            \n\nEr zijn wel enkele uitzonderingen."

                    dict_["description"] = dict_["description"] + "\n" + schadebetalen
                    await logs.make_embed(self, ctx, dict_)
            else:
                await ctx.send(f"{ctx.author.mention}, u dient dit command uit te voeren in een ticket.", delete_after=10)

def setup(bot):
    bot.add_cog(cards(bot))