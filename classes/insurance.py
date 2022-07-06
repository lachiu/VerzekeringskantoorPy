import random
import datetime
import os
import mysql.connector
from dotenv.main import load_dotenv
from classes.client import Client
from classes.employee import Employee
from classes.staticclasses import Category, InsurableType, InsuranceType, SubCategory

class Insurance():
    def __init__(self, agentID, clientID, insured, insurance_typeID, multiplier, amount_paid, startDate, endDate):
        def GeneratePolicyName(self):
            charlist = [
                0, 1, 2,
                3, 4, 5,
                6, 7, 8,
                9
            ]
            randomstring = f"{self.insurance_type.category.short_name.upper()}{self.insurance_type.insurable_type.short_name.upper()}{datetime.datetime.today().strftime('%d%m%y')}"
            iterable = 0
            while iterable < int(5):
                randomchar = random.randrange(0, 8)
                char = charlist[randomchar]
                randomstring += f"{char}"
                iterable += 1

            return randomstring

        def set_date(value):    
            return datetime.datetime.strptime(value)
                                 
        self.agent = None
        self.agentID = agentID
        self.client = None
        self.clientID = clientID
        self.insured = insured
        self.insurance_typeID = insurance_typeID        
        self.multiplier = multiplier
        self.amount_paid = amount_paid
        self.startDate = startDate
        self.endDate = endDate

        load_dotenv()
                
        mydb = mysql.connector.connect(
            host=os.getenv('DB_SERVERNAME'),
            user=os.getenv('DB_USERNAME'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME')
        )

        sql = "SELECT * FROM `tbl_agents` WHERE `id` = %s;"
        mycursor = mydb.cursor(buffered=True)
        mycursor.execute(sql, (agentID,))
        myresult = mycursor.fetchone()

        if myresult != None:
            self.agent = Employee(
                id=myresult[0],
                fivemID=myresult[1],
                discordID=myresult[2],
                bsn=myresult[3],
                fname=myresult[4],
                lname=myresult[5],
                pwd=myresult[6],
                dob=myresult[7],
                enabled=myresult[8]
            )

        sql = "SELECT * FROM `tbl_clients` WHERE `id` = %s;"
        mycursor = mydb.cursor(buffered=True)
        mycursor.execute(sql, (clientID,))
        myresult = mycursor.fetchone()

        if myresult != None:
            self.client = Client(
                id=myresult[0],
                fivemID=myresult[1],
                discordID=myresult[2],
                fname=myresult[3],
                lname=myresult[4],
                adres=myresult[5],
                dob=myresult[6],
                bsn=myresult[7],
                phone=myresult[8],
                crosses=myresult[9],
                licenseA=myresult[10],
                licenseB=myresult[11],
                licenseC=myresult[12],
                licenseFlight=myresult[13],
                licenseBoat=myresult[14]
            )

        sql = "SELECT * FROM `tbl_insurance_types` WHERE `id` = %s;"
        mycursor = mydb.cursor(buffered=True)
        mycursor.execute(sql, (insurance_typeID,))
        myresult = mycursor.fetchone()

        if myresult != None:
            self.insurance_type = InsuranceType(
                id=myresult[0],
                categoryID=myresult[1],
                insurable_typeID=myresult[2],
                price=myresult[3],
                min_mp=myresult[4],
                default_mp=myresult[5]
            )

            self.policy_nr = GeneratePolicyName(self)