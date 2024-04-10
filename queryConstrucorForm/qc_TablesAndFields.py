from PyQt5.QtWidgets import QWidget, QSplitter, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTreeWidget, \
    QTreeWidgetItem, QSpacerItem, QTableWidgetItem, QShortcut, QMenu, QAction
from table import Table, FieldTable, SelectedTable, SelectedFieldTable

import xQuery as qc
from widgets.xTreeWidget import XTreeWidget
from widgets.xTableWidget import XTableWidget
from PyQt5.QtCore import pyqtSignal, Qt, QObject
from PyQt5.QtGui import QCursor
from expression import Expression
from typing import Union
from widgets.expressionEditor import ExpressonEditor


class TablesAndFieldsWidget(QWidget):
    dragAndDrop = dict()

    def __init__(self, query):
        super().__init__()
        self.query = query
        self.query.changedFieldsQuery.connect(self.updateFieldsQuery)
        self.query.changedSelectedTables.connect(self.updateSelectedTables)
        self.query.changedAvailableTables.connect(self.updateAvailableTables)

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

        # self.availableTablesPanelWidget = QWidget()
        # self.availableTablesPanelWidget.setLayout(QHBoxLayout())
        # self.availableTablesWidget.layout().addWidget(self.availableTablesPanelWidget)

        # self.addSubQuery = QPushButton()
        # self.addSubQuery.setText("+")
        # self.availableTablesPanelWidget.layout().addWidget(self.addSubQuery)
        # self.availableTablesPanelWidget.layout().addStretch()
        # self.availableTablesPanelWidget.layout().setContentsMargins(0, 0, 0, 0)

        self.availableTables = XTreeWidget()

        self.availableTablesWidget.layout().addWidget(self.availableTables)
        self.availableTables.mouseDoubleClicked.connect(self.addToSelectedTables)

        self.selectedTablesWidget = QWidget()
        self.selectedTablesWidget.setLayout(QVBoxLayout())
        self.splitter.addWidget(self.selectedTablesWidget)

        # self.selectedTablesPanelWidget = QWidget()
        # self.selectedTablesPanelWidget.setLayout(QHBoxLayout())
        # self.selectedTablesWidget.layout().addWidget(self.selectedTablesPanelWidget)

        # self.replaceTableButton = QPushButton()
        # self.replaceTableButton.setText("=")
        # self.replaceTableButton.clicked.connect(self.replaceTable)
        # self.selectedTablesPanelWidget.layout().addWidget(self.replaceTableButton)
        # self.selectedTablesPanelWidget.layout().addStretch()
        # self.selectedTablesPanelWidget.layout().setContentsMargins(0, 0, 0, 0)

        self.selectedTables = XTreeWidget()
        self.selectedTables.setHeaderLabel('Выбранные таблицы')
        self.selectedTablesWidget.layout().addWidget(self.selectedTables)
        self.selectedTables.dropped.connect(self.addToSelectedTables)
        self.selectedTables.mouseDoubleClicked.connect(self.addToSelectedFields)
        self.selectedTables.delete.connect(self.deleteSelectedTable)
        self.selectedTables.mouseMiddleButtonPressed.connect(self.addReferenceTable)

        self.selectedFieldsWidget = QWidget()
        self.selectedFieldsWidget.setLayout(QVBoxLayout())
        self.splitter.addWidget(self.selectedFieldsWidget)

        # self.selectedFieldsPanelWidget = QWidget()
        # self.selectedFieldsPanelWidget.setLayout(QHBoxLayout())
        # self.selectedFieldsWidget.layout().addWidget(self.selectedFieldsPanelWidget)

        # self.addExpression = QPushButton()
        # self.addExpression.setText("+")
        # self.selectedFieldsPanelWidget.layout().addWidget(self.addExpression)
        # self.selectedFieldsPanelWidget.layout().addStretch()
        # self.selectedFieldsPanelWidget.layout().setContentsMargins(0, 0, 0, 0)

        self.selectedFields = XTableWidget()
        self.selectedFields.verticalHeader().hide()
        self.selectedFields.setColumnCount(1)
        self.selectedFields.setHorizontalHeaderLabels(['Поля'])
        self.selectedFields.horizontalHeader().setStretchLastSection(True)
        self.selectedFieldsWidget.layout().addWidget(self.selectedFields)
        self.selectedFields.dropped.connect(self.addToSelectedFields)
        self.selectedFields.mouseDoubleClicked.connect(self.editExpression)

        # self.selectedFields.itemDoubleClicked.connect(self.editExpression)

        # self.selectedFields.mouseRightButtonPressed.connect(self.execMenuSelectedFields)
        self.selectedFields.setContextMenuPolicy(Qt.CustomContextMenu)
        self.selectedFields.customContextMenuRequested.connect(self.execMenuSelectedFields)

        self.updateAvailableTables()

    def addReferenceTable(self, field):
        if type(field) != SelectedFieldTable or field.fieldTable.fieldTableReference == None:
            return
        self.addToSelectedTables(field.fieldTable.fieldTableReference.table)
        self.query.addJoinAuto()

    def execMenuSelectedFields(self, point):
        self.selectedFields.menu = QMenu(self)

        a = QAction('Добавить', self)
        a.triggered.connect(self.addEmptyField)
        self.selectedFields.menu.addAction(a)

        if 'SUM(0)' not in [expression.rawSqlText for expression in self.query.fields]:
            a = QAction('Добавить SUM(0)', self)
            a.triggered.connect(self.addSUM0)
            self.selectedFields.menu.addAction(a)

        currentItem = self.selectedFields.currentItem()
        if currentItem != None:

            aggFunctions = ['SUM', 'MIN', 'MAX', 'AVG', 'COUNT', 'COUNT( DISTRICT']
            for el in aggFunctions:
                a = QAction(f'Обернуть в {el}', self)
                a.aggFunction = el
                a.triggered.connect(self.wrapAggFunction)
                self.selectedFields.menu.addAction(a)

        self.selectedFields.menu.move(QCursor.pos())
        self.selectedFields.menu.show()
        print('df')

    def addEmptyField(self):
        _expression = self.query.addExpression('NULL')
        self.editExpression(_expression)

    def wrapAggFunction(self):
        aggFunction = self.sender().aggFunction
        if '(' not in aggFunction:
            aggFunction += '('
        _expression = self.selectedFields.currentItem()._object
        _expression.setAggregationFunction(aggFunction)

    def addSUM0(self):
        _expression = self.query.addExpression('SUM(0)', 'SUM0')

    def updateAvailableTables(self):
        self.availableTables.clear()
        self.availableTables.setHeaderLabel('Доступные таблицы')

        for table in qc.XQuery.tablesTemp:
            if table.query == self.query:
                break
            itemTable = QTreeWidgetItem()
            itemTable.setText(0, table.name)
            itemTable._object = table
            for field in table.fields:
                itemChield = QTreeWidgetItem()
                itemChield.setText(0, field.name)
                itemChield._object = field
                itemTable.addChild(itemChield)

            self.availableTables.addTopLevelItem(itemTable)

        for name, table in qc.XQuery.tablesDB.items():
            itemTable = QTreeWidgetItem()
            itemTable.setText(0, name)
            itemTable._object = table
            for field in table.fields:
                itemChield = QTreeWidgetItem()
                if field.fieldTableReference == None:
                    itemChield.setText(0, field.name)
                else:
                    itemChield.setText(0, f'{field.name} ({field.fieldTableReference.table})')
                itemChield._object = field
                itemTable.addChild(itemChield)

            self.availableTables.addTopLevelItem(itemTable)

    def addToSelectedTables(self, _object: Union[Table, FieldTable, None]) -> None:
        """Если прилетает в _object таблица, то добавляем таблицу,
        если прилетает поле таблицы, то добавляем и таблицу и поле (методом addField)"""

        if _object == None:
            self.query.addFieldQuery()

        if not (type(_object) in (Table, FieldTable)):
            return

        if type(_object) is Table:
            self.query.addSelectedTable(_object)
        elif type(_object) is FieldTable:
            self.query.addSelectedTable(_object.table)
            selectedTable = self.query.selectedTables[-1]
            self.query.addFieldQuery(selectedTable.getSelectedField(_object))
        else:
            return

    def addToSelectedFields(self, _object: Union[Table, FieldTable, SelectedTable, SelectedFieldTable]) -> None:
        """NoDocumentation"""

        if type(_object) is Table:
            self.query.addSelectedTable(_object)
            selectedTable = self.query.selectedTables[-1]
            for selectedFieldTable in selectedTable.fields:
                self.query.addFieldQuery(selectedFieldTable)
        elif type(_object) is FieldTable:
            self.query.addSelectedTable(_object.table)
            selectedTable: SelectedTable = self.query.selectedTables[-1]
            self.query.addFieldQuery(selectedTable.getSelectedField(_object))
        elif type(_object) is SelectedTable:
            for selectedFieldTable in _object.fields:
                self.query.addFieldQuery(selectedFieldTable)
        elif type(_object) is SelectedFieldTable:
            self.query.addFieldQuery(_object)

    def updateFieldsQuery(self) -> None:
        """NoDocumentation"""
        self.selectedFields.clear()
        self.selectedFields.setRowCount(0)
        self.selectedFields.setHorizontalHeaderLabels(('Поля',))
        for expression in self.query.fields:
            item = QTableWidgetItem()
            item._object = expression
            item.setText(expression.rawSqlText)
            # self.expressions[expression] = item
            self.selectedFields.addString([item])

    def updateSelectedTables(self) -> None:
        """NoDocumentation"""
        self.selectedTables.clear()
        self.selectedTables.setHeaderLabel('Выбранные таблицы')
        for selectedTable in self.query.selectedTables:
            itemTable = QTreeWidgetItem()
            itemTable.setText(0, selectedTable.alias)
            itemTable._object = selectedTable
            # itemTable.setExpanded(True)
            # self.selectedTables.expandItem(itemTable)

            for selectedField in selectedTable.fields:
                itemChield = QTreeWidgetItem()
                if selectedField.fieldTable.fieldTableReference == None:
                    itemChield.setText(0, selectedField.name)
                else:
                    itemChield.setText(0,
                                       f'{selectedField.name} ({selectedField.fieldTable.fieldTableReference.table})')

                itemChield._object = selectedField
                itemTable.addChild(itemChield)

            self.selectedTables.addTopLevelItem(itemTable)
            itemTable.setExpanded(True)

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
            self.query.deleteFieldQuery(expression)
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
        # if expression == None:
        #     expression = self.query.addFieldQuery()
        self.expressonEditor = ExpressonEditor(self, self.selectedTables.clone(), expression)
        self.expressonEditor.show()
        self.expressonEditor.expressionEdited.connect(self.expressionEdited)

    def expressionEdited(self, expression: Expression, text: str) -> None:
        """NoDocumentation"""
        expression.setRawSqlText(text)
        for row in range(self.selectedFields.rowCount()):
            item = self.selectedFields.item(row, 0)
            if item._object == expression:
                item.setText(text)
                break

        self.query.changedFieldsQuery.emit()
