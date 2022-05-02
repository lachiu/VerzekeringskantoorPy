import classes.client
import classes.employee
import random
import datetime

from classes.staticclasses import InsurableType

class Insurance():
    def __init__(self, bot, agentID, clientID, insured, insurance_typeID, multiplier, amount_paid, startDate, endDate):
        self.policy_nr = None
        if bot.categories and bot.insurabletypes:
            self.policy_nr = self.GeneratePolicyName(f"{bot.categories.short_name}{bot.insurabletypes.short_name}")                    
            
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

    def GeneratePolicyName(self, verzekeringsnaam = "XX"):
        charlist = [
            0, 1, 2,
            3, 4, 5,
            6, 7, 8,
            9
        ]
        randomstring = f"{verzekeringsnaam}{datetime.today().strftime('%d%m%y')}"
        iterable = 0
        while iterable < int(5):
            randomchar = random.randrange(0, 8)
            char = charlist[randomchar]
            randomstring += f"{char}"
            iterable += 1

        self.policy_nr = randomstring