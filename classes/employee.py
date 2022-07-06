class Employee():
    def __init__(self, id, fivemID, discordID, bsn, fname, lname, pwd, dob, enabled):
        def set_bsn(self, value):    
            while len(value) < 6:
                value = "0" + value
            
            return f"NL{value}"
        
        self.id = id
        self.fivemID = fivemID
        self.discordID = discordID
        self.bsn = set_bsn(self, str(bsn))
        self.fname = fname
        self.lname = lname
        self.pwd = pwd        
        self.dob = dob
        self.enabled = enabled        