from datetime import date, datetime, timedelta
from decimal import Decimal
from fpdf import FPDF
from classes.client import Client
from classes.insurance import Insurance
from classes.staticclasses import Category, InsurableType, InsuranceType, SubCategory
import os
import mysql.connector
import time
from dotenv.main import load_dotenv

def generate_conditions_PDF(givenClient:Client = None, givenInsurance:Insurance = None):
    class PDF(FPDF):
        def lines(self):
            self.set_line_width(0.0)
            self.line(5.0,5.0,205.0,5.0) # top one
            self.line(5.0,292.0,205.0,292.0) # bottom one
            self.line(5.0,5.0,5.0,292.0) # left one
            self.line(205.0,5.0,205.0,292.0) # right one

        def footer(self):
            if self.page_no() != 1:
                # Go to 1.5 cm from bottom
                self.set_y(-15)
                # Select Arial italic 8
                self.set_font('Helvetica', 'I', 8)
                ## Print centered page number
                self.cell(0, 10, 'Pagina %s' % self.page_no() + '/{nb}', 0, 0, 'R')
                self.image("images/vkg_logo_render_smoll.png", 8, 280, h=10)

        pass

    if givenClient == None:
        givenClient = Client(
            id=1,
            fivemID=None,
            discordID=None,
            fname="Voornaam",
            lname="Achternaam",
            adres="Straat nummer, postcode",
            dob=date(1990, 1, 1),
            bsn=1,
            phone="04 12 34 56 78",
            crosses=0,
            licenseA=1,
            licenseB=0,
            licenseC=1,
            licenseFlight=0,
            licenseBoat=1
        )

    pdf = PDF()
    # vleeskleur pdf.set_fill_color(255, 112, 112)
    # blauw pdf.set_fill_color(27, 31, 113)
    # wit pdf.set_fill_color(255, 255, 255)
    # zwart pdf.set_fill_color(0, 0, 0)

    # Pagina 1
    pdf.add_page()
    pdf.lines()
    pdf.image("images/vkg_logo_render_smoll.png", 25, 126, h=40)
    pdf.ln(150)
    pdf.set_font('Arial', 'B', 30)
    pdf.cell(0, 40, "Voorwaarden, Juni 2022", 0, 0, "C")

    # Pagina 2
    # Inhoudstafel
    pdf.add_page()

    ## Titel
    pdf.set_font('Arial', 'B', 25)
    pdf.cell(0, 10, "Inhoudstafel", 0, 0, "C")
    pdf.set_line_width(0.6)
    pdf.set_draw_color(255, 112, 112)
    pdf.line(79.0, 19.0, 131.0, 19.0)
    pdf.ln(18)

    ## Inhoud
    pdf.set_font('Arial', 'B', 20)

    line_height = pdf.font_size * 1.5
    col_width = pdf.epw / 2
    data = {}
    if givenInsurance != None:
        data = {
            "Woordbepalingen": 3,
            "Voorwaarden": 4,
            "Bonusmalus": 5,
            "Opzeggen": 7,
            "Wanbetaling": 8,
            "Kruisjes": 9,
            "Blacklist": 10,
            "GDPR": 11
        }
    else:
        data = {
            "Woordbepalingen": 3,
            "Voorwaarden": 5,
            "Bonusmalus": 6,
            "Opzeggen": 8,
            "Wanbetaling": 9,
            "Kruisjes": 10,
            "Blacklist": 11,
            "GDPR": 12
        }

    for key in data.keys():
        pdf.multi_cell(col_width, line_height, f"{key}", border=0, new_x="RIGHT", new_y="TOP", align="L", max_line_height=pdf.font_size)    
        pdf.multi_cell(col_width, line_height, f"{data[key]}", border=0, new_x="RIGHT", new_y="TOP", align="R", max_line_height=pdf.font_size)
        pdf.ln(14)

    # Pagina 3
    # Woordbepalingen
    pdf.add_page()

    ## Titel
    pdf.set_font('Arial', 'B', 25)
    pdf.cell(0, 10, "Woordbepalingen", 0, 0, "C")
    pdf.set_line_width(0.6)
    pdf.set_draw_color(255, 112, 112)
    pdf.line(68.0, 19.0, 105.0, 19.0)
    pdf.line(109.0, 19.0, 126.0, 19.0)
    pdf.line(132.0, 19.0, 142.0, 19.0)
    pdf.ln(12)
    ## Inhoud
    ### De verzekeraar
    pdf.set_font('Arial', 'B', 20)
    pdf.cell(0, 10, "De verzekeraar:")
    pdf.ln(13)
    pdf.set_font('Arial', 'I', 14)
    pdf.cell(20, 0, "")
    pdf.cell(0, 0, "Hierna genoemd als \"verzekeraar\".")
    pdf.ln(8)
    pdf.set_font('Arial', size=14)
    pdf.cell(20, 0, "")
    pdf.cell(0, 0, "Bedrijfsnaam: Verzekeringen Groningen")
    pdf.ln(6)
    pdf.cell(20, 0, "")
    pdf.cell(0, 0, "Adres: Route 68, huisnummer 69, postcode 4024 te Groningen")
    pdf.ln(6)
    pdf.cell(20, 0, "")
    pdf.cell(0, 0, "KvK-nummer: NL01133880")
    pdf.ln(6)
    pdf.cell(20, 0, "")
    pdf.cell(0, 0, "Telefoonnummer: +31 6 95 887 747")

    ## Einde verzekeraar

    pdf.ln(5)

    ## De verzekerde

    # Statische gegevens:
    pdf.set_font('Arial', 'B', 20)
    pdf.cell(0, 10, "De verzekeringsnemer:")
    pdf.ln(13)
    pdf.set_font('Arial', 'I', 14)
    pdf.cell(20, 0, "")
    pdf.cell(0, 0, "Hierna genoemd als \"verzekeringsnemer\" en/of \"klant\".")
    pdf.ln(8)
    pdf.set_font('Arial', size=14)
    pdf.cell(20, 0, "")
    pdf.cell(0, 0, f"Naam: {givenClient.lname} {givenClient.fname}")
    pdf.ln(6)
    pdf.cell(20, 0, "")
    pdf.cell(0, 0, f"Adres: {givenClient.adres}")
    pdf.ln(6)
    pdf.cell(20, 0, "")
    pdf.cell(0, 0, f"Telefoonnummer: {givenClient.phone}")
    pdf.ln(6)
    pdf.cell(20, 0, "")

    rijbewijzen = {
        "A": givenClient.licenseA,
        "B": givenClient.licenseB,
        "C": givenClient.licenseC,
        "Vliegbrevet": givenClient.licenseFlight,
        "Vaarbrevet": givenClient.licenseBoat
    }

    lijstRijbewijzen = list(rijbewijzen.keys())
    rijbewijzenklant = ""
    index = 0
    for key in lijstRijbewijzen:
        if rijbewijzen[key] == 1:
            rijbewijzenklant += key
    
        if len(lijstRijbewijzen) > index + 1 and rijbewijzen[lijstRijbewijzen[index + 1]] == 1:
            rijbewijzenklant += " / "

        index += 1

    pdf.cell(0, 0, f"Rijbewijzen: {rijbewijzenklant}")
    pdf.ln(6)
    pdf.cell(20, 0, "")
    pdf.cell(0, 0, f"BSN: {givenClient.bsn}")

    ## Einde de verzekerde

    if givenInsurance != None:
        ## Het verzekerde
        pdf.ln(5)
        # Statische gegevens
        pdf.set_font('Arial', 'B', 20)
        pdf.cell(0, 10, "Het verzekerde:")
        pdf.ln(13)
        pdf.set_font('Arial', 'I', 14)
        pdf.cell(20, 0, "")
        pdf.cell(0, 0, "Hierna genoemd als \"het verzekerde (goed)\".")
        pdf.ln(8)

        pdf.set_font('Arial', size=14)
        pdf.cell(20, 0, "")
        pdf.cell(0, 0, f"Verzekering: {givenInsurance.insurance_type.category.name} oftewel")
        pdf.ln(5)
        pdf.cell(20, 0, "")

        text = ""
        text += f"{givenInsurance.insurance_type.category.short_name} verzekering"

        if givenInsurance.policy_nr != None:
            text += f" met polisnummer {givenInsurance.policy_nr}."
        else:
            text += "."

        pdf.cell(0, 0, text)        
        
        if givenInsurance != None and givenInsurance.insurance_type.insurable_type.sub_category.id == 1:
            pdf.ln(6)
            pdf.cell(20, 0, "")
            pdf.cell(0, 0, f"Beroep: {givenInsurance.insurance_type.insurable_type.name}")

        elif givenInsurance != None and givenInsurance.insurance_type.insurable_type.sub_category.id == 2:
            pdf.ln(6)
            pdf.cell(20, 0, "")
            pdf.cell(0, 0, f"Type: {givenInsurance.insurance_type.insurable_type.name}")
            pdf.ln(6)
            pdf.cell(20, 0, "")
            pdf.cell(0, 0, f"Kenteken: \"{givenInsurance.insured}\"")

        pdf.ln(6)
        pdf.cell(20, 0, "")
        pdf.cell(0, 0, f"Huidige bonusmalus: {givenInsurance.multiplier}")

        pdf.ln(6)
        pdf.cell(20, 0, "")
        pdf.cell(0, 0, f"Standaard bonusmalus: {givenInsurance.insurance_type.default_mp}")

        pdf.ln(6)
        pdf.cell(20, 0, "")
        pdf.cell(0, 0, f"Minimum bonusmalus: {givenInsurance.insurance_type.min_mp}")

        text = date.fromtimestamp(givenInsurance.startDate)
        pdf.ln(6)
        pdf.cell(20, 0, "")        
        pdf.cell(0, 0, f"Begin datum: {text:%d-%m-%y}")

        text = date.fromtimestamp(givenInsurance.endDate)
        pdf.ln(6)
        pdf.cell(20, 0, "")        
        pdf.cell(0, 0, f"Eind datum: {text:%d-%m-%y}")
    else:
        pass

    ## Einde het verzekerde

    pdf.ln(5)

    ## Premie
    pdf.set_font('Arial', 'B', 20)
    pdf.cell(0, 10, "De premie:")
    pdf.ln(13)
    pdf.set_font('Arial', 'I', 14)
    pdf.cell(20, 0, "")
    pdf.cell(0, 0, "Hierna genoemd als \"premie\".")
    pdf.ln(8)
    pdf.set_font('Arial', size=14)
    pdf.cell(20, 0, "")
    pdf.cell(0, 0, f"Het te betalen bedrag van eender welk type verzekering die")
    pdf.ln(5)
    pdf.cell(20, 0, "")
    pdf.cell(0, 0, f"u afsluit oftewel de wekelijkse kostprijs.")

    ## Einde premie 

    pdf.ln(5)

    ## Bonusmalus

    pdf.set_font('Arial', 'B', 20)
    pdf.cell(0, 10, "De bonusmalus:")
    pdf.ln(13)
    pdf.set_font('Arial', 'I', 14)
    pdf.cell(20, 0, "")
    pdf.cell(0, 0, "Hierna genoemd als \"bonusmalus\".")
    pdf.ln(8)
    pdf.set_font('Arial', size=14)
    pdf.cell(20, 0, "")
    pdf.cell(0, 0, f"Het getal waarmee de geschatte kostprijs vermenigvuldigt")
    pdf.ln(5)
    pdf.cell(20, 0, "")
    pdf.cell(0, 0, f"word om de premie te bekomen.")

    ## Einde bonusmalus

    # Pagina 4
    pdf.add_page()

    ## Uitleg verzekering
    if givenInsurance != None:
        pdf.set_font('Arial', 'B', 20)
        pdf.cell(0, 10, f"{givenInsurance.insurance_type.category.name}:")
        pdf.ln(13)
        pdf.set_font('Arial', 'I', 14)
        pdf.cell(20, 0, "")
        pdf.cell(0, 0, f"Hierna genoemd als \"{givenInsurance.insurance_type.category.short_name} verzekering\".")
        pdf.ln(8)
        pdf.set_font('Arial', size=14)
        pdf.cell(20, 0, "")
        pdf.multi_cell(pdf.epw * 0.8, pdf.font_size * 2, givenInsurance.insurance_type.category.explanation, border=0, new_x="RIGHT", new_y="TOP", max_line_height=pdf.font_size, align="L")

        
    else:
        allCategories = []

        load_dotenv()
                
        mydb = mysql.connector.connect(
            host=os.getenv('DB_SERVERNAME'),
            user=os.getenv('DB_USERNAME'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME')
        )

        sql = "SELECT * FROM `tbl_categories`;"
        mycursor = mydb.cursor(buffered=True)
        mycursor.execute(sql)
        myresult = mycursor.fetchall()

        for record in myresult:
            allCategories.append(Category(
                id=record[0],
                short_name=record[1],
                name=record[2],
                explanation=record[3]
            ))

        index = 0
        for category in allCategories:
            pdf.set_font('Arial', 'B', 20)
            pdf.cell(0, 10, f"{category.name}:")
            pdf.ln(13)
            pdf.set_font('Arial', 'I', 14)
            pdf.cell(20, 0, "")
            pdf.cell(0, 0, f"Hierna genoemd als \"{category.short_name} verzekering\".")
            pdf.ln(6)
            pdf.set_font('Arial', size=14)
            pdf.cell(20, 0, "")
            pdf.multi_cell(pdf.epw * 0.8, pdf.font_size * 2, category.explanation, border=0, new_x="RIGHT", new_y="TOP", max_line_height=pdf.font_size, align="L")
            pdf.ln(12)

            index += 1
    ## Einde uitleg verzekering

    # Pagina 5
    pdf.add_page()

    ## Titel
    pdf.set_font('Arial', 'B', 25)
    pdf.cell(0, 10, "Voorwaarden", 0, 0, "C")
    pdf.set_line_width(0.6)
    pdf.set_draw_color(255, 112, 112)
    pdf.line(78.0, 19.0, 132.0, 19.0)
    pdf.ln(14)

    ## Uitleg voorwaarden
    pdf.set_font('Arial', size=14)
    pdf.cell(10, 0, "")
    pdf.cell(0, 0, "1. Bij het afsluiten van een verzekering, ongeacht welk type, gaat u akkoord")
    pdf.ln(5)
    pdf.cell(10, 0, "")
    pdf.cell(0, 0, "met alle voorwaarden.")

    pdf.ln(8)

    pdf.cell(10, 0, "")
    pdf.cell(0, 0, "2. U bent op het moment van afsluiten van een verzekering, ongeacht welk type,")
    pdf.ln(5)
    pdf.cell(10, 0, "")
    pdf.cell(0, 0, "bewust van uw rechten en plichten.")

    pdf.ln(8)

    pdf.cell(10, 0, "")
    pdf.cell(0, 0, "3. De verzekeraar zal alle kosten gemaakt door de verzekerde terugeisen als")
    pdf.ln(5)
    pdf.cell(10, 0, "")
    pdf.cell(0, 0, "deze in overtreding is met een of meerdere van volgende uitzonderingen:")

    pdf.ln(8)

    pdf.cell(20, 0, "")
    pdf.cell(0, 0, "a. Strafbaar bent voor het WvS (Wetboek van Strafrecht) of de WvW")
    pdf.ln(5)
    pdf.cell(20, 0, "")
    pdf.cell(0, 0, "(Wegenverkeerswet). Denk hierbij aan, maar niet gelimiteerd tot,")
    pdf.ln(5)
    pdf.cell(20, 0, "")
    pdf.cell(0, 0, "volgende zaken:")

    pdf.ln(8)

    pdf.cell(30, 0, "")
    pdf.cell(0, 0, "i. Besturen van een voertuig onder invloed.")

    pdf.ln(8)

    pdf.cell(30, 0, "")
    pdf.cell(0, 0, "ii. Bij gevaarlijk rijgedrag een ongeluk veroorzaken.")

    pdf.ln(8)

    pdf.cell(30, 0, "")
    pdf.cell(0, 0, "iii. Schade veroorzaken en vervolgens vluchtmisdrijf plegen.")

    pdf.ln(8)

    pdf.cell(30, 0, "")
    pdf.cell(0, 0, "iv. Rijden zonder geldig rijbewijs.")

    pdf.ln(8)

    pdf.cell(30, 0, "")
    pdf.cell(0, 0, "v. Rijden zonder geldig kenteken.")

    pdf.ln(8)

    pdf.cell(30, 0, "")
    pdf.cell(0, 0, "vi. Opzettelijk schade veroorzaken.")

    pdf.ln(8)

    pdf.cell(30, 0, "")
    pdf.cell(0, 0, "vii. Schade ten gevolge van:")

    pdf.ln(8)

    pdf.cell(40, 0, "")
    pdf.cell(0, 0, "1. Onbeheerd achterlaten van uw voertuig.")

    pdf.ln(8)

    pdf.cell(40, 0, "")
    pdf.cell(0, 0, "2. Niet slotvast voertuig achterlaten.")

    pdf.ln(8)

    pdf.cell(40, 0, "")
    pdf.cell(0, 0, "3. Sleutels in de nabijheid bewaren.")

    pdf.ln(8)

    pdf.cell(30, 0, "")
    pdf.cell(0, 0, "viii. Nalatenschap m.b.t. aangifte van diefstal/joyriding.")

    pdf.ln(8)

    pdf.cell(20, 0, "")
    pdf.cell(0, 0, "b. Wanbetaling van premies.")

    pdf.ln(8)

    pdf.cell(10, 0, "")
    pdf.cell(0, 0, "4. Bij het afsluiten van een verzekering, ongeacht welk type, bewust")
    pdf.ln(5)
    pdf.cell(10, 0, "")
    pdf.cell(0, 0, "bent dat u een contractuele verbintenis aangaat.")

    pdf.ln(8)

    pdf.cell(10, 0, "")
    pdf.cell(0, 0, "5. Elk contract wordt automatisch vernieuwd na natuurlijke afloop.")

    pdf.ln(8)

    pdf.cell(10, 0, "")
    pdf.cell(0, 0, "6. Het opheven van deze contractuele verbintenis dient te geschieden")
    pdf.ln(5)
    pdf.cell(10, 0, "")
    pdf.cell(0, 0, "ten laatste 3 dagen voor het automatisch vernieuwen wanneer de minimale")
    pdf.ln(5)
    pdf.cell(10, 0, "")
    pdf.cell(0, 0, "bonusmalus reeds behaald werd.")

    pdf.ln(8)

    pdf.cell(10, 0, "")
    pdf.cell(0, 0, "7. Indien er enige vorm van fraude vastgesteld wordt behoud de verzekeraar")
    pdf.ln(5)
    pdf.cell(10, 0, "")
    pdf.cell(0, 0, "het recht om de contractuele verbintenis eenzijdig stop te zetten.")

    ## Einde voorwaarden

    # Pagina 6
    pdf.add_page()

    ## Titel
    pdf.set_font('Arial', 'B', 25)
    pdf.cell(0, 10, "Bonusmalus", 0, 0, "C")
    pdf.set_line_width(0.6)
    pdf.set_draw_color(255, 112, 112)
    pdf.line(79.0, 19.0, 131.0, 19.0)
    pdf.ln(14)

    ## Bonusmalus
    pdf.set_font('Arial', size=14)
    pdf.cell(0, 0, "Als u een verzekering afsluit begint u op een bepaalde bonusmalus.")
    pdf.ln(6)
    pdf.cell(0, 0, "Deze startende bonusmalus wisselt per type verzekering en subcategorie.")
    pdf.ln(8)
    pdf.cell(0, 0, "De bonusmalus stijgt en daalt op basis van de afloop van de schadeclaims.")

    def generatePVV():
        pdf.ln(10)

        pdf.set_font('Arial', 'B', 18)
        pdf.cell(0, 0, "Voor persoonsverzekeringen:")

        pdf.ln(7)

        pdf.set_font('Arial', size=14)
        pdf.cell(0, 0, "Het type beroep en medische achtergrond zal hier de bepalende factor wezen.")
        pdf.ln(6)
        pdf.cell(0, 0, "Hieronder benoemd, maar zijn niet gelimiteerd tot:")
        
        pdf.ln(8)
        
        pdf.cell(10, 0, "")
        pdf.cell(0, 0, "1. Politie- / KMAR ambtenaar")
        
        pdf.ln(8)
        
        pdf.cell(10, 0, "")
        pdf.cell(0, 0, "2. UWV / Interim werker")
        
        pdf.ln(8)
        
        pdf.cell(10, 0, "")
        pdf.cell(0, 0, "3. Ambulance personeel")
        
        pdf.ln(8)
        
        pdf.cell(10, 0, "")
        pdf.cell(0, 0, "4. ANWB personeel")

    def generateVVV():
        pdf.ln(10)

        pdf.set_font('Arial', 'B', 18)
        pdf.cell(0, 0, "Voor voertuigverzekeringen:")

        pdf.ln(7)

        pdf.set_font('Arial', size=14)
        pdf.cell(0, 0, "Het type voertuig wordt bepaalt op basis van een aantal kenmerken voor dat model.")
        pdf.ln(6)
        pdf.cell(0, 0, "Hieronder benoemd, maar zijn niet gelimiteerd tot:")
        
        pdf.ln(8)
        
        pdf.cell(10, 0, "")
        pdf.cell(0, 0, "1. Het verbruik")
        
        pdf.ln(8)
        
        pdf.cell(10, 0, "")
        pdf.cell(0, 0, "2. Het aantal zitplaatsen")
        
        pdf.ln(8)
        
        pdf.cell(10, 0, "")
        pdf.cell(0, 0, "3. Het aantal PK")
        
        pdf.ln(8)
        
        pdf.cell(10, 0, "")
        pdf.cell(0, 0, "4. Het gewicht")

    if givenInsurance != None and givenInsurance.insurance_type.insurable_type.sub_category.id == 1:
        generatePVV()

    elif givenInsurance != None and givenInsurance.insurance_type.insurable_type.sub_category.id == 2:
        generateVVV()
    else:
        generatePVV()
        generateVVV()        

    pdf.ln(10)

    pdf.set_font('Arial', 'B', 18)
    pdf.cell(0, 0, "Het gedrag van de bonusmalus:")
    pdf.ln(7)
    pdf.set_font('Arial', size=14)
    pdf.cell(0, 0, "Na natuurlijke vernieuwing van uw verzekering gaat het systeem kijken naar")
    pdf.ln(5)
    pdf.cell(0, 0, "de huidige bonusmalus en het aantal claims die ingedient werden door uzelf")
    pdf.ln(5)
    pdf.cell(0, 0, "of door een derde partij.")    
    
    # Pagina 7
    pdf.add_page()

    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 0, "Indien er schadeclaims zijn:")
    pdf.ln(7)

    pdf.set_font('Arial', size=14)
    pdf.cell(0, 0, "Als het aantal ingediende claims (waar u in fout bent) door uzelf of door")
    pdf.ln(5)
    pdf.cell(0, 0, "een derde partij hoger is dan uw huidige bonusmalus dan wordt uw nieuwe")
    pdf.ln(5)
    pdf.cell(0, 0, "bonusmalus de huidige bonusmalus + aantal claims + 1.")

    pdf.ln(8)

    pdf.cell(0, 0, "Als het aantal ingediende claims (waar u in fout bent) door uzelf of door")
    pdf.ln(5)
    pdf.cell(0, 0, "een derde partij lager is dan uw huidige bonusmalus dan wordt uw nieuwe")
    pdf.ln(5)
    pdf.cell(0, 0, "bonusmalus het hoogste van:")
    pdf.ln(6)
    pdf.cell(10, 0, "")
    pdf.cell(0, 0, "1. Uw huidige bonusmalus")
    pdf.ln(8)
    pdf.cell(10, 0, "")
    pdf.cell(0, 0, "2. Het aantal ingediende claims (waar u in fout bent) + 1")

    pdf.ln(8)

    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 0, "Indien er geen schadeclaims zijn:")
    pdf.ln(7)

    pdf.set_font('Arial', size=14)
    pdf.cell(0, 0, "Uw nieuwe bonusmalus wordt het hoogste van:")
    pdf.ln(6)
    pdf.cell(10, 0, "")
    pdf.cell(0, 0, "1. De minimum bonusmalus")
    pdf.ln(8)
    pdf.cell(10, 0, "")
    pdf.cell(0, 0, "2. De huidige bonusmalus - 20%")

    pdf.ln(8)

    pdf.cell(0, 0, "Als er in de tweedst volgende periode geen schadeclaims werden ingedient")
    pdf.ln(5)
    pdf.cell(0, 0, "(waar u in fout bent) dan wordt uw nieuwe bonusmalus het hoogste van:")

    pdf.ln(6)
    pdf.cell(10, 0, "")
    pdf.cell(0, 0, "1. De minimum bonusmalus")
    pdf.ln(8)
    pdf.cell(10, 0, "")
    pdf.cell(0, 0, "2. De huidige bonusmalus - 50%")

    pdf.ln(10)

    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 0, "De minimum bonusmalus:")
    pdf.ln(4)
    pdf.set_font('Arial', size=14)
    line_height = pdf.font_size * 1.5
    col_width = pdf.epw / 2

    if givenInsurance != None:
        data = {}

        load_dotenv()
                    
        mydb = mysql.connector.connect(
            host=os.getenv('DB_SERVERNAME'),
            user=os.getenv('DB_USERNAME'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME')
        )

        sql = """SELECT 
        `name`, 
        `min_mp` 
        FROM `tbl_insurance_types` 
            INNER JOIN `tbl_insurable_types` 
            ON `tbl_insurance_types`.`insurable_typeID` = `tbl_insurable_types`.`id` 
        WHERE `categoryID` = %s AND `insurable_typeID` = %s;"""

        mycursor = mydb.cursor(buffered=True)
        mycursor.execute(sql, (givenInsurance.insurance_type.category.id, givenInsurance.insurance_type.insurable_type.id))
        myresult = mycursor.fetchall()

        for record in myresult:
            data[record[0]] = record[1]

        for key in data.keys():            
            pdf.multi_cell(col_width, line_height, key, border=0, new_x="RIGHT", new_y="TOP", max_line_height=pdf.font_size, align="L")
            pdf.multi_cell(col_width, line_height, f"{data[key]}", border=0, new_x="RIGHT", new_y="TOP", max_line_height=pdf.font_size, align="R")
            pdf.ln(line_height)
    else:
        data = []

        load_dotenv()
                    
        mydb = mysql.connector.connect(
            host=os.getenv('DB_SERVERNAME'),
            user=os.getenv('DB_USERNAME'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME')
        )

        sql = "SELECT short_name FROM `tbl_categories`;"
        mycursor = mydb.cursor(buffered=True)
        mycursor.execute(sql)
        myresult = mycursor.fetchall()

        for record in myresult:
            data.append(record[0])

        sql = "SELECT name FROM `tbl_insurable_types`;"
        mycursor = mydb.cursor(buffered=True)
        mycursor.execute(sql)
        myresult = mycursor.fetchall()
        
        tmpdata = []
        for record in myresult:
            tmpdata.append(record[0])

        yaxis = []        
        indexnd = 1
        for value in tmpdata:
            tmp = [value]
            index = 1
            for category in data:
                sql = "SELECT `min_mp` FROM `tbl_insurance_types` WHERE `categoryID` = %s AND `insurable_typeID` = %s;"
                mycursor = mydb.cursor(buffered=True)
                mycursor.execute(sql, (index, indexnd))
                myresult = mycursor.fetchone()
                
                if myresult != None:
                    tmp.append(myresult[0])
                else:
                    tmp.append("0.00")

                #print("Ophalen v/d query:")
                #print()
                #print(f"De insurable type: {value}")
                #print()
                #print(f"De categorie: {category}")
                #print()
                #print(f"Het resultaat: {myresult}")
            
                index += 1
            yaxis.append(tmp)
            indexnd += 1
        
        data.insert(0, "")
        yaxis.insert(0, data)

        line_height = pdf.font_size * 1.5
        col_width = pdf.epw / 7

        #print("Het eindresultaat:")
        #print()
        #print(yaxis)
        #print()
        #print()

        for value in yaxis:
            #print("Elke rij:")
            #print()
            #print(value)
            #print()
            #print()

            pdf.multi_cell(col_width * 2, line_height, f"{value[0]}", border=0, new_x="RIGHT", new_y="TOP", max_line_height=pdf.font_size, align="L")
            pdf.multi_cell(col_width, line_height, f"{value[1]}", border=0, new_x="RIGHT", new_y="TOP", max_line_height=pdf.font_size, align="C")
            pdf.multi_cell(col_width, line_height, f"{value[2]}", border=0, new_x="RIGHT", new_y="TOP", max_line_height=pdf.font_size, align="C")
            pdf.multi_cell(col_width, line_height, f"{value[3]}", border=0, new_x="RIGHT", new_y="TOP", max_line_height=pdf.font_size, align="C")
            pdf.multi_cell(col_width, line_height, f"{value[4]}", border=0, new_x="RIGHT", new_y="TOP", max_line_height=pdf.font_size, align="C")
            pdf.multi_cell(col_width, line_height, f"{value[5]}", border=0, new_x="RIGHT", new_y="TOP", max_line_height=pdf.font_size, align="C")
            pdf.ln(line_height)                

    ## Einde Bonusmalus

    # Pagina 8
    pdf.add_page()

    ## Titel
    pdf.set_font('Arial', 'B', 25)
    pdf.cell(0, 10, "Opzeggen", 0, 0, "C")
    pdf.set_line_width(0.6)
    pdf.set_draw_color(255, 112, 112)
    pdf.line(84.0, 19.0, 90.0, 19.0)
    pdf.line(93.0, 19.0, 105.0, 19.0)
    pdf.line(116.0, 19.0, 126.0, 19.0)
    pdf.ln(8)


    ## Opzeggen
    pdf.set_font('Arial', size=14)
    pdf.ln(6)
    pdf.cell(0, 0, "Uiteraard kan u de verzekering die u heeft afgesloten opzeggen.")
    pdf.ln(8)
    pdf.cell(0, 0, "Er zijn enkele voorwaarden die van toepassing zijn als u de verzekering")
    pdf.ln(5)
    pdf.cell(0, 0, "wilt opzeggen:")
    pdf.ln(8)
    pdf.cell(10, 0, "")
    pdf.cell(0, 0, "1. De bonusmalus staat op het minimum van het type verzekering.")
    pdf.ln(8)
    pdf.cell(10, 0, "")
    pdf.cell(0, 0, "2. U laat ten laatste 3 dagen voor de natuurlijke vernieuwing")
    pdf.ln(5)
    pdf.cell(10, 0, "")
    pdf.cell(0, 0, "dit weten aan de verzekeraar.")
    pdf.ln(8)
    pdf.cell(0, 0, "Graag hadden wij ook een reden ontvangen om onze diensten en producten")
    pdf.ln(5)
    pdf.cell(0, 0, "te verbeteren naar onze toekomstige klanten toe.")
    ## Einde opzeggen

    # Pagina 9
    pdf.add_page()

    ## Titel
    pdf.set_font('Arial', 'B', 25)
    pdf.cell(0, 10, "Wanbetaling", 0, 0, "C")
    pdf.set_line_width(0.6)
    pdf.set_draw_color(255, 112, 112)
    pdf.line(80.0, 19.0, 125.0, 19.0)
    pdf.ln(8)

    ## Opzeggen
    pdf.set_font('Arial', size=14)
    pdf.ln(6)
    pdf.cell(0, 0, "Mocht u om eender welke reden dan ook financiële problemen ondervinden,")
    pdf.ln(5)
    pdf.cell(0, 0, "aarzel dan niet om ons hiervan op de hoogte te stellen.")
    pdf.ln(8)
    pdf.cell(0, 0, "Afbetalingsplannen kunnen altijd gemaakt worden via onze boekhoudkundige")
    pdf.ln(5)
    pdf.cell(0, 0, "afdeling.")

    pdf.ln(10)

    pdf.cell(0, 0, "Indien we aan het begin van de natuurlijke vernieuwing geen betaling")
    pdf.ln(5)
    pdf.cell(0, 0, "ontvangen hebben zullen we overgaan tot het terugvorderen van deze kosten,")
    pdf.ln(5)
    pdf.cell(0, 0, "indien nodig via gerechtelijke weg.")

    pdf.ln(10)

    pdf.cell(0, 0, "Ook zal de bonusmalus van deze, opvolgende, 2de natuurlijke vernieuwing")
    pdf.ln(5)
    pdf.cell(0, 0, "geen herziening van de bonusmalus ontvangen en een kruisje ontvangen")
    pdf.ln(5)
    pdf.cell(0, 0, "op uw naam.")

    pdf.ln(10)

    pdf.cell(0, 0, "Als we op het einde van de tweedst natuurlijke vernieuwing nog geen")
    pdf.ln(5)
    pdf.cell(0, 0, "betaling ontvangen hebben komt op u de blacklist voor de duur van 1 maand en")
    pdf.ln(5)
    pdf.cell(0, 0, "ontvangt u uw 2de kruisje en starten we de gerechtelijke procedure op.")

    ## Einde opzeggen

    # Pagina 10
    pdf.add_page()

    ## Titel
    pdf.set_font('Arial', 'B', 25)
    pdf.cell(0, 10, "Kruisjes", 0, 0, "C")
    pdf.set_line_width(0.6)
    pdf.set_draw_color(255, 112, 112)
    pdf.line(88.0, 19.0, 109.0, 19.0)
    pdf.line(113.0, 19.0, 122.0, 19.0)
    pdf.ln(8)

    ## Kruisjes
    pdf.set_font('Arial', size=14)
    pdf.ln(6)
    pdf.cell(0, 0, "In eerste instantie proberen we het afstraffen minimaal te houden.")
    pdf.ln(8)
    pdf.cell(0, 0, "Soms is er helaas geen andere oplossing. Mocht u dus financiële problemen")
    pdf.ln(5)
    pdf.cell(0, 0, "ondervinden, contacteer ons dan voor er zich echt grote problemen manifesteren.")

    pdf.ln(10)

    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 0, "Bij 1 kruisje:")
    pdf.ln(7)

    pdf.set_font('Arial', size=14)
    pdf.cell(10, 0, "")
    pdf.cell(0, 0, "- Lichte waarschuwing, u bent op dit moment niet goed bezig en")
    pdf.ln(5)
    pdf.cell(13, 0, "")
    pdf.cell(0, 0, "wij verwachten dat dit zich niet zal herhalen.")

    pdf.ln(10)

    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 0, "Bij 2 kruisjes:")
    pdf.ln(7)

    pdf.set_font('Arial', size=14)
    pdf.cell(10, 0, "")
    pdf.cell(0, 0, "- U moet nu echt wel alert worden, bij 3 kruisjes krijgt u problemen.")

    pdf.ln(10)

    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 0, "Bij 3 kruisjes:")
    pdf.ln(7)

    pdf.set_font('Arial', size=14)
    pdf.cell(10, 0, "")
    pdf.cell(0, 0, "- 1 maand blacklist")

    if givenClient != None:
        pdf.ln(10)
        pdf.set_font('Arial', 'B', size=14)
        pdf.cell(0, 0, f"U heeft op dit moment {givenClient.crosses} kruisjes.")

    ## Einde kruisjes

    # Pagina 11
    pdf.add_page()

    ## Titel
    pdf.set_font('Arial', 'B', 25)
    pdf.cell(0, 10, "Blacklist", 0, 0, "C")
    pdf.set_line_width(0.6)
    pdf.set_draw_color(255, 112, 112)
    pdf.line(87.0, 19.0, 123.0, 19.0)
    pdf.ln(8)

    ## Blacklist
    pdf.set_font('Arial', size=14)
    pdf.ln(6)
    pdf.cell(0, 0, "De zwarte lijst of blacklist is een algemene databank waar u in terecht")
    pdf.ln(5)
    pdf.cell(0, 0, "komt als u een speciaal risici vormt. Dit kan zijn omdat u de premies")
    pdf.ln(5)
    pdf.cell(0, 0, "niet op tijd betaald heeft, veel schadegevallen hebt veroorzaakt,")
    pdf.ln(5)
    pdf.cell(0, 0, "een frauduleuze verklaring hebt afgelegd bij het aangaan van een verzekering,")
    pdf.ln(5)
    pdf.cell(0, 0, "ongeacht het type, of u gezien wordt als verzwaard risico.")
    pdf.ln(10)
    pdf.cell(0, 0, "Eens u op deze lijst staat, kan u geen enkele verzekering meer afsluiten")
    pdf.ln(5)
    pdf.cell(0, 0, "voor de bepaalde periode.")
    ## Einde blacklist

    # Pagina 12
    pdf.add_page()

    ## Titel
    pdf.set_font('Arial', 'B', 25)
    pdf.cell(0, 10, "GDPR", 0, 0, "C")
    pdf.set_line_width(0.6)
    pdf.set_draw_color(255, 112, 112)
    pdf.line(93.0, 19.0, 118.0, 19.0)
    pdf.ln(8)

    ## Blacklist
    pdf.set_font('Arial', size=14)
    pdf.ln(6)
    pdf.cell(0, 0, "De gegevens die wij verzamelen over u zijn gegevens die u zelf aangeeft")
    pdf.ln(5)
    pdf.cell(0, 0, "bij het aangaan van een verzekering voor facturatie doeleinden.")

    pdf.alias_nb_pages()
    pdf.output('pdf/voorwaarden.pdf')
    return "pdf/voorwaarden.pdf"

