import os
import mysql.connector
from dotenv.main import load_dotenv

class InsuranceType():
    def __init__(self, id, categoryID, insurable_typeID, price, min_mp, default_mp):
        self.id = id
        self.price = price
        self.min_mp = min_mp
        self.default_mp = default_mp
        self.categoryID = categoryID
        self.insurable_typeID = insurable_typeID

        load_dotenv()
                
        mydb = mysql.connector.connect(
            host=os.getenv('DB_SERVERNAME'),
            user=os.getenv('DB_USERNAME'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME')
        )

        sql = "SELECT * FROM `tbl_categories` WHERE `id` = %s;"
        mycursor = mydb.cursor(buffered=True)
        mycursor.execute(sql, (categoryID,))
        myresult = mycursor.fetchone()

        if myresult != None:
            self.category = Category(
                id=myresult[0],
                short_name=myresult[1],
                name=myresult[2],
                explanation=myresult[3]
            )

            sql = "SELECT * FROM `tbl_insurable_types` WHERE `id` = %s;"
            mycursor = mydb.cursor(buffered=True)
            mycursor.execute(sql, (insurable_typeID,))
            myresultnd = mycursor.fetchone()

            if myresultnd != None:
                self.insurable_type = InsurableType(
                    id=myresultnd[0],
                    short_name=myresultnd[1],
                    name=myresultnd[2],
                    subcategoryID=myresultnd[3]
                )

class InsurableType():
    def __init__(self, id, short_name, name, subcategoryID):
        self.id = id
        self.short_name = short_name
        self.name = name
        self.sub_categoryID = subcategoryID

        load_dotenv()
                
        mydb = mysql.connector.connect(
            host=os.getenv('DB_SERVERNAME'),
            user=os.getenv('DB_USERNAME'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME')
        )

        sql = "SELECT * FROM `tbl_sub_categories` WHERE `id` = %s;"
        mycursor = mydb.cursor(buffered=True)
        mycursor.execute(sql, (subcategoryID,))
        myresult = mycursor.fetchone()

        if myresult != None:
            self.sub_category = SubCategory(
                id=myresult[0],
                short_name=myresult[1],
                name=myresult[2]
            )

class Category():
    def __init__(self, id, short_name, name, explanation):
        self.id = id
        self.short_name = short_name
        self.name = name
        self.explanation = explanation

class SubCategory():
    def __init__(self, id, short_name, name):
        self.id = id
        self.short_name = short_name
        self.name = name