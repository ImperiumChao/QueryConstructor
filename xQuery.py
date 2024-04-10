from PyQt5.QtSql import QSqlQuery
from PyQt5.QtCore import pyqtSignal, QObject
from table import Table, SelectedTable, SelectedFieldTable
from queryConstrucorForm.queryConstructor import QueryConstructor
from expression import Expression
from collections import OrderedDict, Counter, namedtuple
from typing import Dict, List, Union, Tuple
from itertools import count, combinations
from types import SimpleNamespace
from enum import Enum

import pandas as pd
import re
import pickle


class TypesQuery(Enum):
    main = 1
    union = 2
    unionAll = 3
    temp = 4
    subQuery = 5


class JoinTables():
    def __init__(self, query, table1: SelectedTable, join: str, table2: SelectedTable):
        self.query = query
        self.table1 = table1
        self.join = join
        self.table2 = table2
        self.conditions: List[Expression] = self.getJoinAuto()

    def getJoinAuto(self):

        for fieldTable1 in self.table1.fields:
            for fieldTable2 in self.table2.fields:
                if fieldTable1.fieldTable.fieldTableReference == fieldTable2.fieldTable or \
                        fieldTable2.fieldTable.fieldTableReference == fieldTable1.fieldTable:
                    return [Expression(self.query, _object=self, rawSqlText=f'{fieldTable1.path} = {fieldTable2.path}')]
        return [Expression(self.query, _object=self, rawSqlText='TRUE')]

    def setTypeJoin(self, typeJoin: str) -> None:
        """NoDocumentation"""
        self.join = typeJoin
        type(self.query).updateTextQueries()
        # self.query.needUpdateTextQuery.emit()

    def setTable1(self, table: SelectedTable, noSignal=False) -> None:
        """NoDocumentation"""
        self.table1 = table
        if not noSignal:
            self.query.needUpdateTextQuery.emit()

    def setTable2(self, table: SelectedTable, noSignal=False) -> None:
        """NoDocumentation"""
        self.table2 = table
        if not noSignal:
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
    tablesDB: Dict[str, Table] = dict()
    tablesTemp: List[Table] = list()
    subqueries: List[Table] = list()
    parameters: Dict[str, str] = dict()
    mainQuery: 'XQuery' = None
    queryConstructor = None
    typeDB = 'SQLITE'

    changedSelectedTables = pyqtSignal()
    changedFieldsQuery = pyqtSignal()
    changedGroupingData = pyqtSignal()
    changedJoins = pyqtSignal()
    changedConditions = pyqtSignal()
    changedConditionsAfterGrouping = pyqtSignal()
    changedFieldsOrderBy = pyqtSignal()
    needUpdateTextQuery = pyqtSignal()
    addedUnionQuery = pyqtSignal(object)
    changedAvailableTables = pyqtSignal()

    def __init__(self):
        super().__init__()
        if XQuery.mainQuery is None:
            XQuery.mainQuery = self

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
        self.isUnionQuery = False
        self.name = '*main*'
        self.type = TypesQuery.main
        # self.parameters = dict()
        self.textQuery = ''
        self.queryForUnion = None
        self.needUpdateTextQuery.connect(lambda: XQuery.updateTextQueries)

    @classmethod
    def addQuery(cls):
        cls.mainQuery.type = TypesQuery.temp

        namesTables = [table.name for table in XQuery.tablesTemp]
        for i in count(1):
            newName = f'query{i}'
            if newName not in namesTables:
                XQuery.mainQuery.name = newName
                break

        cls.tablesTemp.append(Table(XQuery.mainQuery.name, query=XQuery.mainQuery))
        cls.mainQuery = cls()
        cls.updateTextQueries()

        return cls.mainQuery

    @classmethod
    def updateTextQueries(cls):
        for table in cls.subqueries * 4 + cls.tablesTemp:
            table.query.updateTextQuery()

        cls.mainQuery.updateTextQuery()
        cls.updateParameters()
        cls.queryConstructor.textQuery.setText(cls.mainQuery.textQuery)
        cls.queryConstructor.updateParameters()

    def updateTextQuery(self) -> None:
        """NoDocumentation"""
        indent = ' ' * 4
        tablesTemp = []
        for table in XQuery.tablesTemp:
            if table.query == self or table.query.queryForUnion == self:
                break
            tablesTemp.append(self.getTextQuery(table.query, table.name))

        tablesTemp.append('')
        separator = '\n;\n' + '/' * 80 + '\n'
        self.textQuery = separator.join(tablesTemp)

        self.textQuery += self.getTextQuery(self, basic=True)

        # self.updateParameters()
        # if self == XQuery.mainQuery:
        #     XQuery.queryConstructor.updateTextQuery()

    @classmethod
    def updateParameters(cls):
        prevParameters = cls.parameters.copy()
        cls.parameters.clear()

        queries = [table.query.textQuery for table in cls.tablesTemp] \
                  + [table.query.textQuery for table in cls.subqueries] + [cls.mainQuery.textQuery]

        textAllQueries = ' '.join(queries)

        cls.parameters = {param: prevParameters.setdefault(param) for param in
                          re.findall(':[a-zA-Z]\w+', textAllQueries)}

    @classmethod
    def getTextQuery(cls, query, nameTableTemp='', basic=False) -> str:
        query.usingGrouping = sum([field.hasAggregation for field in query.fields]) > 0

        indent = ' ' * 4
        if query.type == TypesQuery.temp and not basic:
            if XQuery.typeDB == 'SQLITE':
                res = f'CREATE TABLE {nameTableTemp} AS SELECT \n'
            else:
                pass
        else:
            res = 'SELECT \n'

        if query.type in (TypesQuery.union, TypesQuery.unionAll):
            fields = [expression.rawSqlText for expression in query.fields]
        else:
            fields = [f'{expression.rawSqlText} AS {expression.alias}' for expression in query.fields]
        res += indent + f',\n{indent}'.join(fields)

        if len(query.selectedTables) == 0:
            return res

        res += '\nFROM \n'

        tablesWithJoins = set()
        tablesWithoutJoins = set()

        tablesWithJoins = {join.table1 for join in query.joins} | {join.table2 for join in query.joins}
        tablesWithoutJoins = set(query.selectedTables) - tablesWithJoins

        joins = query.joins.copy()
        while (len(joins) > 0):
            table = query.getStartingTable(joins)
            res += query.getChainJoinsForTable(table, joins)

        def viewTable(selTable):
            if selTable.alias == '':
                return selTable.table.name
            else:
                return f'{selTable.table.name} AS {selTable.alias}'

        tables = [viewTable(selectedTable)
                  for selectedTable in tablesWithoutJoins \
                  if selectedTable.table.query is None or selectedTable.table.query.type != TypesQuery.subQuery]

        def addIndents(text: str):
            strings = text.split('\n')
            firstString = strings[0]
            strings = list(map(lambda el: indent + el, strings))
            strings[0] = firstString
            return '\n'.join(strings)

        tablesSubquerys = [f'({addIndents(cls.getTextQuery(selectedTable.table.query))}) AS {selectedTable.alias}' \
                           for selectedTable in tablesWithoutJoins \
                           if
                           not selectedTable.table.query is None and selectedTable.table.query.type == TypesQuery.subQuery]

        res += indent + f', \n{indent}'.join(tables + tablesSubquerys)

        if len(query.conditions) != 0:
            res += '\nWHERE \n'
            res += indent + f', \n{indent}'.join([condition.rawSqlText for condition in query.conditions])

        if query.usingGrouping:
            groupBy = [field.rawSqlText for field in query.fields if not field.hasAggregation]
            if len(groupBy) > 0:
                res += '\nGROUP BY \n'
                res += indent + f', \n{indent}'.join(groupBy)

        if len(query.conditionsAfterGrouping) != 0:
            res += '\nHAVING \n'
            res += indent + f', \n{indent}'.join([condition.rawSqlText for condition in query.conditionsAfterGrouping])

        if len(query.unions) != 0:
            for union in query.unions:
                res += f'\n\n{union.union}\n\n{cls.getTextQuery(union.query)}'

        if len(query.orderBy) != 0 and basic:
            def orderby_text(expression):
                typeOfSorting = expression.typeOfSorting
                if typeOfSorting == 'ASC':
                    typeOfSorting = ''
                return f'{expression.field.alias} {typeOfSorting}'

            res += '\nORDER BY \n'
            res += indent + f', \n{indent}'.join([orderby_text(expression) for expression in query.orderBy])
        return res

    def getStartingTable(self, joins: list):
        counter = Counter()
        for join in joins:
            if not self.tableIsSubordinate(join.table1):
                counter.update({join.table1: 1})
            if not self.tableIsSubordinate(join.table2):
                counter.update({join.table2: 1})

        return counter.most_common(1)[0][0]

    def getChainJoinsForTable(self, table: SelectedTable, joins: list, level: int = 0):
        level += 1
        indent = '    '

        joinsTable = []
        for join in joins:
            if table in (join.table1, join.table2):
                joinsTable.append(join)

        for join in joinsTable:
            joins.remove(join)

        if not table.table.query is None and table.table.query.type == TypesQuery.subQuery:
            textSubQuery = self.getTextQuery(table.table.query)
            textSubQuery.replace('\n', '\n' + level * indent)
            res = f'({textSubQuery}) AS {table.alias}'
        else:
            res = f'{table.table.name} AS {table.alias}'
        for join in joinsTable:
            if join.table1 == table:
                tableForJoin = join.table2
            else:
                tableForJoin = join.table1
            res += f'\n{indent * level}{join.join} JOIN {self.getChainJoinsForTable(tableForJoin, joins, level)}'
            separator = f'\n{indent * (level + 1)}AND '
            if len(join.conditions) != 0:
                res += f'\n{indent * level}ON {separator.join([el.rawSqlText for el in join.conditions])}'
            else:
                res += f'\n{indent * level}ON TRUE'
        return res

    def tableIsSubordinate(self, table: SelectedTable, tableIgnore: SelectedTable | None = None) -> bool:

        for join in self.joins:
            if join.join == 'LEFT' and join.table2 == table:
                return True

            if table == join.table1 and tableIgnore != join.table2 and join.join != 'LEFT':
                if self.tableIsSubordinate(join.table2, table):
                    return True

            if table == join.table2 and tableIgnore != join.table1:
                if self.tableIsSubordinate(join.table1, table):
                    return True

        return False

    def getQueryConstructor(self) -> QueryConstructor:
        """NoDocumentation"""
        # if XQuery.queryConstructor is None:
        XQuery.queryConstructor = QueryConstructor(self)
        return XQuery.queryConstructor
        # else:
        #     XQuery.queryConstructor.show()

    def addSelectedTable(self, table: Table, noSignal=False) -> SelectedTable:
        """NoDocumentation"""
        tableName = table.name.split('.')[-1]

        aliases = [table.alias for table in self.selectedTables]
        if tableName not in aliases:
            alias = tableName
        else:
            for i in count(1):
                if tableName + str(i) not in aliases:
                    alias = tableName + str(i)
                    break

        selectedTable = SelectedTable(self, table, alias)
        self.selectedTables.append(selectedTable)
        if not noSignal:
            self.changedSelectedTables.emit()

        # self.needUpdateTextQuery.emit()
        XQuery.updateTextQueries()
        return selectedTable

    def addFieldQuery(self, field: Union[SelectedFieldTable, None] = None, noSignal=False) -> Expression:
        """NoDocumentation"""
        if field == None:
            fieldName = 'field'
        else:
            fieldName = field.name

        aliases = [field.alias for field in self.fields]
        if fieldName not in aliases:
            alias = fieldName
        else:
            for i in count(1):
                if fieldName + str(i) not in aliases:
                    alias = fieldName + str(i)
                    break

        expression = Expression(self, field, alias)
        self.fields.append(expression)
        XQuery.updateTextQueries()

        if not noSignal:
            self.changedFieldsQuery.emit()
        return expression

    def addExpression(self, rawSqlText, alias='', noSignal=False):
        fieldName = 'field'

        aliases = [field.alias for field in self.fields]
        if fieldName not in aliases:
            alias = fieldName
        else:
            for i in count(1):
                if fieldName + str(i) not in aliases:
                    alias = fieldName + str(i)
                    break
        expression = Expression(self, alias=alias)
        expression.setRawSqlText(rawSqlText)

        self.fields.append(expression)
        XQuery.updateTextQueries()

        if not noSignal:
            self.changedFieldsQuery.emit()
        return expression

    def deleteSelectedTable(self, selectedTable: SelectedTable, noSignal=False) -> None:
        """NoDocumentation"""
        self.selectedTables.remove(selectedTable)
        XQuery.updateTextQueries()
        if not noSignal:
            self.changedSelectedTables.emit()

    def deleteFieldQuery(self, expression: Expression, noSignal=False) -> None:
        """NoDocumentation"""
        self.fields.remove(expression)
        XQuery.updateTextQueries()
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
                XQuery.updateTextQueries()
                if not noSignal:
                    self.changedJoins.emit()
                return joinTables

    def deleteJoin(self, joins, noSignal=False) -> None:
        """NoDocumentation"""
        self.joins.remove(joins)
        XQuery.updateTextQueries()
        if not noSignal:
            self.changedJoins.emit()

    def addAggregaredFields(self, expression: Expression, noSignal=False) -> None:
        """NoDocumentation"""
        expression.setAggregationFunction('SUM')
        self.usingGrouping = True
        XQuery.updateTextQueries()
        if not noSignal:
            self.changedGroupingData.emit()

    def deleteAggregationField(self, expression: Expression, noSignal=False) -> None:
        """NoDocumentation"""
        expression.setAggregationFunction('')
        XQuery.updateTextQueries()
        if not noSignal:
            self.changedGroupingData.emit()

    def setGroupingEnabled(self, value: bool, noSignal=False) -> None:
        """NoDocumentation"""
        self.usingGrouping = value
        XQuery.updateTextQueries()
        if not noSignal:
            self.changedGroupingData.emit()

    def addUnionQuery(self) -> 'XQuery':
        """NoDocumentation"""
        query = XQuery()
        query.name = 'unionAll'
        query.queryForUnion = self
        query.type = TypesQuery.unionAll
        union = SimpleNamespace()
        union.query = query
        union.union = 'UNION'
        self.unions.append(union)
        self.addedUnionQuery.emit(query)
        return query

    def deleteUnionQuery(self, query) -> None:
        """NoDocumentation"""
        self.unions.remove(self.find(self.unions, 'query', query))
        XQuery.updateTextQueries()

    def moveField(self, index: int, up: bool, withAlias=True, noSignal=False) -> None:
        """NoDocumentation"""
        if up:
            if not withAlias:
                self.fields[index].alias, self.fields[index - 1].alias = \
                    self.fields[index - 1].alias, self.fields[index].alias
            self.fields[index], self.fields[index - 1] = self.fields[index - 1], self.fields[index]
        else:
            if not withAlias:
                self.fields[index].alias, self.fields[index + 1].alias = \
                    self.fields[index + 1].alias, self.fields[index].alias
            self.fields[index], self.fields[index + 1] = self.fields[index + 1], self.fields[index]

        XQuery.updateTextQueries()
        if not noSignal:
            self.changedFieldsQuery.emit()

    def checkJoinsQuery(self) -> bool:
        """NoDocumentation"""
        pass

    def addCondition(self, selectedFieldTable: Union[SelectedFieldTable, None] = None, noSignal=False) -> Expression:
        """NoDocumentation"""
        expression = Expression(self, selectedFieldTable)
        self.conditions.append(expression)
        XQuery.updateTextQueries()
        if not noSignal:
            self.changedConditions.emit()
        return expression

    def deleteCondition(self, expression: Expression, noSignal=False) -> None:
        """NoDocumentation"""
        self.conditions.remove(expression)
        XQuery.updateTextQueries()
        if not noSignal:
            self.changedConditions.emit()

    def addConditionAfterGrouping(self, expression: Union[Expression, None] = None, noSignal=False) -> Expression:
        """NoDocumentation"""
        expression = Expression(self, expression)
        self.conditionsAfterGrouping.append(expression)
        XQuery.updateTextQueries()
        if not noSignal:
            self.changedConditionsAfterGrouping.emit()
        return expression

    def deleteConditionAfterGrouping(self, expression: Expression, noSignal=False) -> None:
        """NoDocumentation"""
        self.conditionsAfterGrouping.remove(expression)
        XQuery.updateTextQueries()
        if not noSignal:
            self.changedConditionsAfterGrouping.emit()

    def addFieldOrderBy(self, _object: Union[Expression, SelectedFieldTable], noSignal=False) -> SimpleNamespace:
        """NoDocumentation"""

        orderBy = SimpleNamespace()
        orderBy.field = _object
        orderBy.typeOfSorting = 'ASC'
        self.orderBy.append(orderBy)
        XQuery.updateTextQueries()
        if not noSignal:
            self.changedFieldsOrderBy.emit()
        return orderBy

    def deleteFieldOrderBy(self, _object, noSignal=False) -> None:
        """NoDocumentation"""
        self.orderBy.remove(_object)
        XQuery.updateTextQueries()
        if not noSignal:
            self.changedFieldsOrderBy.emit()

    def setTypeOfSorting(self, _object, typeOfSorting: str, noSignal=False) -> None:
        """NoDocumentation"""
        _object.typeOfSorting = typeOfSorting
        XQuery.updateTextQueries()
        if not noSignal:
            self.changedFieldsOrderBy.emit()

    @classmethod
    def updateTablesDB(cls, tables):
        for name, fields in tables.items():
            cls.tablesDB[name] = Table(name, fields)
        Table.findReferences()

    def getPandasDataFrameJoins(self) -> pd.DataFrame:
        """NoDocumentation"""
        res = pd.DataFrame(columns=('aliasTable1', 'join', 'aliasTable2'))

        for join in self.joins:
            res.append({'aliasTable1': join.table1.alias, 'join': join.join, 'aliasTable2': join.table2.alias})

        return res

    def setAliasField(self, expression: Expression, alias: str, noSignal=False) -> None:
        expression.alias = alias
        if not noSignal:
            XQuery.updateTextQueries()

    @staticmethod
    def find(objects: object, attribute: str, value: object) -> object:
        """NoDocumentation"""
        for ob in objects:
            if getattr(ob, attribute) == value:
                return ob
        return None
