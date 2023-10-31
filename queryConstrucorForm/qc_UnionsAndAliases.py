from PyQt5.QtWidgets import QWidget, QSplitter, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTreeWidget, \
    QTreeWidgetItem, QSpacerItem, QTableWidgetItem, QShortcut, QComboBox, QLineEdit

import xQuery
from table import Table, FieldTable, SelectedTable, SelectedFieldTable

import xQuery as qc
from widgets.xTreeWidget import XTreeWidget
from widgets.xTableWidget import XTableWidget
from PyQt5.QtCore import pyqtSignal, Qt
from expression import Expression
from typing import Union
from widgets.expressionEditor import ExpressonEditor


class UnionsAndAliases(QWidget):
    addedUnionQuery = pyqtSignal(object)

    def __init__(self, query):
        super().__init__()
        layout = QHBoxLayout()
        self.setLayout(layout)

        self.query = query
        self.unionsWidget = QWidget()
        self.unionsWidget.setLayout(QVBoxLayout())

        self.unionsPanelWidget = QWidget()
        self.unionsPanelWidget.setLayout(QHBoxLayout())
        self.addUnionButton = QPushButton('+')
        self.addUnionButton.pressed.connect(self.addUnionQuery)
        self.unionsPanelWidget.layout().addWidget(self.addUnionButton)
        self.unionsPanelWidget.layout().addStretch()
        self.unionsPanelWidget.layout().setContentsMargins(0, 0, 0, 0)
        self.unionsWidget.layout().addWidget(self.unionsPanelWidget)

        self.unions = QTableWidget()
        self.unions.cellClicked.connect(self.selectCurrentQuery)

        self.unionsWidget.layout().addWidget(self.unions)
        layout.addWidget(self.unionsWidget)

        self.aliasesWidget = QWidget()
        self.aliasesWidget.setLayout(QVBoxLayout())
        layout.addWidget(self.aliasesWidget)

        self.aliasesPanelWidget = QWidget()
        self.aliasesPanelWidget.setLayout(QHBoxLayout())
        self.aliasesWidget.layout().addWidget(self.aliasesPanelWidget)

        self.moveAliasUpButton = QPushButton()
        self.moveAliasUpButton.setText("↑")
        self.moveAliasUpButton.clicked.connect(lambda: self.moveField(True))
        self.aliasesPanelWidget.layout().addWidget(self.moveAliasUpButton)

        self.moveAliasDownButton = QPushButton()
        self.moveAliasDownButton.setText("↓")
        self.moveAliasDownButton.clicked.connect(lambda: self.moveField(False))

        self.aliasesPanelWidget.layout().addWidget(self.moveAliasDownButton)
        self.aliasesPanelWidget.layout().addStretch()
        self.aliasesPanelWidget.layout().setContentsMargins(0, 0, 0, 0)

        self.aliases = QTableWidget()
        self.aliases.itemChanged.connect(self.setAliasForExpression)
        self.aliasesWidget.layout().addWidget(self.aliases)

        self.fieldsCurrentQueryWidget = QWidget()
        self.fieldsCurrentQueryWidget.setLayout(QVBoxLayout())
        layout.addWidget(self.fieldsCurrentQueryWidget)

        self.currentQueryPanelWidget = QWidget()
        self.currentQueryPanelWidget.setLayout(QHBoxLayout())
        self.fieldsCurrentQueryWidget.layout().addWidget(self.currentQueryPanelWidget)

        self.moveFieldCurrentQueryUpButton = QPushButton()
        self.moveFieldCurrentQueryUpButton.setText("↑")
        self.moveFieldCurrentQueryUpButton.clicked.connect(lambda: self.moveFieldCurrentQuery(True))
        self.currentQueryPanelWidget.layout().addWidget(self.moveFieldCurrentQueryUpButton)

        self.moveFieldCurrentQueryDownButton = QPushButton()
        self.moveFieldCurrentQueryDownButton.setText("↓")
        self.moveFieldCurrentQueryDownButton.clicked.connect(lambda: self.moveFieldCurrentQuery(False))
        self.currentQueryPanelWidget.layout().addWidget(self.moveFieldCurrentQueryDownButton)

        self.currentQueryPanelWidget.layout().addStretch()
        self.currentQueryPanelWidget.layout().setContentsMargins(0, 0, 0, 0)

        self.fieldsCurrentQuery = QTableWidget()
        self.fieldsCurrentQueryWidget.layout().addWidget(self.fieldsCurrentQuery)

    def addUnionQuery(self, query=None) -> None:
        """Добавляем либо первый запрос, либо еще один на объединение"""
        if query == None:
            query = self.query.addUnionQuery()
            query.changedFieldsQuery.connect(self.updateData)

        self.addedUnionQuery.emit(query)

        # numQuery = len(self.query.unions) + 1
        # nameQuery = f'Запрос {str(numQuery)}'
        # widget = TablesAndFieldsWidget(query)
        # self.tabsUnionsTablesAndFields.addTab(widget, nameQuery)
        #
        # widget = JoinsWidget(query)
        # self.tabsJoins.addTab(widget, nameQuery)
        #
        # widget = ConditionsWidget(query)
        # self.tabsConditions.addTab(widget, nameQuery)
        #
        # widget = GroupingWidget(query)
        # self.tabsGrouping.addTab(widget, nameQuery)
        #
        # widget = ConditionsAfterGroupingWidget(query)
        # self.tabsConditionsAfterGrouping.addTab(widget, nameQuery)
        # self.tabsConstructorQuery.setCurrentIndex(0)
        # self.tabsUnionsTablesAndFields.setCurrentIndex(numQuery - 1)
        #
        # self.currentQuery = query
        self.updateData()

    def selectCurrentQuery(self, row, column) -> None:
        """NoDocumentation"""
        self.currentQuery = self.unions.item(row, 1)._object
        self.updateData()
        currentItem = self.unions.item(row, column)
        self.unions.setCurrentItem(currentItem)
        self.fieldsCurrentQuery.setHorizontalHeaderLabels((currentItem.text(),))

    def setAliasForExpression(self, itm) -> None:
        """NoDocumentation"""
        self.query.setAliasField(itm._object, itm.text())

    def moveField(self, up: bool) -> None:
        """NoDocumentation"""

        row = self.aliases.currentRow()

        if row < 0:
            return
        if up and row == 0:
            return
        elif not up and row == self.aliases.rowCount() - 1:
            return

        if up:
            newRow = row - 1
        else:
            newRow = row + 1

        self.moveFildTable(self.aliases, row, up)
        self.moveFildTable(self.fieldsCurrentQuery, row, up)

        self.aliases.setCurrentItem(self.aliases.item(newRow, 0))
        self.query.moveField(row, up, True)
        for union in self.query.unions:
            union.query.moveField(row, up, True)

    def moveFildTable(self, table: QTableWidget, row: int, up: bool) -> None:
        """NoDocumentation"""

        itm1 = table.item(row, 0)

        if up:
            itm2 = table.item(row - 1, 0)
        else:
            itm2 = table.item(row + 1, 0)

        itm1._object, itm2._object = itm2._object, itm1._object

        text = itm1.text()
        itm1.setText(itm2.text())
        itm2.setText(text)

    def moveFieldCurrentQuery(self, up) -> None:
        """NoDocumentation"""
        row = self.fieldsCurrentQuery.currentRow()

        if row < 0:
            return
        if up and row == 0:
            return
        elif not up and row == self.fieldsCurrentQuery.rowCount() - 1:
            return

        if up:
            newRow = row - 1
        else:
            newRow = row + 1

        self.moveFildTable(self.fieldsCurrentQuery, row, up)

        self.fieldsCurrentQuery.setCurrentItem(self.fieldsCurrentQuery.item(newRow, 0))
        self.currentQuery.moveField(row, up, True)

    def updateData(self) -> None:
        """NoDocumentation"""
        self.unions.clear()
        self.unions.setColumnCount(2)
        self.unions.horizontalHeader().setStretchLastSection(True)
        self.unions.setRowCount(len(self.query.unions) + 1)
        self.unions.setHorizontalHeaderLabels(('Вид', 'Запрос'))

        itm = QTableWidgetItem()
        itm.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        itm._object = self.query
        self.unions.setItem(0, 0, itm)

        itm = QTableWidgetItem()
        itm.setText('Запрос 1')
        itm.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        itm._object = self.query
        self.unions.setItem(0, 1, itm)

        for n, union in enumerate(self.query.unions):
            self.unions.setCellWidget(n + 1, 0, self.getComboBoxTypeUnionSelection(union))

            itm = QTableWidgetItem()
            itm.setText(f'Запрос {str(n + 2)}')
            itm.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            itm._object = union.query
            self.unions.setItem(n + 1, 1, itm)

        self.aliases.clear()
        self.aliases.setColumnCount(1)
        self.aliases.horizontalHeader().setStretchLastSection(True)
        self.aliases.setRowCount(len(self.query.fields))
        self.aliases.setHorizontalHeaderLabels(('Имя поля',))

        self.fieldsCurrentQuery.clear()
        self.fieldsCurrentQuery.setColumnCount(1)
        self.fieldsCurrentQuery.horizontalHeader().setStretchLastSection(True)
        self.fieldsCurrentQuery.setRowCount(len(self.query.fields))
        self.fieldsCurrentQuery.setHorizontalHeaderLabels(('Запрос 1',))

        n = 0
        for expression in self.query.fields:
            itm = QTableWidgetItem()
            itm.setText(expression.alias)
            itm._object = expression
            self.aliases.setItem(n, 0, itm)

            itm = QTableWidgetItem()
            itm.setText(expression.rawSqlText)
            itm._object = expression
            itm.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            self.fieldsCurrentQuery.setItem(n, 0, itm)
            n += 1

    def getComboBoxTypeUnionSelection(self, union) -> QComboBox:
        """NoDocumentation"""
        res = QComboBox()
        res.union = union
        res.setLineEdit(QLineEdit())
        res.lineEdit().union = union
        res.lineEdit().setReadOnly(True)
        res.setStyleSheet("QComboBox { qproperty-frame: false }");
        res.addItem('UNION')
        res.addItem('UNION ALL')
        res.setCurrentText(union.union)

        res.activated.connect(self.selectedTypeUnion)
        # res.lineEdit().selectedJoin.connect(self.setCurrentJoin)
        return res

    def selectedTypeUnion(self) -> None:
        """NoDocumentation"""
        comboBox: QComboBox = self.sender()
        union = comboBox.union
        union.union = comboBox.currentText()