#generate_conditions_PDF()

def generate_invoice_PDF(givenClient:Client = None, givenInsurance:Insurance = None, timedeltauitleg = None):
    now = datetime.now()
    today = now.today()
    next_week = today + timedelta(days=7)
    day_before = timedelta(days=1)
    betaaltermijn = next_week - day_before

    class PDF(FPDF):
        pass

    pdf = PDF()
    pdf.add_page(orientation="L")

    if givenClient == None:
        givenClient = Client(
            id=1,
            fivemID=None,
            discordID=None,
            fname="Voornaam",
            lname="Achternaam",
            adres="Straat nummer, postcode",
            dob=date(1990, 1, 1),
            bsn=1,
            phone="+31 4 12 34 56 78",
            crosses=0,
            licenseA=1,
            licenseB=0,
            licenseC=1,
            licenseFlight=0,
            licenseBoat=1
        )  

    if givenInsurance == None:        
        givenInsurance = Insurance(
            agentID=1,
            clientID=1,
            insured="SJAAK",
            insurance_typeID=1,
            multiplier=2,
            amount_paid=2400,
            startDate=now.timestamp(),
            endDate=next_week.timestamp()
        )

    pdf.image("images/vkg_logo_render_smoll.png", 177, 10, h=25)
    pdf.set_font('Arial', size=14)

    line_height = pdf.font_size * 1.2
    col_width = pdf.epw / 5

    gegevens = [
        ["Polisgegevens:", "", "", "", ""],
        ["Nummer:", f"{givenInsurance.policy_nr}", "", "", ""],
        ["Verzekering:", f"{givenInsurance.insurance_type.category.short_name.upper()}", "", "", ""],
        ["Type:", f"{givenInsurance.insurance_type.insurable_type.name}", "", "", ""],
        ["", "", "", "", ""],
        ["Klantgegevens:", "", "", "Bedrijfsgegevens:", ""],
        ["Naam:",f"{givenClient.fname} {givenClient.lname}", "", "Naam:", "Verzekeringen Groningen"],
        ["Adres:", f"{givenClient.adres}", "", "Adres:", "Route 68, huisnummer 69"],
        ["Telefoonnummer:", f"{givenClient.phone}", "", "Postcode:", "4024"],
        ["Geboortedatum:", f"{givenClient.dob.strftime('%d-%m-%Y')}", "", "Telefoonnummer:", "+31 6 95 887 747"],
        ["BSN:", f"{givenClient.bsn}", "", "KvK-nummer:", "NL01133880"]
    ]

    for rij in gegevens:
        pdf.multi_cell(col_width, line_height, rij[0], border=0, new_x="RIGHT", new_y="TOP", max_line_height=pdf.font_size, align="L")
        pdf.multi_cell(col_width + (col_width / 2), line_height, rij[1], border=0, new_x="RIGHT", new_y="TOP", max_line_height=pdf.font_size, align="L")
        pdf.multi_cell(col_width / 2, line_height, rij[2], border=0, new_x="RIGHT", new_y="TOP", max_line_height=pdf.font_size, align="L")    
        pdf.multi_cell(col_width, line_height, rij[3], border=0, new_x="RIGHT", new_y="TOP", max_line_height=pdf.font_size, align="L")
        pdf.multi_cell(col_width + (col_width / 2), line_height, rij[4], border=0, new_x="RIGHT", new_y="TOP", max_line_height=pdf.font_size, align="L")
        pdf.ln(line_height)

    # vleeskleur pdf.set_fill_color(255, 112, 112)
    # licht donkere vleeskleur pdf.set_fill_color(247, 163, 163)
    # lichte vleeskleur pdf.set_fill_color(250, 195, 195)
    # blauw pdf.set_fill_color(27, 31, 113)
    # lichtblauw pdf.set_fill_color(130, 135, 237)
    # wit pdf.set_fill_color(255, 255, 255)
    # zwart pdf.set_fill_color(0, 0, 0)
    pdf.set_line_width(1.0)
    pdf.line(0.0, 80.0, 300.0, 80.0)

    pdf.set_fill_color(255, 112, 112)
    pdf.rect(0, 80.5, 300, 8.2, style="F")

    
    yaxis = 88.7  
    #yaxis += 0.1    
    pdf.set_fill_color(250, 195, 195)
    #yaxis += 0.3
    pdf.rect(0, yaxis, 300, 8, style="F")
    
    
    yaxis += 8.0   
    pdf.set_fill_color(247, 163, 163)
    #yaxis += 0.3    
    pdf.rect(0, yaxis, 300, 8, style="F")
    yaxis += 8.0
        
    pdf.set_fill_color(250, 195, 195)
    #yaxis += 0.3
    pdf.rect(0, yaxis, 300, 8, style="F")
    yaxis += 8.0
    pdf.set_line_width(1.0)
    pdf.line(0.0, yaxis, 300.0, yaxis)
    #yaxis += 0.7
    yaxis += 0.4
    pdf.set_fill_color(255, 112, 112)
    pdf.rect(0, yaxis, 300, 8, style="F")
    yaxis += 8.0
    pdf.line(0.0, yaxis, 300.0, yaxis)

    pdf.set_line_width(1)
    pdf.line(104, 80, 104, 112.5)
    pdf.line(124, 80, 124, 112.5)

    pdf.set_line_width(1)
    pdf.line(164, 80, 164, 112.5)
    pdf.line(202, 80, 202, 112.5)

    pdf.set_line_width(1)
    pdf.line(244, 80, 244, 112.5)

    pdf.ln(6)

    def plaatsDecimaalSeps(getal):
        if len(getal[:-3]) > 6:
            getal = getal[0:-9] + "." + getal[-9:-6] + "." + getal[-6:len(getal)]
        elif len(getal[:-3]) > 3:
            getal = getal[0:-6] + "." + getal[-6:len(getal)]

        return getal

    prijs_excl = str('%.2f' % round(float((givenInsurance.amount_paid * 100) / 121), 2))
    prijs_excl = prijs_excl.replace('.', ',')
    prijs_excl = plaatsDecimaalSeps(prijs_excl)
    prijs_incl = str('%.2f' % round(float(givenInsurance.amount_paid), 2))
    prijs_incl = prijs_incl.replace('.', ',')
    prijs_incl = plaatsDecimaalSeps(prijs_incl)

    data = [
        ["Product:", "Duur:", "Bonusmalus:", "Prijs: (excl. BTW)"],
        [f"{givenInsurance.insurance_type.category.name} {givenInsurance.insurance_type.insurable_type.name}", 
        f"{timedeltauitleg}", 
        f"{givenInsurance.multiplier}", 
        f"{prijs_excl} euro"],
        ["", "", "", ""],
        ["", "", "", ""],
        ["", "", "Totaal: (incl. BTW)", f"{prijs_incl} euro"],
    ]

    line_height = pdf.font_size * 1.63
    col_width = pdf.epw / 8

    for row in data:
        pdf.multi_cell(col_width * 2, line_height, row[0], border=0, new_x="RIGHT", new_y="TOP", max_line_height=pdf.font_size, align="L")
        pdf.multi_cell(col_width * 2, line_height, row[1], border=0, new_x="RIGHT", new_y="TOP", max_line_height=pdf.font_size, align="C")
        pdf.multi_cell(col_width * 2, line_height, row[2], border=0, new_x="RIGHT", new_y="TOP", max_line_height=pdf.font_size, align="C")
        pdf.multi_cell(col_width * 2, line_height, row[3], border=0, new_x="RIGHT", new_y="TOP", max_line_height=pdf.font_size, align="R")
        pdf.ln(line_height)        

    pdf.ln(14)
    pdf.cell(0, 0, "Factuurgegevens:")
    pdf.ln(4.5)
    data = [
        ["Polisnummer:", f"{givenInsurance.policy_nr}"],
        ["Factuurdatum:", f"{today.strftime('%d-%m-%Y')}"],
        ["Betaal termijn:", f"{betaaltermijn.strftime('%d-%m-%Y')}"],                
        ["Begindatum:", f"{datetime.fromtimestamp(givenInsurance.startDate).strftime('%d-%m-%Y')}"],
        ["Natuurlijke vernieuwing:", f"{datetime.fromtimestamp(givenInsurance.endDate).strftime('%d-%m-%Y')}"],
    ]

    for row in data:
        pdf.multi_cell(pdf.epw / 4, pdf.font_size * 1.2, row[0], border=0, new_x="RIGHT", new_y="TOP", max_line_height=pdf.font_size, align="L")
        pdf.multi_cell(pdf.epw / 4, pdf.font_size * 1.2, row[1], border=0, new_x="RIGHT", new_y="TOP", max_line_height=pdf.font_size, align="L")        
        pdf.ln(6)

    maand_naam = [
        "Januari",
        "Februari",
        "Maart",
        "April",
        "Mei",
        "Juni",
        "Juli",
        "Augustus",
        "September",
        "Oktober",
        "November",
        "December"        
    ]

    pdf.ln(-20)    
    pdf.cell(140, 0, "")
    pdf.cell(0, 0, "De voorwaarden vindt u terug in het ander document.")
    pdf.ln(6)
    pdf.cell(140, 0, "")
    pdf.cell(0, 0, f"De versie van de maand {maand_naam[today.month - 1]} geldt voor deze factuur.")
    pdf.ln(34)
    pdf.set_text_color(255, 112, 112)
    pdf.set_font('Arial', 'B', size=16)
    pdf.cell(0, 0, f"Deze factuur dient uiterst tegen {betaaltermijn.strftime('%d-%m-%Y')} voldaat te worden.", align="C")
    pdf.output(f"pdf/factuur_vkg_{givenInsurance.policy_nr.lower()}.pdf")
    return f"pdf/factuur_vkg_{givenInsurance.policy_nr.lower()}.pdf"