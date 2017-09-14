class BillItem:

    fields = []

    def __init__(self, wordArray):
        self.fields = wordArray[:]

    def getField(self, index):
        return self.fields[index]

    def setField(self, index, fieldValue):
        self.fields[index] = fieldValue

    def getSize(self):
        return len(self.fields)

    def pop(self, index):
        self.fields.pop(index)

    def printAll(self):
        fieldConcat = ""
        for field in self.fields:
            fieldConcat += field + " "
        print(fieldConcat)
