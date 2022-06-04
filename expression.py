from table import FieldTable, SelectedFieldTable


class Expression():
    def __init__(self, query: "XQuery", alias, selectedFildTable: SelectedFieldTable = None):
        self.query = query
        self.alias = alias
        if selectedFildTable == None:
            self.sqltext = ''
            # self.usedFieldsTables = dict()
        else:
            self.sqlText = selectedFildTable.path
            # self.usedFieldsTables = {selectedFildTable}
        self.hasAggregation = False

    def setText(self, text) -> None:
        """NoDocumentation"""
        self.sqlText = text

