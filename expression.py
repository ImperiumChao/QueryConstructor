from table import FieldTable, SelectedFieldTable
import xQuery
import re
from typing import Union

class Expression():
    def __init__(self, query: 'XQuery', _object: Union[SelectedFieldTable, 'Expression', 'UnionTables', None] = None, alias: str = ''):
        self.query = query
        self.alias = alias
        self.intricateAggregation = False
        self.isCondition = alias == ''
        self.usedFieldsTables = dict()

        if self.isCondition:    # условие связи, условие до группировки,  условие после группировки
            self.alias = None
            self.rawSqlTextWithoutAgg = None
            self.aggregationFunction = None
            self.intricateAggregation = None
            self.hasAggregation = None

            if _object == None:
                self.rawSqlText = ''
            elif type(_object) == xQuery.UnionTables:   # условие связи
                self.rawSqlText = ''    # пока что так
            elif type(_object) == SelectedFieldTable:   # условие до группировки
                self.rawSqlText = f'{_object.path} = :{_object.name}'
            elif type(_object) == Expression:           # условие после группировки
                self.rawSqlText = f'{_object.rawSqlText} = :param'

        else:   # поле запроса
            self.alias = alias
            if _object == None:
                self.rawSqlText = ''
            else:
                _object: SelectedFieldTable
                self.rawSqlText = _object.path

            self.alias = alias
            self.rawSqlTextWithoutAgg = self.rawSqlText
            self.aggregationFunction = ''
            self.intricateAggregation = False
            self.hasAggregation = False

        self.rawSqlTextToParameterizedSqlText()



    def setRawSqlText(self, text: str) -> None:
        """NoDocumentation"""
        self.rawSqlText = text.strip()
        self.rawSqlTextToParameterizedSqlText()

        if not self.isCondition:
            pattern = r'(?i)XXX\s*\('
            foundAggregationFunctions = list()
            for aggFunction in ('SUM', 'MIN', 'MAX', "AVG"):
                count = len(re.findall(pattern.replace('XXX', aggFunction), self.rawSqlText))
                if count == 1:
                    foundAggregationFunctions.append(aggFunction)
                elif count > 1:
                    self.intricateAggregation = True
                    self.aggregationFunction = ''
                    return

            count = len(foundAggregationFunctions)

            if count == 1:
                self.aggregationFunction = foundAggregationFunctions[0]
                self.hasAggregation = True
            elif count > 1:
                self.intricateAggregation = True
                self.aggregationFunction = ''
                self.hasAggregation = True
            else:
                self.intricateAggregation = False
                self.aggregationFunction = ''
                self.hasAggregation = False


    def setRawSqlTextWithoutAgg(self, text) -> None:
        """NoDocumentation"""
        if self.intricateAggregation:
            self.setRawSqlText(text)
            return

        self.rawSqlTextWithoutAgg = text

    def rawSqlTextToParameterizedSqlText (self) -> None:
        """NoDocumentation"""
        numParameters = 1
        for _, table in self.query.selectedTables.items():
            for _, fieldTable in table.fields.items():
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
        self.aggregationFunction = aggregationFunction
        if self.aggregationFunction =='':
            self.setRawSqlText(self.rawSqlTextWithoutAgg)
            self.hasAggregation = False
        else:
            self.setRawSqlText(f'{aggregationFunction}({self.rawSqlText})')
            self.hasAggregation = True

        self.rawSqlTextToParameterizedSqlText()