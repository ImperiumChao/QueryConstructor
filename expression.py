from table import FieldTable, SelectedFieldTable
import xQuery
from typing import Union


class Expression():
    aggFunctions = ('SUM(', 'MIN(', 'MAX(', 'AVG(', 'COUNT( DISTRICT ')

    def __init__(self, query: 'XQuery', _object: Union[SelectedFieldTable, 'Expression', 'UnionTables', None] = None,
                 alias: str = '', rawSqlText=''):
        self.query = query
        self.alias = alias
        self.isCondition = alias == ''
        self.usedFieldsTables = dict()

        if self.isCondition:  # условие связи, условие до группировки,  условие после группировки
            self.alias = None
            self.hasAggregation = None

            if _object == None:
                self.rawSqlText = rawSqlText
            elif type(_object) == xQuery.JoinTables:  # условие связи
                self.rawSqlText = rawSqlText  # пока что так
            elif type(_object) == SelectedFieldTable:  # условие до группировки
                self.rawSqlText = f'{_object.path} = :{_object.name}'
            elif type(_object) == Expression:  # условие после группировки
                self.rawSqlText = f'{_object.rawSqlText} = :param'

        else:  # поле запроса
            self.alias = alias
            if _object == None:
                self.rawSqlText = ''
            else:
                _object: SelectedFieldTable
                self.rawSqlText = _object.path

            self.alias = alias
            self.hasAggregation = False

        self.rawSqlTextToParameterizedSqlText()

    def setRawSqlText(self, text: str) -> None:
        """NoDocumentation"""
        self.rawSqlText = text.strip()
        self.rawSqlTextToParameterizedSqlText()
        self.hasAggregation = False
        if not self.isCondition:
            for aggFunction in self.aggFunctions:
                if aggFunction in self.rawSqlText:
                    self.hasAggregation = True
                    break

        self.query.changedFieldsQuery.emit()
        xQuery.XQuery.updateTextQueries()

    def rawSqlTextToParameterizedSqlText(self) -> None:
        """NoDocumentation"""
        self.usedFieldsTables.clear()
        numParameters = 1
        for selectedTable in self.query.selectedTables:
            for fieldTable in selectedTable.fields:
                path: str = fieldTable.path
                if path in self.rawSqlText:
                    self.parameterizedSqlText = self.rawSqlText.replace(path, '{' + str(numParameters) + '}')
                    self.usedFieldsTables[fieldTable] = numParameters
                    numParameters += 1

    def parameterizedSqlTextToRawSqlText(self) -> None:
        """NoDocumentation"""
        res = self.parameterizedSqlText
        for key, fieldTable in self.usedFieldsTables.items():
            res = res.replace('{' + key + '}', fieldTable.path)

        self.setRawSqlText(res)

    def setAggregationFunction(self, aggregationFunction: str) -> None:
        """NoDocumentation"""
        if self.hasAggregation:
            for aggFunctionOld in self.aggFunctions:
                self.rawSqlText = self.rawSqlText.replace(aggFunctionOld, aggregationFunction)
        else:
            self.rawSqlText = f'{aggregationFunction}{self.rawSqlText})'
            self.hasAggregation = True

        self.rawSqlTextToParameterizedSqlText()
        self.query.changedFieldsQuery.emit()
        xQuery.XQuery.updateTextQueries()
