from PyQt5.QtSql import QSqlQuery
from table import Table, SelectedTable, SelectedFieldTable
from queryConstrucorForm.queryConstructor import QueryConstructor
from expression import Expression
from collections import OrderedDict
from typing import Dict, List

class XQuery(QSqlQuery):
    availableTables: Dict[str, Table] = dict()

    def __init__(self):
        super().__init__()
        self.selectedTables: Dict[str, SelectedTable] = dict()
        self.selectedFields: List[Expression] = list()
        self.usingGrouping = False
        self.intricateAggregation = False
        self.unions = list()
        self.joins = list()
        self.conditions = list()
        self.conditionsAfterGrouping = list()
        self.fields = dict()
        self.foundParameters = dict()

        if len(self.availableTables) == 0:
            XQuery.updateAvailableTables()

        print(self.availableTables)

    def openQueryConstructor(self) -> None:
        """NoDocumentation"""
        if hasattr(self, 'queryConsructor'):
            self.queryConsructor.show()
        else:
            self.queryConsructor = QueryConstructor(self)
            self.queryConsructor.show()

    @staticmethod
    def addAndGetSelectedTable(query: "XQuery", table: Table) -> SelectedTable:
        """NoDocumentation"""
        alias = table.name
        if alias in query.selectedTables:
            i = 1
            while True:
                alias = table.name + str(i)
                if alias in query.selectedTables:
                    i += 1
                else:
                    break

        selectedTable = SelectedTable(query, table, alias)
        query.selectedTables[table.name] = selectedTable
        return selectedTable

    @staticmethod
    def addAndGetSelectedField(query: "XQuery", selectedFieldTable: SelectedFieldTable) -> Expression:
        """NoDocumentation"""
        alias = selectedFieldTable.name
        if alias in query.selectedFields:
            i = 1
            while True:
                alias = selectedFieldTable.name + str(i)
                if alias in query.selectedFields:
                    i += 1
                else:
                    break

        expression = Expression(query, alias, selectedFieldTable)
        query.selectedFields.append(expression)
        return expression

    @staticmethod
    def deleteSelectedTable(query: "XQuery", selectedTable: SelectedTable) -> None:
        """NoDocumentation"""
        del query.selectedTables[selectedTable.alias]


    @staticmethod
    def deleteSelectedField(query: "XQuery", expression: Expression) -> None:
        """NoDocumentation"""
        query.selectedFields.remove(expression)

    @classmethod
    def updateAvailableTables(cls):
        query = QSqlQuery()
        query.prepare('SELECT name, sql FROM sqlite_master WHERE type=\'table\' AND name <> \"sqlite_sequence\"')
        query.exec()

        while (query.next()):
            name = query.value('name')
            sql = query.value('sql')
            cls.availableTables[name] = Table(name, sql)


