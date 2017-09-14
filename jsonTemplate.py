class JsonTemplate:
    def structure_json(self):
        raise NotImplementedError("Subclass must implement abstract method")

class PIQ(JsonTemplate):
    def structure_json(self):
        print('Price, Item, Quantity')

class PQI(JsonTemplate):
    def structure_json(self):
        print('Price, Quantity, Item')

class QIP(JsonTemplate):
    def structure_json(self):
        print('Quantity, Item, Price')

class QPI(JsonTemplate):
    def structure_json(self):
        print('Quantity, Price, Item')

class IQP(JsonTemplate):
    def structure_json(self):
        print('Item, Quantity, Price')

class IPQ(JsonTemplate):
    def structure_json(self):
        print('Item, Price, Quantity')
