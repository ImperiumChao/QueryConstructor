import re
import string
# from xQuery import XQuery
from typing import Dict, List, Union, Tuple


class Table():

    def __init__(self, name: str, fields=[], query=None):
        self.name = name
        self.query = query

        if not query is None:
            self.fields = list()
            for field in self.query.fields:
                self.fields.append(FieldTable(self, name=field.alias))
        else:
            self.fields = list()
            for field in fields:
                self.fields.append(FieldTable(self, name=field.name, referencePath=field.reference))

    def __str__(self):
        return self.name

    @classmethod
    def findReferences(cls):
        for path, field in FieldTable.fields.items():
            if field.referencePath != '':
                field.fieldTableReference = FieldTable.fields[field.referencePath]


class FieldTable():
    fields = dict()

    def __init__(self, table: Table, name: str = '', referencePath=''):
        self.table = table
        self.name = name
        if referencePath == None:
            self.referencePath = ''
        else:
            self.referencePath = referencePath
        self.fieldTableReference = None
        self.path = f'{self.table.name}.{self.name}'
        self.fields[self.path] = self

    def __str__(self):
        return self.path

    def __del__(self):
        self.fields.remove(self)


class SelectedTable():
    def __init__(self, query, table: Table, alias: str):
        self.query = query
        self.table = table
        self.alias = alias
        self.fields = list()
        for field in table.fields:
            self.fields.append(SelectedFieldTable(self, field))

    def __str__(self):
        return self.alias

    def getSelectedField(self, field: FieldTable) -> "SelectedFieldTable":
        """NoDocumentation"""
        tmp = [f for f in self.fields if f.fieldTable == field]
        return tmp[0]


class SelectedFieldTable():
    def __init__(self, selectedTable: "SelectedTable", fildTable: FieldTable):
        self.table = selectedTable.table
        self.selectedTable = selectedTable
        self.fieldTable = fildTable
        self.name = self.fieldTable.name
        self.path = f'{self.selectedTable.alias}.{self.name}'

    def __str__(self):
        return self.path
