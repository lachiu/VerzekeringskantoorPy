import os
import time
import signal
import typing
import discord
import general
import mysql.connector
from cogs.db.tickets import ChannelButton
from logs import return_embed
from logs import make_embed
from logs import make_log
from logs import make_discord_log
from dotenv.main import load_dotenv
from discord.ext import commands
from general_bot import bot_speaks
import pdf_generation

class administration(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        dict_ = {
            "url": "",
            "title": "Welkom bij VKG",
            "description": f"Beste {member.mention},\n\
                \n\
                Van harte welkom!\
                \nIndien u contact met ons wenst op te nemen kan u dat doen \
                via ons ticketsysteem, die vind u terug in \
                {self.bot.ticketchannel.mention} nadat u akkoord bent gegaan \
                met de {self.bot.ruleschannel.mention}.\
                \n\
                \n\
                Met vriendelijke groeten,\
                \n{self.bot.user.mention}\
                \nSecretaresse",
            "author": "",
            "items": {}
        }
        embed = await return_embed(dict_, color=0xffffff)
        message = await self.bot.frontdoor.send(embed=embed)
        await message.add_reaction('👋')

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        rolegivermessageid = int(general.open_yaml("rolegiver"))
        if rolegivermessageid == payload.message_id and not payload.user_id == self.bot.user.id:
            if str(payload.emoji) == '👌':
                message = await self.bot.ruleschannel.fetch_message(payload.message_id)
                vkgGuild = self.bot.get_guild(875098573262438420)
                role = vkgGuild.get_role(general.return_role_id("klant"))
                await payload.member.add_roles(role)
                await message.clear_reactions()
                await message.add_reaction('👌')

    @commands.command()
    async def setuprules(self, ctx):
        await ctx.message.delete()
        if general.check_perms('dev', ctx.author):
            vkgGuild = self.bot.get_guild(875098573262438420)
            await self.bot.ruleschannel.purge(limit=10, bulk=False)
            jobmanagers = discord.utils.get(vkgGuild.roles, id=general.return_role_id("groningse inspectie"))
            dict_ = {
                "url": "",
                "title": "Algemeen | Lid 1",
                "description": f"Hieronder vind u de regels die ten alle tijden gelden in deze Discord server.\
                    \nDeze server word uitsluitend beheerd door {self.bot.boss.mention}.\
                    \nDe {jobmanagers.mention} zijn ook aanwezig waar u, indien nodig ook naartoe kan.\
                    \n\
                    \nNa het behandeld hebben van uw ticket \
                    ([die vind u hier overigens terug](https://discord.com/channels/875098573262438420/918435738662629386)) \
                    vragen wij u om deel te nemen aan een review.\
                    \nDeze word, na beoordeling op spelling en grof taalgebruik, toegevoegd en getoond op onze site.",
                "author": "",
                "items": {}
            }
                
            embed = await return_embed(dict_)
            await self.bot.ruleschannel.send(embed=embed)

            dict_ = {
                "url": "",
                "title": "Algemeen | Lid 2",
                "description": f"{self.bot.user.mention} is onze secretaresse. Deze, en overigens onze andere \
                    medewerkers ook, dient u altijd met respect te benaderen.\
                    \nGebeurd dat niet? Dan kunnen wij sancties opleggen:\
                    \n- Waarschuwing\
                    \n- Mute\
                    \n- Kick\
                    \n- Ban\
                    \n- Sancties vanuit de gemeente\
                    \n- Blacklist\
                    \n\
                    \nIk hoop dat ik dat maar 1 keer hoef te herhalen.\
                    \nAls we ons allen aan deze regels kunnen houden komt het goed.",
                "author": "",
                "items": {}
            }
                
            embed = await return_embed(dict_)
            await self.bot.ruleschannel.send(embed=embed)

            dict_ = {
                "url": "",
                "title": "Regel 1",
                "description": f"Het is niet toegestaan om medewerkers te gaan PM'en of \
                    een vriendschapsverzoek te sturen of te bellen.",
                "author": "",
                "items": {}
            }
                
            embed = await return_embed(dict_)
            await self.bot.ruleschannel.send(embed=embed)

            dict_ = {
                "url": "",
                "title": "Regel 2",
                "description": f"Het bespreken van strafmaatregelen tegen andere klanten dient \
                    te geschieden in een ticket, bij voorkeur, of de algemene Discord.\
                    \n\
                    \nStaff lastigvallen om hier dingen geregeld te krijgen heeft ook geen effect.",
                "author": "",
                "items": {}
            }
                
            embed = await return_embed(dict_)
            await self.bot.ruleschannel.send(embed=embed)

            dict_ = {
                "url": "",
                "title": "Regel 3",
                "description": f"Taalgebruik verder dient te gebeuren met al het mogelijke respect voor anderen.\
                    \nMet ziektes schelden, het n-woord of andere discriminerende uitspraken \
                    zijn hier ook niet welkom.",
                "author": "",
                "items": {}
            }
                
            embed = await return_embed(dict_)
            await self.bot.ruleschannel.send(embed=embed)

            dict_ = {
                "url": "",
                "title": "Regel 4",
                "description": f"Het is niet toegestaan om zinloze tickets te openen, \
                    te spammen (meerdere berichten, caps, emojis).",
                "author": "",
                "items": {}
            }
                
            embed = await return_embed(dict_)
            await self.bot.ruleschannel.send(embed=embed)

            dict_ = {
                "url": "",
                "title": "Regel 5",
                "description": f"Mocht het nog niet duidelijk zijn, het is dus de bedoeling \
                    dat u ten allen tijden met respect praat t.o.v. anderen.\
                    \nHet maakt niet uit of het een medewerker, vriend, burger of stafflid is.\
                    \n\
                    \nDe communicatie hier gebeurt strikt professioneel.",
                "author": "",
                "items": {}
            }
                
            embed = await return_embed(dict_)
            await self.bot.ruleschannel.send(embed=embed)

            dict_ = {
                "url": "",
                "title": "Regel 6",
                "description": f"Roddels of onwaarheden verspreiden (lees eerroof of laster) zal \
                    met harde hand op gereageerd worden (in RP).\
                    \n\
                    \nFouten kunnen gebeuren, dat is nu eenmaal menselijk.\
                    \nWe doen ons uiterste best om daar een compromis als oplossing in te bekomen, \
                    indien mogelijk.\
                    \nOnze excuses mocht dat bij u plaats vinden/hebben gevonden.\
                    \nWij streven naar professionaliteit en voortbrengen van een nieuwe RP in Grp.",
                "author": "",
                "items": {}
            }
                
            embed = await return_embed(dict_)
            await self.bot.ruleschannel.send(embed=embed)

            dict_ = {
                "url": "",
                "title": "Regel 7",
                "description": f"Alle communicatie op dit kanaal na, gebeurt IC.\
                    \nDiscord word hulpcentrum/contactformulier.\
                    \nOverige termen lijken ons vanzelfsprekend.\
                    \nHet is dus ten strengste verboden om IC en OOC door elkaar te halen.\
                    \nHier zal streng op worden toegekeken.",
                "author": "",
                "items": {}
            }
                
            embed = await return_embed(dict_)
            await self.bot.ruleschannel.send(embed=embed)

            dict_ = {
                "url": "",
                "title": "Overeenkomst",
                "description": f"Indien u akkoord bent met deze regels en onze manier van werken \
                    klikt u vervolgens op de emoji hieronder.",
                "author": "",
                "items": {}
            }

            embed = await return_embed(dict_)
            message = await self.bot.ruleschannel.send(embed=embed)
            await message.add_reaction('👌')
            general.write_yaml("rolegiver", message.id)

    @commands.command()
    async def setupbutton(self, ctx):
        await ctx.message.delete()
        if general.check_perms('dev', ctx.author):
            dict_ = {
                "url": "",
                "title": "Verzekerings Kantoor Groningen - Supportcentrum",
                "description": "Klik hieronder op een van de knoppen om de juiste hulp te krijgen.",
                "author": "",
                "items": {}
            }

            embed = await return_embed(dict_, color=0xfc0303)
            await self.bot.ticketchannel.send(embed=embed, view=ChannelButton(self.bot))

    @commands.command()
    async def setupschoolmessages(self, ctx):
        await ctx.message.delete()
        if general.check_perms('dev', ctx.author):
            # Eerst de kanalen purgen.
            await self.bot.schooldocs.purge(limit=10, bulk=False)
            await self.bot.schoollevelthree.purge(limit=10, bulk=False)
            await self.bot.schoolleveltwo.purge(limit=10, bulk=False)
            await self.bot.schoollevelone.purge(limit=10, bulk=False)
            
            # Document channel
            # self.bot.schooldocs
            # ======================================= #
            dict_ = {
                "url": "",
                "title": "De klantcommands",
                "description": f"__**!klant:**__\
                    \n**nieuw** (add, new, toevoegen)\
                    \n*Optionele parameters:*\
                    \nFivem licentie (of 'geen'/'leeg'),\
                    \nDiscord id (tag, id of 'leeg'),\
                    \nVoornaam (in rp),\
                    \nAchternaam (in rp),\
                    \nGeboortedatum (in rp),\
                    \nRijbewijs A (0 of 1),\
                    \nRijbewijs B (0 of 1),\
                    \nRijbewijs C (0 of 1),\
                    \nVliegbrevet (0 of 1),\
                    \nVaarbewijs (0 of 1)\
                    \n\
                    \n**edit** (aanpassen, pasaan, verander)\
                    \n*Optionele parameters:*\
                    \nDiscord id (tag, id of 'leeg'),\
                    \nKeuze (een van bovenstaande gegevens of 'geen'),\
                    \nNieuwe waarde (moet voldoen aan de vereiste van hierboven)\
                    \n\
                    \n**zie** (bekijken, see)\
                    \n*Optionele parameters:*\
                    \nDiscord id (tag, id of 'leeg')",
                "author": "",
                "items": {}
            }

            embed = await return_embed(dict_, color=0xffffff)
            await self.bot.schooldocs.send(embed=embed)

            dict_ = {
                "url": "",
                "title": "De werknemercommands",
                "description": f"__**!werknemer:**__\
                    \n**nieuw** (add, new, toevoegen)\
                    \n*Optionele parameters:*\
                    \nFivem licentie (of 'geen'/'leeg'),\
                    \nDiscord id (tag, id of 'leeg'),\
                    \nVoornaam (in rp),\
                    \nAchternaam (in rp),\
                    \nWachtwoord ('geen'),\
                    \nGeboortedatum (in rp),\
                    \nIngeschakeld (1)\
                    \n\
                    \n**edit** (aanpassen, pasaan, verander)\
                    \n*Optionele parameters:*\
                    \nDiscord id (tag, id of 'leeg'),\
                    \nKeuze (een van bovenstaande gegevens of 'geen'),\
                    \nNieuwe waarde (moet voldoen aan de vereiste van hierboven)\
                    \n\
                    \n**zie** (bekijken, see)\
                    \n*Optionele parameters:*\
                    \nDiscord id (tag, id of 'leeg')",
                "author": "",
                "items": {}
            }

            embed = await return_embed(dict_, color=0xffffff)
            await self.bot.schooldocs.send(embed=embed)

            dict_ = {
                "url": "",
                "title": "De verzekercommands", # kloppen nog niet
                "description": f"__**!werknemer:**__\
                    \n**nieuw** (add, new, toevoegen)\
                    \n*Optionele parameters:*\
                    \nFivem licentie (of 'geen'/'leeg'),\
                    \nDiscord id (tag, id of 'leeg'),\
                    \nVoornaam (in rp),\
                    \nAchternaam (in rp),\
                    \nWachtwoord ('geen'),\
                    \nGeboortedatum (in rp),\
                    \nIngeschakeld (1)\
                    \n\
                    \n**edit** (aanpassen, pasaan, verander)\
                    \n*Optionele parameters:*\
                    \nDiscord id (tag, id of 'leeg'),\
                    \nKeuze (een van bovenstaande gegevens of 'geen'),\
                    \nNieuwe waarde (moet voldoen aan de vereiste van hierboven)\
                    \n\
                    \n**zie** (bekijken, see)\
                    \n*Optionele parameters:*\
                    \nDiscord id (tag, id of 'leeg')",
                "author": "",
                "items": {}
            }

            embed = await return_embed(dict_, color=0xffffff)
            await self.bot.schooldocs.send(embed=embed)

            dict_ = {
                "url": "",
                "title": "Algemene commands",
                "description": f"__**!kaart:**__\
                    *Laat een bericht zien met uitleg over elk verzekeringstype.\
                    *Mogelijke opties zijn **ba**, **omnium**, **hv** en **zv**.*\
                    \n\
                    \n__**!geef**__\
                    \nRol (tag, id)\
                    \n\
                    \n__**!neem**__\
                    \nRol (tag, id)\
                    \n\
                    \n__**!repairkit**__\
                    \n**neem** (take)\
                    \nHoeveelheid (aantal),\
                    \nReden (verplicht)\
                    \n\
                    \n**add** (voegtoe, toevoegen)\
                    \nHoeveelheid (aantal),\
                    \nReden (verplicht)\
                    \n\
                    \n**zie** (see, huidig, current)\
                    \n\
                    \n__**!kluis**__\
                    \n**neem** (take)\
                    \nHoeveelheid (aantal),\
                    \nReden (verplicht)\
                    \n\
                    \n**add** (voegtoe, toevoegen)\
                    \nHoeveelheid (aantal),\
                    \nReden (verplicht)\
                    \n\
                    \n**zie** (see, huidig, current)\
                    ",
                "author": "",
                "items": {}
            }

            embed = await return_embed(dict_, color=0xffffff)
            await self.bot.schooldocs.send(embed=embed)            

            dict_ = {
                "url": "",
                "title": "De verloningen",
                "description": f"**Per behandeld lvl-3 ticket: €1.500,00**,\
                    \n**Per behandeld lvl-2 ticket: €1.000,00**,\
                    \n**Per behandeld lvl-1 ticket: €500,00**,\
                    \n**Per aangeworven medewerker: €500,00**,\
                    \n**Per aangeworven klant: €500,00**,\
                    \n**Per verkochte verzekering: 10%**\
                    \n*Uitbetalingen gebeuren per week.*",
                "author": "",
                "items": {}
            }

            embed = await return_embed(dict_, color=0xffffff)
            await self.bot.schooldocs.send(embed=embed)

            # lvl-3 school channel
            # self.bot.schoollevelthree
            # ======================================= #
            dict_ = {
                "url": "",
                "title": "Welkom bij VKG",
                "description": f"Beste {self.bot.superrole.mention},\n\
                    \n\
                    Van harte welkom!\
                    \n\
                    \nVolgende zaken zitten in jouw takenpakket:\
                    \n**Klachten die geëscaleerd werden behandelen**,\
                    \n**Klachten m.b.t. jouw medewerkers behandelen**,\
                    \n**Managers opleiden**,\
                    \n**Overig lvl-2 takenpakket**\
                    \n\
                    \nDe verloningen:\
                    \n**Per behandeld lvl-3 ticket: €1.500,00**,\
                    \n**Per behandeld lvl-2 ticket: €1.000,00**,\
                    \n**Per behandeld lvl-1 ticket: €500,00**,\
                    \n**Per aangeworven medewerker: €500,00**,\
                    \n**Per aangeworven klant: €500,00**,\
                    \n**Per verkochte verzekering: 10%**\
                    \n*Uitbetalingen gebeuren per week.*\
                    \n\
                    \nMochten er klachten zijn kan je bij {self.bot.boss.mention} terecht \
                    \nof bij een {self.bot.jmrole.mention}.\
                    \n\
                    \nWe wensen jou veel succes met je nieuwe baan!\
                    \n\
                    Met vriendelijke groeten,\
                    \n{self.bot.user.mention}\
                    \nSecretaresse\
                    \n\
                    \n{self.bot.boss.mention}\
                    \n{self.bot.directorrole.mention}",
                "author": "",
                "items": {}
            }

            embed = await return_embed(dict_, color=0xffffff)
            await self.bot.schoollevelthree.send(embed=embed)

            # lvl-2 school channel
            # self.bot.schoolleveltwo
            # ======================================= #
            dict_ = {
                "url": "",
                "title": "Welkom bij VKG",
                "description": f"Beste {self.bot.managerrole.mention},\n\
                    \n\
                    Van harte welkom!\
                    \n\
                    \nVolgende zaken zitten in jouw takenpakket:\
                    \n**Wekelijks updaten van de supervisors**,\
                    \n**Klachten die geëscaleerd werden behandelen**,\
                    \n**Verzekeringsagenten opleiden**,\
                    \n**Overig lvl-1 takenpakket**\
                    \n\
                    \nDe verloningen:\
                    \n**Per behandeld lvl-2 ticket: €1.000,00**,\
                    \n**Per behandeld lvl-1 ticket: €500,00**,\
                    \n**Per aangeworven medewerker: €500,00**,\
                    \n**Per aangeworven klant: €500,00**,\
                    \n**Per verkochte verzekering: 10%**\
                    \n*Uitbetalingen gebeuren per week.*\
                    \n\
                    \nMochten er klachten zijn kan je bij {self.bot.superrole.mention}, {self.bot.boss.mention} \
                    \nof bij {self.bot.jmrole.mention} terecht.\
                    \n\
                    \nWe wensen jou veel succes met je nieuwe baan!\
                    \n\
                    Met vriendelijke groeten,\
                    \n{self.bot.user.mention}\
                    \nSecretaresse\
                    \n\
                    \n{self.bot.boss.mention}\
                    \n{self.bot.directorrole.mention}",
                "author": "",
                "items": {}
            }

            embed = await return_embed(dict_, color=0xffffff)
            await self.bot.schoolleveltwo.send(embed=embed)

            # Elevated ticket na schade toegewezen gekregen te hebben.
            dict_ = {
                "url": "",
                "title": "Schuld betwisten",
                "description": f"Dit is zowat het enige scenario dat ik me nu kan bedenken. \
                    Verder komen er uiteraard situaties bij die de verzekeringsagenten niet kunnen afhandelen.\
                    \n\
                    \nDe klant geeft aan dat die niet akkoord is met het besluit van de collega.\
                    Als het geen duidelijke zaak is, vraag je (in rp) naar een agent.",
                "author": "",
                "items": {}
            }

            embed = await return_embed(dict_, color=0xffffff)
            await self.bot.schoolleveltwo.send(embed=embed)

            # lvl-1 school channel
            # self.bot.schoollevelone
            # ======================================= #
            dict_ = {
                "url": "",
                "title": "Welkom bij VKG",
                "description": f"Beste {self.bot.agentrole.mention},\n\
                    \n\
                    Van harte welkom!\
                    \n\
                    \nVolgende zaken zitten in jouw takenpakket:\
                    \n**Wekelijks updaten van de managers**,\
                    \n**Verzekeringen verkopen**,\
                    \n**Aangiftes behandelen**,\
                    \n**Problemen verhelpen**,\
                    \n**Indien nodig, escaleer je de ticket.**\
                    \n\
                    \nDe verloningen:\
                    \n**Per behandeld lvl-1 ticket: €500,00**,\
                    \n**Per aangeworven medewerker: €500,00**,\
                    \n**Per aangeworven klant: €500,00**,\
                    \n**Per verkochte verzekering: 10%**\
                    \n*Uitbetalingen gebeuren per week.*\
                    \n\
                    \nMochten er klachten zijn kan je bij {self.bot.managerrole.mention}, {self.bot.boss.mention} terecht \
                    \nof bij een {self.bot.jmrole.mention}.\
                    \n\
                    \nWe wensen jou veel succes met je nieuwe baan!\
                    \n\
                    Met vriendelijke groeten,\
                    \n{self.bot.user.mention}\
                    \nSecretaresse\
                    \n\
                    \n{self.bot.boss.mention}\
                    \n{self.bot.directorrole.mention}",
                "author": "",
                "items": {}
            }

            embed = await return_embed(dict_, color=0xffffff)
            await self.bot.schoollevelone.send(embed=embed)
            
            dict_ = {
                "url": "",
                "title": "Nieuwe ticket",
                "description": f"Oke, er werd een ticket geopend. Rustig in- en uitademen.\
                    \nKlantvriendelijkheid staat voorop maar dat spreekt voor zich.\
                    \n\
                    \n__**Een (mogelijke) klant kan een ticket openen voor volgende zaken:**__\
                    \n**Een probleem**,\
                    \n**Een vraag**,\
                    \n**Een aankoop**,\
                    \n**Een ongeluk**\
                    \n\
                    \nEen vraag of probleem heeft iets te veel mogelijkheden om je daar \
                    nu al goed op voor te bereiden. Als je twijfelt of een probleem hebt \
                    kan je naar een manager vragen in {self.bot.officelevelone.mention}.\
                    Mocht het nodig zijn kan je een ticket verhogen naar lvl-2 met de ``!lift`` command.",
                "author": "",
                "items": {}
            }

            embed = await return_embed(dict_, color=0xffffff)
            await self.bot.schoollevelone.send(embed=embed)

            dict_ = {
                "url": "",
                "title": "Verkoop-ticket",
                "description": f"__**Een verkoop**__\
                    \nIndien het om een auto gaat check je eerst om wat voor voertuig het gaat. (evt. met een foto) \
                    Ook vraag je een foto van het kenteken ter bevestiging.\
                    \nBij een zorgverzekering of ba verzekering vraag je om een foto van de \
                    loonbrief (*F2-spier*). Dit mag de baan zijn die de laagste prijs verantwoord. \
                    (bijvoorbeeld klant is werkzaam bij de politie en doet uwv baantjes, dan mag die de verzekering als agent aanvragen)\
                    \nDe prijzen die je vind je terug in {self.bot.schooldocs.mention}.",
                "author": "",
                "items": {}
            }

            embed = await return_embed(dict_, color=0xffffff)
            await self.bot.schoollevelone.send(embed=embed)

            dict_ = {
                "url": "",
                "title": "Ongeluk-ticket",
                "description": f"__**Een ongeluk**__ *(houd er rekening mee dat de persoon mogelijk gestresseerd is)*\
                    \nVoor een geldige claim hebben we de gegevens nodig van:\
                    \n**De klant zelf**, via het rijbewijs, *(verifieer de klant)*,\
                    \n**Het voertuig en het kenteken**, *(verifieer met de polis via foto's)*,\
                    \n**De locatie**, *(foto van de locatie met GPS zichtbaar)*,\
                    \n**De schade**, *(a.d.h.v. een foto en dient overeen te komen met aangifte ANWB)*,\
                    \n**Vraag ook naar de roepnummer van de ANWB'er**, *(ter verificatie voor de aangifte van de ANWB'er)*,\
                    \n**Dezelfde gegevens van het andere voertuig en de chauffeur zoals de klant**, *(indien geen eenzijdig ongeval)*\
                    \n\
                    \nNu is het aan jou om te gaan kijken of er een E-MW (externe medewerker) aangifte heeft gedaan van de reparatie.\
                    \nIndien er na een week van het ongeluk nog geen aangifte is gebeurd komk het schadegeval te vervallen.\
                    \nIs er wel een aangifte gebeurd? Dan ga je kijken wie er in fout is. Jij geeft gewoon aan in je ticket wie er in fout is als volgt:\
                    \n\
                    \n```Beste\
                    \n\
                    \nWij hebben geconstateerd dat u (of 'de andere partij') in fout was.\
                    \n(indien de persoon zelf schuldig word bevonden) Hierbij willen wij u ook op de hoogte stellen van een verhoging van uw bonusmalus met 1 (voor uw genoemde producten, dus bijvoorbeeld) voor zowel uw BA verzekering als uw (full) omnium van uw (type) oldtimer met kenteken '00 AAA 0' met als reden (vul reden in).\
                    \n\
                    \nIk hoop u hiermee voldoende te hebben geïnformeerd.\
                    \n\
                    \nMet vriendelijke groeten,\
                    \nJe naam\
                    \nVerzekeringsagent```\
                    \n\
                    \nMocht de klant daar tegen in bezwaar gaan, dan ``!lift`` je de ticket en dan neemt een manager het over.\
                    \nAls de manager van mening is dat je goed hebt gehandeld word je uitbetaald.",
                "author": "",
                "items": {}
            }

            embed = await return_embed(dict_, color=0xffffff)
            await self.bot.schoollevelone.send(embed=embed)

            # E-MW school channel
            # self.bot.schoolemw
            # ======================================= #
            dict_ = {
                "url": "",
                "title": "Welkom bij VKG",
                "description": f"Beste {self.bot.emwrole.mention},\n\
                    \n\
                    Van harte welkom!\
                    \n\
                    \n__**{self.bot.anwbrole.mention}, {self.bot.amburole.mention}:**__\
                    \nWij verwachten van jou dat je een verslag maakt \
                    wanneer iemand zich aanmeld met schade en je hebt geconstateerd \
                    dat de persoon in het bezit is van een BA of omnium verzekering. \
                    \nWat er in de aangifte moet staan vind je als voorlaatste puntje terug.\
                    \n\
                    \n__**{self.bot.politierole.mention}, {self.bot.vsgrole.mention}:**__\
                    \nWij verwachten van jou dat je een analyse maakt van een gegeven situatie.\
                    Hier dien je objectief naar te kijken en een verdict te vellen, nl. wie er schuldig is.\
                    Jij bepaalt dus wie er in fout is. Verklaar ook in je verslag waarom dat zo is.\
                    \n\
                    \n__**BA:**__\
                    \nHet andere voertuig vergoeden wij, inclusief RWS en takelwagen.\
                    \\Het niet verzekerde voertuig krijgt een factuur.\
                    \n\
                    \n__**Omnium:**__\
                    \nHet verzekerde voertuig vergoeden wij, exclusief RWS en takelwagen.\
                    \n\
                    \n__**Full Omnium:**__\
                    \nHet verzekerde voertuig vergoeden wij, inclusief RWS en takelwagen.\
                    \n\
                    \n__**Handelsverzekering:**__\
                    \nHet verzekerde voertuig vergoeden wij, inclusief RWS en takelwagen.\
                    \nHet andere voertuig vergoeden wij, inclusief RWS en takelwagen.\
                    \n\
                    \n__**Zorgverzekering:**__\
                    \nDe verzekerde zijn medische kosten worden vergoed.\
                    \nKosten van niet-verzekerden kunnen verhaald worden \
                    als de politie de BA verzekerde schuldig achten.\
                    \n\
                    \n__**De aangifte:**__\
                    \nJe komt aan bij je melding en heeft een verzekering.\
                    \n\nOptie 1:\
                    \nJe maakt een ticket aan, daarin meld je het volgende:\
                    \n**Wie jij bent**, *(naam, roepnummer, job)*,\
                    \n**Om welk voertuig en/of persoon het gaat**, *(nummerplaat, naam, bsn)*,\
                    \n**De andere partij**, *(nummerplaat, naam, bsn)*,\
                    \n**Beschrijving**, *(jouw vaststelling(en))*\
                    \n**Locatie**, *(met foto, gps bij ongeluk)*\
                    \n\nOptie 2:\
                    \n<https://forms.gle/bXS5hjMqBEGmRtDg6>\
                    \n\
                    \nDe verloningen:\
                    \n**Per correcte aangifte: €250,00**\
                    \n**Per analyse: €350,00** (auto ongeluk)\
                    \n**Per analyse: €500,00**, *(vliegtuig en boot ongeluk)*\
                    \n*Uitbetalingen gebeuren per week.*\
                    \n\
                    \nMochten er klachten zijn kan je bij {self.bot.managerrole.mention}, {self.bot.boss.mention} of \
                    {self.bot.jmrole.mention} terecht.\
                    \n\
                    \nWe wensen jou veel succes met je nieuwe baan!\
                    \n\
                    Met vriendelijke groeten,\
                    \n{self.bot.user.mention}\
                    \nSecretaresse\
                    \n\
                    \n{self.bot.boss.mention}\
                    \n{self.bot.directorrole.mention}",
                "author": "",
                "items": {}
            }

            embed = await return_embed(dict_, color=0xffffff)
            await self.bot.schoolemw.send(embed=embed)

    @commands.command()
    async def roletemplate(self, ctx):
        await ctx.message.delete()
        if general.check_perms('dev', ctx.author):
            dict_ = {
                "url": "",
                "title": "Rol aanvragen",
                "description": f"Beste werknemer,\n\
                    \nGelieve je te houden aan de template hieronder.\n\
                    \n\
                    Met vriendelijke groeten,\
                    \n{self.bot.user.mention}\
                    \nSecretaresse",
                "author": "",
                "items": {}
            }
                        
            bali = self.bot.get_channel(875098573547646994)
            embed = await return_embed(dict_, color=0xffffff)
            await bali.send(embed=embed)
            await bali.send("```Naam:\nRol:```")
            
    @commands.command(aliases=['waarschuw'])
    async def warn(self, ctx, member: discord.Member, *, reason="geen reden opgegeven"):
        await ctx.message.delete()
        if general.check_perms('administrative', ctx.author):
            dict_ = {
                "url": "",
                "title": "Waarschuwing gelogd",
                "description": f"{member.mention} werd gewaarschuwd voor: {reason}.",
                "author": "",
                "items": {}
            }
            
            embed = await return_embed(dict_)
            await ctx.send(embed=embed, delete_after=20)

            log_dict = {
                "mod": ctx.author.id,
                "user": member.id,
                "reason": reason,
                "unixtime": int(time.time()),
                "perms": "administrative",
                "type": 0
            }

            make_log(log_dict)

            try:
                channel = await member.create_dm()
                await channel.send(embed=embed)
            except:
                pass

            await make_discord_log(self, ctx, log_dict)
        else:
            await ctx.send(f'{ctx.author.mention}, jammer genoeg heeft u niet genoeg permissies.', delete_after=10)

    @commands.command(aliases=['stamp'])
    async def kick(self, ctx, member: discord.Member, *, reason="geen reden opgegeven"):
        await ctx.message.delete()
        if general.check_perms('administrative', ctx.author):
            dict_ = {
                "url": "",
                "title": "Kick gelogd",
                "description": f"{member.mention} werd gekickt voor: {reason}.",
                "author": "",
                "items": {}
            }

            embed = await return_embed(dict_)
            await ctx.send(embed=embed, delete_after=20)

            log_dict = {
                "mod": ctx.author.id,
                "user": member.id,
                "reason": reason,
                "unixtime": int(time.time()),
                "perms": "administrative",
                "type": 1
            }

            make_log(log_dict)
            
            try:
                channel = await member.create_dm()
                await channel.send(embed=embed)
            except:
                pass

            await make_discord_log(self, ctx, log_dict)
            await member.kick(reason=reason)
        else:
            await ctx.send(f'{ctx.author.mention}, jammer genoeg heeft u niet genoeg permissies.', delete_after=10)

    @commands.command(aliases=['banhamer'])
    async def ban(self, ctx, member: discord.Member, *, reason="geen reden opgegeven"):
        await ctx.message.delete()
        if general.check_perms('administrative', ctx.author) and not general.check_perms('administrative', member):
            dict_ = {
                "url": "",
                "title": "Ban gelogd",
                "description": f"{member.mention} werd geband voor: {reason}.",
                "author": "",
                "items": {}
            }
            
            embed = await return_embed(dict_)
            await ctx.send(embed=embed, delete_after=20)

            log_dict = {
                "mod": ctx.author.id,
                "user": member.id,
                "reason": reason,
                "unixtime": int(time.time()),
                "perms": "administrative",
                "type": 2
            }

            make_log(log_dict)

            try:
                channel = await member.create_dm()
                await channel.send(embed=embed)
            except:
                pass

            await make_discord_log(self, ctx, log_dict)
            await member.ban(reason=reason)
        else:
            await ctx.send(f'{ctx.author.mention}, jammer genoeg heeft u niet genoeg permissies.', delete_after=10)

    @commands.command()
    async def unban(self, ctx, member, *, reason="geen reden opgegeven"):
        await ctx.message.delete()
        if general.check_perms('administrative', ctx.author):
            banned_users = await ctx.guild.bans()
            member_name, member_discriminator = member.split('#')

            for ban_entry in banned_users:
                user = ban_entry.user

                if (user.name, user.discriminator) == (member_name, member_discriminator):
                    dict_ = {
                        "url": "",
                        "title": "Unban gelogd",
                        "description": f"{member} werd geunband.",
                        "author": "",
                        "items": {}
                    }
                    embed = return_embed(dict_)
                    await ctx.send(embed=embed, delete_after=20)
                    
                    log_dict = {
                        "mod": ctx.author.id,
                        "user": user.id,
                        "reason": reason,
                        "unixtime": int(time.time()),
                        "perms": "administrative",
                        "type": 3
                    }
                    
                    make_log(log_dict)

                    try:
                        channel = await member.create_dm()
                        await channel.send(embed=embed)
                    except:
                        pass

                    await make_discord_log(self, ctx, log_dict)
                    await ctx.guild.unban(user)
                    return
        else:
            await ctx.send(f'{ctx.author.mention}, jammer genoeg heeft u niet genoeg permissies.', delete_after=10)

    @commands.command()
    async def toonlocatie(self, ctx):
        await ctx.message.delete()
        if general.check_perms('basic', ctx.author):
            await ctx.send("Ons hoofdkantoor is gevestigd op postcode 4024.\nHet zwart omkaderd gedeelte is Sandy Super's garage.\nHieronder ziet u de kaart:")
            await ctx.send("http://vkg.groningenrp.xyz/images/vkg_dekaart.png")

    @commands.command()
    async def purge(self, ctx, qty: int):
        await ctx.message.delete()
        if general.check_perms('administrative', ctx.author):
            await ctx.channel.purge(limit=(qty))

    @commands.command(aliases=['dc'])
    async def disconnect(self, ctx):
        await ctx.message.delete()
        if general.check_perms('dev', ctx.author):
            bot_speaks(self.bot, 'Ik sluit af.')
            await ctx.self.close()
            os.kill(os.getppid(), signal.SIGHUP)

    @commands.command(aliases=['reload'])
    async def reload_specific_cog_command(self, ctx, arg: str):
        await ctx.message.delete()     
        if general.check_perms('dev', ctx.author):
            cog = None
            if self.bot.coglist[arg]:
                cog = self.bot.coglist[arg]
                await self.bot.reload_extension(cog)
                await ctx.send(f'{ctx.author.mention}, {arg} werd gereload.', delete_after=10)
                
            else:
                await ctx.send(f'{ctx.author.mention}, jammer genoeg is er geen cog met die naam.', delete_after=10)                            

    @commands.command(aliases=['geef'])
    async def _add_role(self, ctx, param_one: typing.Union[discord.Member, discord.Role, str], param_two: typing.Union[discord.Member, discord.Role, str]):
        member = None
        role = None
        run = True
        await ctx.message.delete()
        if general.check_perms('administrative', ctx.author):
            if isinstance(param_one, discord.Member):
                member = param_one
            elif isinstance(param_one, discord.Role):
                role = param_one
            elif isinstance(param_one, str):
                role = discord.utils.get(ctx.guild.roles, id=general.return_role_id(param_one))
            else:
                await ctx.send(f'{ctx.author.mention}, parameter :one: werd niet gevonden.', delete_after=10)
                run = False
                
            if isinstance(param_two, discord.Member):
                member = param_two
            elif isinstance(param_two, discord.Role):
                role = param_two
            elif isinstance(param_two, str):
                role = general.return_role_id(param_two)
            else:
                await ctx.send(f'{ctx.author.mention}, parameter :two: werd niet gevonden.', delete_after=10)
                run = False

            if run:
                bot_speaks(self.bot, f'{ctx.author} heeft voldoende permissies en geeft {member} de {role} rol.')
                await member.add_roles(role)
                await ctx.send(f'{ctx.author.mention}, het is gelukt. {member.mention} heeft nu de {role} rol.', delete_after=30)
        else:
            await ctx.send(f'{ctx.author.mention}, u heeft niet voldoende permissies hiervoor.', delete_after=10)
        
    @commands.command(aliases=['neem'])
    async def _take_role(self, ctx, param_one: typing.Union[discord.Member, discord.Role, str], param_two: typing.Union[discord.Member, discord.Role, str]):
        member = None
        role = None
        run = True
        await ctx.message.delete()
        if general.check_perms('administrative', ctx.author):
            if isinstance(param_one, discord.Member):
                member = param_one
            elif isinstance(param_one, discord.Role):
                role = param_one
            elif isinstance(param_one, str):
                role = discord.utils.get(ctx.guild.roles, id=general.return_role_id(param_one))
            else:
                await ctx.send(f'{ctx.author.mention}, parameter :one: werd niet gevonden.', delete_after=10)
                run = False
                
            if isinstance(param_two, discord.Member):
                member = param_two
            elif isinstance(param_two, discord.Role):
                role = param_two
            elif isinstance(param_two, str):
                role = general.return_role_id(param_two)
            else:
                await ctx.send(f'{ctx.author.mention}, parameter :two: werd niet gevonden.', delete_after=10)
                run = False

            if run:
                bot_speaks(self.bot, f'{ctx.author} heeft voldoende permissies en neemt van {member} de {role} rol af.')
                await member.remove_roles(role)
                await ctx.send(f'{ctx.author.mention}, het is gelukt. {member.mention} heeft nu geen {role} rol meer.', delete_after=30)
        else:
            await ctx.send(f'{ctx.author.mention}, u heeft niet voldoende permissies hiervoor.', delete_after=10)
        
async def setup(bot):
    await bot.add_cog(administration(bot))