from PyQt5.QtSql import QSqlQuery
from PyQt5.QtCore import pyqtSignal, QObject
from table import Table, SelectedTable, SelectedFieldTable
from queryConstrucorForm.queryConstructor import QueryConstructor
from expression import Expression
from collections import OrderedDict
from typing import Dict, List, Union, Tuple
import pandas as pd

class UnionTables():
    def __init__(self, query, table1: SelectedTable, union: str, table2: SelectedTable):
        self.query = query
        self.table1 = table1
        self.union = union
        self.table2 = table2
        self.conditions: List[Expression] = list()

    def setTypeUnion(self, typeUnion: str) -> None:
        """NoDocumentation"""
        self.union = typeUnion

    def setTable1(self, table: SelectedTable) -> None:
        """NoDocumentation"""
        self.table1 = table

    def setTable2(self, table: SelectedTable) -> None:
        """NoDocumentation"""
        self.table2 = table

    def addCondition(self, expression: Expression) -> None:
        """NoDocumentation"""
        self.conditions.append(expression)

    def deleteCondition(self, expression: Expression) -> None:
        """NoDocumentation"""
        pass


class XQuery(QSqlQuery, QObject):
    availableTables: Dict[str, Table] = dict()
    changedSelectedTables = pyqtSignal()
    changedSelectedFields = pyqtSignal()
    changedGroupingData = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.selectedTables: Dict[str, SelectedTable] = OrderedDict()
        self.fields: Dict[str, Expression] = OrderedDict()
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
        self.changedSelectedTables.emit()
        return selectedTable

    def addAndGetSelectedField(self, selectedFieldTable: SelectedFieldTable) -> Expression:
        """NoDocumentation"""
        alias = selectedFieldTable.name
        if alias in self.fields:
            i = 1
            while True:
                alias = selectedFieldTable.name + str(i)
                if alias in self.fields:
                    i += 1
                else:
                    break

        expression = Expression(self, selectedFieldTable, alias)
        self.fields[alias] = expression
        self.changedSelectedFields.emit()
        return expression

    def deleteSelectedTable(self, selectedTable: SelectedTable) -> None:
        """NoDocumentation"""
        del self.selectedTables[selectedTable.alias]

    def deleteSelectedField(self, expression: Expression) -> None:
        """NoDocumentation"""
        del self.fields[expression.alias]

    def addAndGetUnionAuto(self) -> Union[UnionTables, None]:
        """NoDocumentation"""
        if len(self.selectedTables) < 2:
            return None
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

    def deleteUnion(self, union) -> None:
        """NoDocumentation"""
        self.unions.remove(union)

    def addAggregaredFields(self, expression: Expression, aggregationFunction = 'SUM') -> None:
        """NoDocumentation"""
        expression.setAggregationFunction(aggregationFunction)
        self.usingGrouping = True
        self.changedGroupingData.emit()

    def deleteAggregationField(self, expression: Expression) -> None:
        """NoDocumentation"""
        expression.setAggregationFunction('')
        self.changedGroupingData.emit()


    def groupingEnabled(self, value: bool) -> None:
        """NoDocumentation"""
        self.usingGrouping = value
        self.changedGroupingData.emit()



    @classmethod
    def updateAvailableTables(cls):
        query = QSqlQuery()
        query.prepare('SELECT name, sql FROM sqlite_master WHERE type=\'table\' AND name <> \"sqlite_sequence\"')
        query.exec()

        while (query.next()):
            name = query.value('name')
            sql = query.value('sql')
            cls.availableTables[name] = Table(name, sql)

    def getPandasDataFrameUnions(self) -> pd.DataFrame:
        """NoDocumentation"""
        res = pd.DataFrame(columns=('aliasTable1', 'union', 'aliasTable2'))

        for union in self.unions:
            res.append({'aliasTable1': union.table1.alias, 'union': union.union, 'aliasTable2': union.table2.alias})

        return res

    def checkUnionsQuery(self) -> bool:
        """NoDocumentation"""
        pass

    def addAndGetCondition(self, selectedFieldTable: Union[SelectedFieldTable, None] = None) -> Expression:
        """NoDocumentation"""
        expression = Expression(self, selectedFieldTable)
        self.conditions.append(expression)
        return expression

    def deleteCondition(self, expression: Expression) -> None:
        """NoDocumentation"""
        self.conditions.remove(expression)

    def addAndGetConditionAfterGrouping(self, expression: Union[Expression, None] = None) -> Expression:
        """NoDocumentation"""
        expression = Expression(self, expression)
        self.conditionsAfterGrouping.append(expression)
        return expression

    def deleteConditionAfterGrouping(self, expression: Expression) -> None:
        """NoDocumentation"""
        self.conditionsAfterGrouping.remove(expression)



