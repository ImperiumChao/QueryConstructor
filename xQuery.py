from PyQt5.QtSql import QSqlQuery
from PyQt5.QtCore import pyqtSignal, QObject
from table import Table, SelectedTable, SelectedFieldTable
from queryConstrucorForm.queryConstructor import QueryConstructor
from expression import Expression
from collections import OrderedDict
from typing import Dict, List, Union, Tuple
import pandas as pd
from types import SimpleNamespace


class JoinTables():
    def __init__(self, query, table1: SelectedTable, join: str, table2: SelectedTable):
        self.query = query
        self.table1 = table1
        self.join = join
        self.table2 = table2
        self.conditions: List[Expression] = list()

    def setTypeJoin(self, typeJoin: str) -> None:
        """NoDocumentation"""
        self.join = typeJoin
        self.query.needUpdateTextQuery.emit()


    def setTable1(self, table: SelectedTable) -> None:
        """NoDocumentation"""
        self.table1 = table
        self.query.needUpdateTextQuery.emit()


    def setTable2(self, table: SelectedTable) -> None:
        """NoDocumentation"""
        self.table2 = table
        self.query.needUpdateTextQuery.emit()

    def addCondition(self, expression: Expression) -> None:
        """NoDocumentation"""
        self.conditions.append(expression)
        self.query.needUpdateTextQuery.emit()

    def deleteCondition(self, expression: Expression) -> None:
        """NoDocumentation"""
        self.conditions.remove(expression)
        self.query.needUpdateTextQuery.emit()


