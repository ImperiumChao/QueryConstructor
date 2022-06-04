import re
import string


class Table():
    def __init__(self, name: str, sqlText: str):
        self.name = name
        self.sqlText = sqlText

        self.createFields(self.sqlText)

    def __str__(self):
        return self.name

    def createFields(self, sqlText: str) -> None:
        """NoDocumentation"""
        textInParentheses = sqlText[sqlText.find('('):sqlText.find(');')]
        textInParentheses = textInParentheses.replace('(', '')
        textInParentheses = textInParentheses.replace(')', '')
        textInParentheses = textInParentheses.replace('\"', '')
        textInParentheses = textInParentheses.replace('`', '')
        textInParentheses = textInParentheses.replace('\t', ' ')
        textInParentheses = textInParentheses.replace('\n', ' ')
        textInParentheses = textInParentheses.strip()

        for i in range(10):
            textInParentheses = textInParentheses.replace('  ', ' ')

        descriptionFields = textInParentheses.split(',')
        self.fields = list()

        for sqlField in descriptionFields:
            sqlField = sqlField.strip()
            if sqlField.find('FOREIGN KEY') == -1:
                self.fields.append(FieldTable(self, sqlField))

class FieldTable():
    def __init__(self, table: Table, sqlCreateTable: str):
        self.table = table
        self.sqlCreateTable = sqlCreateTable
        self.name = sqlCreateTable[0:sqlCreateTable.find(' ')]

        text = sqlCreateTable[len(self.name):].strip()
        self.typeField = text.split(' ')[0]

    def __str__(self):
        return f'{self.table.name}.{self.name}'


class SelectedTable():
    def __init__(self, query, table: Table, alias: str):
        self.query = query
        self.table = table
        self.alias = alias
        self.fields = dict()
        for field in table.fields:
            self.fields[field] = SelectedFieldTable(self, field)
    def __str__(self):
        return self.alias

    def getSelectedField(self, field: FieldTable) -> "SelectedFieldTable":
        """NoDocumentation"""
        return self.fields[field]



class SelectedFieldTable():
    def __init__(self, selectedTable: "SelectedTable", fildTable: FieldTable):
        self.table = selectedTable.table
        self.selectedTable = selectedTable
        self.fieldTable = fildTable
        self.name = self.fieldTable.name
        self.path = f'{self.selectedTable.alias}.{self.name}'

    def __str__(self):
        return self.path







