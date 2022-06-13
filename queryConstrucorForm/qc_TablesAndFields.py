from PyQt5.QtWidgets import QWidget, QSplitter, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTreeWidget, \
    QTreeWidgetItem, QSpacerItem, QTableWidgetItem, QShortcut
from table import Table, FieldTable, SelectedTable, SelectedFieldTable

import xQuery as qc
from widgets.xTreeWidget import XTreeWidget
from widgets.xTableWidget import XTableWidget
from PyQt5.QtCore import pyqtSignal, Qt
from expression import Expression
from typing import Union
from widgets.expressionEditor import ExpressonEditor

class TablesAndFieldsWidget(QWidget):
    dragAndDrop = dict()

    def __init__(self, query):
        super().__init__()
        self.query = query

        self.deleteshortcut = QShortcut(self)
        self.deleteshortcut.setKey(Qt.Key_Delete)
        self.deleteshortcut.activated.connect(self.deleteObject)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.splitter = QSplitter()
        self.layout.addWidget(self.splitter)

        self.availableTablesWidget = QWidget()
        self.availableTablesWidget.setLayout(QVBoxLayout())
        # self.availableTablesWidget.layout().setContentsMargins(4, 4, 4, 4)
        self.splitter.addWidget(self.availableTablesWidget)

        self.availableTablesPanelWidget = QWidget()
        self.availableTablesPanelWidget.setLayout(QHBoxLayout())
        self.availableTablesWidget.layout().addWidget(self.availableTablesPanelWidget)


        self.addSubQuery = QPushButton()
        self.addSubQuery.setText("+")
        self.availableTablesPanelWidget.layout().addWidget(self.addSubQuery)
        self.availableTablesPanelWidget.layout().addStretch()
        self.availableTablesPanelWidget.layout().setContentsMargins(0, 0, 0, 0)

        self.availableTables = XTreeWidget()
        self.availableTables.setHeaderLabel('Доступные таблицы')
        self.availableTablesWidget.layout().addWidget(self.availableTables)
        self.availableTables.mouseDoubleClicked.connect(self.addToSelectedTables)

        self.selectedTablesWidget = QWidget()
        self.selectedTablesWidget.setLayout(QVBoxLayout())
        self.splitter.addWidget(self.selectedTablesWidget)

        self.selectedTablesPanelWidget = QWidget()
        self.selectedTablesPanelWidget.setLayout(QHBoxLayout())
        self.selectedTablesWidget.layout().addWidget(self.selectedTablesPanelWidget)

        self.replaceTableButton = QPushButton()
        self.replaceTableButton.setText("=")
        self.replaceTableButton.clicked.connect(self.replaceTable)
        self.selectedTablesPanelWidget.layout().addWidget(self.replaceTableButton)
        self.selectedTablesPanelWidget.layout().addStretch()
        self.selectedTablesPanelWidget.layout().setContentsMargins(0, 0, 0, 0)


        self.selectedTables = XTreeWidget()
        self.selectedTables.setHeaderLabel('Выбранные таблицы')
        self.selectedTablesWidget.layout().addWidget(self.selectedTables)
        self.selectedTables.dropped.connect(self.addToSelectedTables)
        self.selectedTables.mouseDoubleClicked.connect(self.addToSelectedFields)
        self.selectedTables.delete.connect(self.deleteSelectedTable)

        self.selectedFieldsWidget = QWidget()
        self.selectedFieldsWidget.setLayout(QVBoxLayout())
        self.splitter.addWidget(self.selectedFieldsWidget)

        self.selectedFieldsPanelWidget = QWidget()
        self.selectedFieldsPanelWidget.setLayout(QHBoxLayout())
        self.selectedFieldsWidget.layout().addWidget(self.selectedFieldsPanelWidget)

        self.addExpression = QPushButton()
        self.addExpression.setText("+")
        self.selectedFieldsPanelWidget.layout().addWidget(self.addExpression)
        self.selectedFieldsPanelWidget.layout().addStretch()
        self.selectedFieldsPanelWidget.layout().setContentsMargins(0, 0, 0, 0)



        self.selectedFields = XTableWidget()
        self.selectedFields.verticalHeader().hide()
        self.selectedFields.setColumnCount(1)
        self.selectedFields.setHorizontalHeaderLabels(['Поля'])
        self.selectedFields.horizontalHeader().setStretchLastSection(True)
        self.selectedFieldsWidget.layout().addWidget(self.selectedFields)
        self.selectedFields.dropped.connect(self.addToSelectedFields)
        self.selectedFields.mouseDoubleClicked.connect(self.editExpression)

        for name, table in qc.XQuery.availableTables.items():
            itemTable = QTreeWidgetItem()
            itemTable.setText(0, name)
            itemTable._object = table
            for field in table.fields:
                itemChield = QTreeWidgetItem()
                itemChield.setText(0, field.name)
                itemChield._object = field
                itemTable.addChild(itemChield)

            self.availableTables.addTopLevelItem(itemTable)

    def addToSelectedTables(self, _object: Union[Table, FieldTable]) -> None:
        """Если прилетает в _object таблица, то добавляем таблицу,
        если прилетает поле таблицы, то добавляем и таблицу и поле (методом addField)"""

        if not (type(_object) in (Table, FieldTable)):
            return

        if type(_object) is Table:
            table = _object
            selectedTable = self.query.addAndGetSelectedTable(table)
        elif type(_object) is FieldTable:
            table = _object.table
            selectedTable = self.query.addAndGetSelectedTable(table)

            self.addFieldToSelectedFields(selectedTable.getSelectedField(_object))
        else:
            return
        self.addTableToSelectedTables(selectedTable)

    def addToSelectedFields(self, _object: Union[Table, FieldTable, SelectedTable, SelectedFieldTable]) -> None:
        """NoDocumentation"""

        if type(_object) is Table:
            selectedTable = self.query.addAndGetSelectedTable(_object)
            self.addTableToSelectedTables(selectedTable)
            for _, selectedField in selectedTable.fields.items():
                self.addFieldToSelectedFields(selectedField)
        elif type(_object) is FieldTable:
            selectedTable = self.query.addAndGetSelectedTable(_object.table)
            self.addTableToSelectedTables(selectedTable)
            self.addFieldToSelectedFields(selectedTable.getSelectedField(_object))
        elif type(_object) is SelectedTable:
            for _, selectedField in _object.fields.items():
                self.addFieldToSelectedFields(selectedField)
        elif type(_object) is SelectedFieldTable:
            self.addFieldToSelectedFields(_object)



    def addTableToSelectedTables(self, selectedTable: SelectedTable) -> None:
        """NoDocumentation"""
        itemTable = QTreeWidgetItem()
        itemTable.setText(0, selectedTable.alias)
        itemTable._object = selectedTable

        for _, selectedField in selectedTable.fields.items():
            itemChield = QTreeWidgetItem()
            itemChield.setText(0, selectedField.path)
            itemChield._object = selectedField
            itemTable.addChild(itemChield)

        self.selectedTables.addTopLevelItem(itemTable)

    def addFieldToSelectedFields(self, selectedField: SelectedFieldTable) -> None:
        """NoDocumentation"""
        item = QTableWidgetItem()
        expression = qc.XQuery.addAndGetSelectedField(self.query, selectedField)
        item._object = expression
        item.setText(expression.sqlText)
        # self.expressions[expression] = item
        self.selectedFields.addString([item])


    def deleteSelectedField(self, expression: Expression) -> None:
        """NoDocumentation"""
        self.selectedFields.deleteString(expression)

    def deleteSelectedTable(self, _object: Union[SelectedTable, SelectedFieldTable]) -> None:
        """NoDocumentation"""
        pass
    def replaceTable(self) -> None:
        """NoDocumentation"""
        print('replaceTable')

    def deleteObject(self) -> None:
        """NoDocumentation"""
        if self.selectedFields.hasFocus():
            currentItem = self.selectedFields.currentItem()
            if currentItem == None:
                return
            expression = currentItem._object
            self.selectedFields.deleteString(expression)
            self.query.deleteSelectedField(expression)
        elif self.selectedTables.hasFocus():
            currentItem = self.selectedTables.currentItem()
            if currentItem == None:
                return

            if type(currentItem._object) == SelectedTable:
                selectedTable = currentItem._object
                self.selectedTables.deleteBranch(selectedTable)
                self.query.deleteSelectedTable(selectedTable)


    def editExpression(self, expression: Expression) -> None:
        """NoDocumentation"""
        self.expressonEditor = ExpressonEditor(self, self.selectedTables, expression)
        self.expressonEditor.show()
        self.expressonEditor.expressionEdited.connect(self.expressionEdited)

    def expressionEdited(self, expression: Expression) -> None:
        """NoDocumentation"""
        for row in range(self.selectedFields.rowCount()):
            item = self.selectedFields.item(row, 0)
            if item._object == expression:
                item.setText(expression.sqlText)
                break

