class Client():
    def __init__(self, id, fivemID, discordID, fname, lname, adres, dob, bsn, phone, crosses, licenseA, licenseB, licenseC, licenseFlight, licenseBoat):
        def set_bsn(self, value):
            while len(value) < 6:
                value = "0" + value

            return f"NL{value}"

        self.id = id
        self.fivemID = fivemID
        self.discordID = discordID
        self.fname = fname
        self.lname = lname
        self.adres = adres
        self.dob = dob
        self.bsn = set_bsn(self, str(bsn))
        self.phone = phone
        self.crosses = crosses
        self.licenseA = licenseA
        self.licenseB = licenseB
        self.licenseC = licenseC
        self.licenseFlight = licenseFlight
        self.licenseBoat = licenseBoat