class InsuranceType():
    def __init__(self, id, categoryID, insurable_typeID, price, min_tmp, default_mp):
        self.id = id
        self.categoryID = categoryID
        self.insurable_typeID = insurable_typeID
        self.price = price
        self.min_tmp = min_tmp
        self.default_mp = default_mp

class InsurableType():
    def __init__(self, id, short_name, name, subcategoryID):
        self.id = id
        self.short_name = short_name
        self.name = name
        self.subcategoryID = subcategoryID

class Category():
    def __init__(self, id, short_name, name):
        self.id = id
        self.short_name = short_name
        self.name = name

class SubCategory():
    def __init__(self, id, short_name, name):
        self.id = id
        self.short_name = short_name
        self.name = name