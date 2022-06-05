from PyQt5.QtSql import QSqlQuery
from table import Table, SelectedTable, SelectedFieldTable
from queryConstrucorForm.queryConstructor import QueryConstructor
from expression import Expression
from collections import OrderedDict
from typing import Dict, List, Union, Tuple

class UnionTables():
    def __init__(self, query, table1: SelectedTable, union: str, table2: SelectedTable):
        self.table1 = table1
        self.union = union
        self.table2 = table2
        self.conditions: List[Expression] = list()

class XQuery(QSqlQuery):
    availableTables: Dict[str, Table] = dict()

    def __init__(self):
        super().__init__()
        self.selectedTables: Dict[str, SelectedTable] = OrderedDict()
        self.fields: Dict[str, SelectedTable] = OrderedDict()
        self.unions: List[UnionTables] = list()
        self.joins: List['XQuery'] = list()
        self.conditions: List[Expression] = list()
        self.conditionsAfterGrouping: List[Expression] = list()
        self.sorting: List[Union[SelectedFieldTable, Expression]]
        # self.foundParameters: Dict[str, str] = dict()
        self.usingGrouping = False
        self.intricateAggregation = False

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

    def addAndGetSelectedTable(self, table: Table) -> SelectedTable:
        """NoDocumentation"""
        alias = table.name
        if alias in self.selectedTables:
            i = 1
            while True:
                alias = table.name + str(i)
                if alias in self.selectedTables:
                    i += 1
                else:
                    break

        selectedTable = SelectedTable(self, table, alias)
        self.selectedTables[table.name] = selectedTable
        return selectedTable

    def addAndGetSelectedField(self, selectedFieldTable: SelectedFieldTable) -> Expression:
        """NoDocumentation"""
        alias = selectedFieldTable.name
        if alias in self.fields:
            i = 1
            while True:
                alias = selectedFieldTable.name + str(i)
                if alias in query.fields:
                    i += 1
                else:
                    break

        expression = Expression(self, selectedFieldTable, alias)
        self.fields[alias] = expression
        return expression

    @staticmethod
    def deleteSelectedTable(query: "XQuery", selectedTable: SelectedTable) -> None:
        """NoDocumentation"""
        del query.selectedTables[selectedTable.alias]


    @staticmethod
    def deleteSelectedField(query: "XQuery", expression: Expression) -> None:
        """NoDocumentation"""
        query.fields.remove(expression)

    def addAndGetUnionAuto(self) -> Union[UnionTables, None]:
        """NoDocumentation"""

        alreadyUnitedTables = set()
        table1 = list(self.selectedTables.values())[0]
        alreadyUnitedTables.add(table1)

        for union in self.unions:
            alreadyUnitedTables.add(union.table1)
            alreadyUnitedTables.add(union.table2)

        if len(alreadyUnitedTables) == len(self.selectedTables):
            return None

        for _, selectedTable in self.selectedTables.items():
            if not selectedTable in alreadyUnitedTables:
                table2 = selectedTable
                unionTables = UnionTables(self, table1, 'INNER', table2)
                self.unions.append(unionTables)
                return unionTables




    @classmethod
    def updateAvailableTables(cls):
        query = QSqlQuery()
        query.prepare('SELECT name, sql FROM sqlite_master WHERE type=\'table\' AND name <> \"sqlite_sequence\"')
        query.exec()

        while (query.next()):
            name = query.value('name')
            sql = query.value('sql')
            cls.availableTables[name] = Table(name, sql)