class XQuery(QSqlQuery, QObject):
    availableTables: Dict[str, Table] = dict()

    changedSelectedTables = pyqtSignal()
    changedFieldsQuery = pyqtSignal()
    changedGroupingData = pyqtSignal()
    changedJoins = pyqtSignal()
    changedConditions = pyqtSignal()
    changedConditionsAfterGrouping = pyqtSignal()
    changedFieldsOrderBy = pyqtSignal()
    needUpdateTextQuery = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.selectedTables: Lict[SelectedTable] = list()
        self.fields: List[Expression] = list()
        self.joins: List[JoinTables] = list()
        self.unions: List[SimpleNamespace] = list()
        self.conditions: List[Expression] = list()
        self.conditionsAfterGrouping: List[Expression] = list()
        self.orderBy: List[SimpleNamespace] = list()
        # self.foundParameters: Dict[str, str] = dict()
        self.usingGrouping = False
        self.intricateAggregation = False

        self.needUpdateTextQuery.connect(self.updateTextQuery)
        if len(self.availableTables) == 0:
            XQuery.updateAvailableTables()

        print(self.availableTables)

    def updateTextQuery(self) -> None:
        """NoDocumentation"""
        indent = ' ' * 4
        res = 'SELECT \n'
        fields = [f'{expression.rawSqlText} AS {expression.alias}' for expression in self.fields]
        res += indent + f',\n{indent}'.join(fields)

        if len(self.selectedTables) == 0:
            self.queryConsructor.textQuery.setText(res)
            return


        res += '\nFROM \n'

        tablesWithJoins = set()
        tablesWithoutJoins = set()
        for selectedtable in self.selectedTables:
            if self.find(self.joins, 'table1', selectedtable) != None or\
                    self.find(self.joins, 'table2', selectedtable) != None:
                tablesWithJoins.add(selectedtable)
            else:
                tablesWithoutJoins.add(selectedtable)


        # if len(self.joins) != 0:
        #     joins = self.joins.copy()
        #     while True:
        #         firstTable = None
        #         for selectedtable in tablesWithJoins:
        #             if firstTable != None:
        #                 break
        #             for join in joins:
        #                 if selectedtable in (join.table1, join.table2):
        #                     if join.join == 'LEFT' and selectedtable == join.table2:
        #                         continue
        #                     elif join.join == 'RIGHT' and selectedtable == join.table1:
        #                         continue
        #                     else:
        #                         firstTable = selectedtable
        #                         break
        #
        #         res += f'{firstTable.table.name} AS {firstTable.alias}'
        #         res += self.getTextJoinsForTable(firstTable, joins)
        #
        #
        #         if len(joins) == 0:
        #             break

        res += indent + f', \n{indent}'.join([f'{selectedTable.table.name} AS {selectedTable.alias}' for selectedTable in tablesWithoutJoins])

        if len(self.conditions)!=0:
            res += '\nWHERE \n'
            res += indent + f', \n{indent}'.join([condition.rawSqlText for condition in self.conditions])

        if len(self.orderBy)!=0:
            def orderby_text(expression):
                typeOfSorting = expression.typeOfSorting
                if typeOfSorting == 'ASC':
                    typeOfSorting = ''
                return f'{expression.field.alias} {typeOfSorting}'

            res += '\nORDER BY \n'
            res += indent + f', \n{indent}'.join([orderby_text(expression) for expression in self.orderBy])
        self.queryConsructor.textQuery.setText(res)


    def getTextJoinsForTable(self, table: SelectedTable, joins: List[JoinTables]) -> str:
        """NoDocumentation"""
        res = ''
        for join in joins:
            if not table in (join.table1, join.table2):
                continue

            if table == join.table1:
                joinedTable = join.table2
            else:
                joinedTable = join.table1

            res += f'\n{join.join} JOIN {joinedTable.table.name} AS {joinedTable.alias}\n'
            joinscopy = joins.copy()
            joinscopy.remove(join)
            # res += self.getTextJoinsForTable(joinedTable, joinscopy)
            res += 'ON '
            conditions = list()
            for expression in join.conditions:
                conditions.append(expression.rawSqlText)
            res += ' AND '.join(conditions)
        return res


    def openQueryConstructor(self) -> None:
        """NoDocumentation"""
        if hasattr(self, 'queryConsructor'):
            self.queryConsructor.show()
        else:
            self.queryConsructor = QueryConstructor(self)
            self.queryConsructor.show()

    def addSelectedTable(self, table: Table, noSignal=False) -> SelectedTable:
        """NoDocumentation"""
        alias = table.name
        i = 0
        while True:
            searchValue = XQuery.find(self.selectedTables, 'alias', alias)
            if searchValue == None:
                break
            i += 1
            alias = table.name + str(i)

        selectedTable = SelectedTable(self, table, alias)
        self.selectedTables.append(selectedTable)
        self.needUpdateTextQuery.emit()
        if not noSignal:
            self.changedSelectedTables.emit()
        return selectedTable

    def addFieldQuery(self, selectedFieldTable: SelectedFieldTable, noSignal=False) -> Expression:
        """NoDocumentation"""
        alias = selectedFieldTable.name
        i = 0
        while True:
            searchValue = XQuery.find(self.fields, 'alias', alias)
            if searchValue == None:
                break
            i += 1
            alias = selectedFieldTable.name + str(i)

        expression = Expression(self, selectedFieldTable, alias)
        self.fields.append(expression)
        self.needUpdateTextQuery.emit()

        if not noSignal:
            self.changedFieldsQuery.emit()
        return expression

    def deleteSelectedTable(self, selectedTable: SelectedTable, noSignal=False) -> None:
        """NoDocumentation"""
        self.selectedTables.remove(selectedTable)
        self.needUpdateTextQuery.emit()
        if not noSignal:
            self.changedSelectedTables.emit()

    def deleteFieldQuery(self, expression: Expression, noSignal=False) -> None:
        """NoDocumentation"""
        self.fields.remove(expression)
        self.needUpdateTextQuery.emit()
        if not noSignal:
            self.changedFieldsQuery.emit()

    def addJoinAuto(self, noSignal=False) -> Union[JoinTables, None]:
        """NoDocumentation"""
        if len(self.selectedTables) < 2:
            return None
        alreadyUnitedTables = set()
        table1 = self.selectedTables[0]
        alreadyUnitedTables.add(table1)

        for join in self.joins:
            alreadyUnitedTables.add(join.table1)
            alreadyUnitedTables.add(join.table2)

        if len(alreadyUnitedTables) == len(self.selectedTables):
            return None

        for selectedTable in self.selectedTables:
            if not selectedTable in alreadyUnitedTables:
                table2 = selectedTable
                joinTables = JoinTables(self, table1, 'INNER', table2)
                self.joins.append(joinTables)
                return joinTables
        self.needUpdateTextQuery.emit()
        if not noSignal:
            self.changedJoins.emit()

    def deleteJoin(self, joins, noSignal=False) -> None:
        """NoDocumentation"""
        self.joins.remove(joins)
        self.needUpdateTextQuery.emit()
        if not noSignal:
            self.changedJoins.emit()

    def addAggregaredFields(self, expression: Expression, noSignal=False) -> None:
        """NoDocumentation"""
        expression.setAggregationFunction('SUM')
        self.usingGrouping = True
        self.needUpdateTextQuery.emit()
        if not noSignal:
            self.changedGroupingData.emit()


    def deleteAggregationField(self, expression: Expression, noSignal=False) -> None:
        """NoDocumentation"""
        expression.setAggregationFunction('')
        self.needUpdateTextQuery.emit()
        if not noSignal:
            self.changedGroupingData.emit()

    def setGroupingEnabled(self, value: bool, noSignal=False) -> None:
        """NoDocumentation"""
        self.usingGrouping = value
        self.needUpdateTextQuery.emit()
        if not noSignal:
            self.changedGroupingData.emit()


    def addUnionQuery(self) -> 'XQuery':
        """NoDocumentation"""
        query = XQuery()
        union = SimpleNamespace()
        union.query = query
        union.union = 'UNION'
        self.unions.append(union)
        return query

    def deleteUnionQuery(self, query) -> None:
        """NoDocumentation"""
        self.unions.remove(self.find(self.unions, 'query', query))

    def moveField(self, index: int, up: bool, noSignal=False) -> None:
        """NoDocumentation"""
        if up:
            self.fields[index], self.fields[index - 1] = self.fields[index - 1], self.fields[index]
        else:
            self.fields[index], self.fields[index + 1] = self.fields[index + 1], self.fields[index]
        self.needUpdateTextQuery.emit()
        if not noSignal:
            self.changedFieldsQuery.emit()

    def checkJoinsQuery(self) -> bool:
        """NoDocumentation"""
        pass

    def addCondition(self, selectedFieldTable: Union[SelectedFieldTable, None] = None, noSignal=False) -> Expression:
        """NoDocumentation"""
        expression = Expression(self, selectedFieldTable)
        self.conditions.append(expression)
        self.needUpdateTextQuery.emit()
        if not noSignal:
            self.changedConditions.emit()
        return expression

    def deleteCondition(self, expression: Expression, noSignal=False) -> None:
        """NoDocumentation"""
        self.conditions.remove(expression)
        self.needUpdateTextQuery.emit()
        if not noSignal:
            self.changedConditions.emit()

    def addConditionAfterGrouping(self, expression: Union[Expression, None] = None, noSignal=False) -> Expression:
        """NoDocumentation"""
        expression = Expression(self, expression)
        self.conditionsAfterGrouping.append(expression)
        self.needUpdateTextQuery.emit()
        if not noSignal:
            self.changedConditionsAfterGrouping.emit()
        return expression

    def deleteConditionAfterGrouping(self, expression: Expression, noSignal=False) -> None:
        """NoDocumentation"""
        self.conditionsAfterGrouping.remove(expression)
        self.needUpdateTextQuery.emit()
        if not noSignal:
            self.changedConditionsAfterGrouping.emit()

    def addFieldOrderBy(self, _object: Union[Expression, SelectedFieldTable], noSignal=False) -> SimpleNamespace:
        """NoDocumentation"""

        orderBy = SimpleNamespace()
        orderBy.field = _object
        orderBy.typeOfSorting = 'ASC'
        self.orderBy.append(orderBy)
        self.needUpdateTextQuery.emit()
        if not noSignal:
            self.changedFieldsOrderBy.emit()
        return orderBy

    def deleteFieldOrderBy(self, _object, noSignal=False) -> None:
        """NoDocumentation"""
        self.orderBy.remove(_object)
        self.needUpdateTextQuery.emit()
        if not noSignal:
            self.changedFieldsOrderBy.emit()

    def setTypeOfSorting(self, _object, typeOfSorting: str, noSignal=False) -> None:
        """NoDocumentation"""
        _object.typeOfSorting = typeOfSorting
        self.needUpdateTextQuery.emit()
        if not noSignal:
            self.changedFieldsOrderBy.emit()


    @classmethod
    def updateAvailableTables(cls):
        query = QSqlQuery()
        query.prepare('SELECT name, sql FROM sqlite_master WHERE type=\'table\' AND name <> \"sqlite_sequence\"')
        query.exec()

        while (query.next()):
            name = query.value('name')
            sql = query.value('sql')
            cls.availableTables[name] = Table(name, sql)

    def getPandasDataFrameJoins(self) -> pd.DataFrame:
        """NoDocumentation"""
        res = pd.DataFrame(columns=('aliasTable1', 'join', 'aliasTable2'))

        for join in self.joins:
            res.append({'aliasTable1': join.table1.alias, 'join': join.join, 'aliasTable2': join.table2.alias})

        return res

    @staticmethod
    def find(objects: object, attribute: str, value: object) -> object:
        """NoDocumentation"""
        for ob in objects:
            if getattr(ob, attribute) == value:
                return ob
        return None
