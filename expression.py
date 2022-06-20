from table import FieldTable, SelectedFieldTable
import xQuery
from typing import Union


class Expression():
    def __init__(self, query: 'XQuery', _object: Union[SelectedFieldTable, 'Expression', 'UnionTables', None] = None, alias: str = ''):
        self.query = query
        self.alias = alias
        # self.usedFieldsTables = dict()
        if _object == None:
            self.sqlText = ''
        else:
            if alias == '':
                if type(_object) == SelectedFieldTable: #Условие до группировки
                    self.sqlText = f'{_object.path} = :{_object.name}'
                elif type(_object) == xQuery.UnionTables: #Условие связи
                    pass
                else:
                    pass

            else: #Поле запроса
                _object: SelectedFieldTable = _object
                self.sqlText = _object.path
            # self.usedFieldsTables = {selectedFildTable}
        self.aggregationFunction = ''

    def setText(self, text) -> None:
        """NoDocumentation"""
        self.sqlText = text

