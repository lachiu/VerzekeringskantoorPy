class InsuranceTypes():
    def __init__(self, id, categoryID, insurable_typeID, price, min_tmp, default_mp):
        self.id = id
        self.categoryID = categoryID
        self.insurable_typeID = insurable_typeID
        self.price = price
        self.min_tmp = min_tmp
        self.default_mp = default_mp

class InsurableTypes():
    def __init__(self, id, short_name, name, subcategoryID):
        self.id = id
        self.short_name = short_name
        self.name = name
        self.subcategoryID = subcategoryID

class Categories():
    def __init__(self, id, short_name, name):
        self.id = id
        self.short_name = short_name
        self.name = name

class SubCategories():
    def __init__(self, id, short_name, name):
        self.id = id
        self.short_name = short_name
        self.name = name