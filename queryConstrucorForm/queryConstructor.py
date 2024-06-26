﻿from PyQt5.QtWidgets import QWidget, QTabWidget, QTreeWidget, QListWidget, QPushButton, QVBoxLayout, \
    QHBoxLayout, QSplitter, QTableWidget, QTextEdit, QShortcut, QTableWidgetItem, QLineEdit, QComboBox, \
    QTreeWidgetItem, QCheckBox, QSizePolicy

from PyQt5 import QtCore
from PyQt5.QtCore import Qt, pyqtSignal, QObject
from queryConstrucorForm.qc_Conditions import ConditionsWidget
from queryConstrucorForm.qc_Grouping import GroupingWidget
from queryConstrucorForm.qc_SubQueries import SubQueriesWidget
from queryConstrucorForm.qc_TablesAndFields import TablesAndFieldsWidget
from queryConstrucorForm.qc_Joins import JoinsWidget
from queryConstrucorForm.qc_СonditionsAfterGrouping import ConditionsAfterGroupingWidget
from queryConstrucorForm.qc_UnionsAndAliases import UnionsAndAliases
from queryConstrucorForm.qc_OrderBy import OrderBy
from widgets.xTreeWidget import XTreeWidget
from widgets.xTableWidget import XTableWidget
from table import SelectedTable, SelectedFieldTable
from expression import Expression
from random import randint
from typing import Union
from collections import namedtuple


class QueryConstructor(QWidget):
    dragAndDrop = dict()
    executeQuery = pyqtSignal()

    def __init__(self, query):
        super().__init__()
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.WindowMinimizeButtonHint)
        # self.deleteshortcut = QShortcut(self)
        # self.deleteshortcut.setKey(Qt.Key_Delete)
        # self.deleteshortcut.activated.connect(self.deleteObject)

        self.setWindowTitle('Конструктор запросов')
        self.query = query
        self.XQuery = type(query)
        self.TypesQuery = type(query.type)

        self.setLayout(QVBoxLayout())
        self.splitter = QSplitter()
        self.layout().addWidget(self.splitter)
        self.textQuery = QTextEdit()
        self.textQuery.setReadOnly(True)
        self.splitter.addWidget(self.textQuery)

        self.parameters = QTableWidget()
        self.parameters.cellChanged.connect(self.setParameter)
        self.splitter.addWidget(self.parameters)
        self.parameters.setColumnCount(2)
        self.parameters.horizontalHeader().setStretchLastSection(True)

        self.tabsConstructorQuery = QTabWidget()
        self.splitter.addWidget(self.tabsConstructorQuery)

        self.tabTablesAndFields = QWidget()
        self.tabTablesAndFields.setLayout(QHBoxLayout())
        self.tabsConstructorQuery.addTab(self.tabTablesAndFields, "Таблицы и поля")
        self.tabTablesAndFields.tabsQueries = QTabWidget()
        self.tabTablesAndFields.tabsQueries.setTabBarAutoHide(True)
        self.tabTablesAndFields.tabsQueries.setTabPosition(QTabWidget.East)

        self.tabTablesAndFields.layout().addWidget(self.tabTablesAndFields.tabsQueries)

        self.tabJoins = QWidget()
        self.tabJoins.setLayout(QVBoxLayout())
        self.tabsConstructorQuery.addTab(self.tabJoins, "Связи")
        self.tabJoins.tabsQueries = QTabWidget()
        self.tabJoins.tabsQueries.setTabBarAutoHide(True)
        self.tabJoins.tabsQueries.setTabPosition(QTabWidget.East)
        self.tabJoins.layout().addWidget(self.tabJoins.tabsQueries)

        self.tabConditions = QWidget()
        self.tabConditions.setLayout(QVBoxLayout())
        self.tabsConstructorQuery.addTab(self.tabConditions, "Условия")
        self.tabConditions.tabsQueries = QTabWidget()
        self.tabConditions.tabsQueries.setTabBarAutoHide(True)
        self.tabConditions.tabsQueries.setTabPosition(QTabWidget.East)
        self.tabConditions.layout().addWidget(self.tabConditions.tabsQueries)

        self.tabGrouping = QWidget()
        self.tabGrouping.setLayout(QHBoxLayout())
        # self.tabsConstructorQuery.addTab(self.tabGrouping, "Группировка")
        self.tabGrouping.tabsQueries = QTabWidget()
        self.tabGrouping.tabsQueries.setTabPosition(QTabWidget.East)
        self.tabGrouping.layout().addWidget(self.tabGrouping.tabsQueries)

        self.tabConditionsAfterGrouping = QWidget()
        self.tabConditionsAfterGrouping.setLayout(QVBoxLayout())
        self.tabsConstructorQuery.addTab(self.tabConditionsAfterGrouping, "Условия после группировки")
        self.tabConditionsAfterGrouping.tabsQueries = QTabWidget()
        self.tabConditionsAfterGrouping.tabsQueries.setTabBarAutoHide(True)
        self.tabConditionsAfterGrouping.tabsQueries.setTabPosition(QTabWidget.East)
        self.tabConditionsAfterGrouping.layout().addWidget(self.tabConditionsAfterGrouping.tabsQueries)

        self.tabUnionsAndAliases = QWidget()
        self.tabUnionsAndAliases.setLayout(QHBoxLayout())
        self.tabsConstructorQuery.addTab(self.tabUnionsAndAliases, "Объединения и псевдонимы")
        self.tabUnionsAndAliases.tabsQueries = QTabWidget()
        self.tabUnionsAndAliases.tabsQueries.setTabBarAutoHide(True)
        self.tabUnionsAndAliases.tabsQueries.setTabPosition(QTabWidget.East)
        self.tabUnionsAndAliases.layout().addWidget(self.tabUnionsAndAliases.tabsQueries)

        self.tabOrderBy = QWidget()
        self.tabOrderBy.setLayout(QHBoxLayout())
        self.tabsConstructorQuery.addTab(self.tabOrderBy, "Порядок")
        self.tabOrderBy.tabsQueries = QTabWidget()
        self.tabOrderBy.tabsQueries.setTabBarAutoHide(True)
        self.tabOrderBy.tabsQueries.setTabPosition(QTabWidget.East)
        self.tabOrderBy.layout().addWidget(self.tabOrderBy.tabsQueries)

        self.tabQueries = QWidget()
        self.tabQueries.setLayout(QHBoxLayout())
        self.tabsConstructorQuery.addTab(self.tabQueries, "Запросы")

        self.queryPanelWidget = QWidget()
        self.queryPanelWidget.setLayout(QHBoxLayout())

        self.addQueryButton = QPushButton('+')
        self.moveUpQueryButton = QPushButton('↑')
        self.moveDownQueryButton = QPushButton('↓')

        self.addQueryButton.clicked.connect(lambda: self.addQuery())

        self.queryPanelWidget.layout().addWidget(self.addQueryButton)
        self.queryPanelWidget.layout().addWidget(self.moveUpQueryButton)
        self.queryPanelWidget.layout().addWidget(self.moveDownQueryButton)
        self.queryPanelWidget.layout().addStretch()

        self.queriesWidget = QWidget()
        self.queriesWidget.setLayout(QVBoxLayout())
        self.queriesWidget.layout().addWidget(self.queryPanelWidget)

        self.queries = QTableWidget()
        self.queries.itemChanged.connect(self.renameTable)
        self.queriesWidget.layout().addWidget(self.queries)

        self.tabQueries.layout().addWidget(self.queriesWidget)

        self.queries.setColumnCount(2)
        self.queries.horizontalHeader().setStretchLastSection(True)

        self.lowerPanel = QWidget()
        self.lowerPanel.setLayout(QHBoxLayout())
        self.lowerPanel.layout().addStretch()
        self.buttonExecute = QPushButton('Выполнить')
        self.buttonExecute.clicked.connect(lambda: self.executeQuery.emit())
        self.lowerPanel.layout().addWidget(self.buttonExecute)
        self.layout().addWidget(self.lowerPanel)
        self.lowerPanel.layout().setContentsMargins(0, 0, 0, 0)

        sizePolicy = QSizePolicy()
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHorizontalStretch(255)
        self.lowerPanel.setSizePolicy(sizePolicy)

        self.addQuery(self.query)
        self.setCurrentQueryByIndex(0)
        self.updateParameters()

    def renameTable(self, itm):
        table = itm._object
        table.name = itm.text()

    def setParameter(self, row: int, column: int):
        param = self.parameters.item(row, 0).text()
        value = self.parameters.item(row, 1).text()
        type(self.query).mainQuery.parameters[param] = value

    def updateTextQuery(self):
        self.textQuery.setText(self.XQuery.mainQuery.textQuery)
        self.updateParameters()

    def updateParameters(self):
        # parameters = dict()
        # for row in range(self.parameters.rowCount()):
        #     parameters[self.parameters.item(row, 0).text()] = parameters[self.parameters.item(row, 1).text()]

        self.parameters.clear()
        self.parameters.setHorizontalHeaderLabels(['Параметр', 'Значение'])
        parametersQuery = self.XQuery.mainQuery.parameters
        self.parameters.setRowCount(len(parametersQuery))

        for row, (param, value) in enumerate(type(self.query).mainQuery.parameters.items()):
            self.parameters.cellChanged.disconnect()

            itm = QTableWidgetItem()
            itm.setText(param)
            itm.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)

            self.parameters.setItem(row, 0, itm)

            itm = QTableWidgetItem()
            if value != None:
                itm.setText(value)
            # itm.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)

            self.parameters.setItem(row, 1, itm)

            self.parameters.cellChanged.connect(self.setParameter)

    def setCurrentQueryByIndex(self, index: int):
        tabs = (self.tabTablesAndFields,
                self.tabJoins,
                self.tabConditions,
                self.tabConditionsAfterGrouping,
                self.tabUnionsAndAliases,
                self.tabOrderBy,
                )
        for tab in tabs:
            try:
                tab.tabsQueries.currentChanged.disconnect()
            except:
                pass
            tab.tabsQueries.setCurrentIndex(index)
            tab.tabsQueries.currentChanged.connect(self.setCurrentQueryByIndex)

        self.currentQuery = self.tabTablesAndFields.tabsQueries.currentWidget()._object

    def addQuery(self, query=None):
        if query == None:
            query = self.XQuery.addQuery()

        query.addedUnionQuery.connect(self.addUnionQuery)

        tabs = ((self.tabTablesAndFields, TablesAndFieldsWidget),
                (self.tabJoins, JoinsWidget),
                (self.tabConditions, ConditionsWidget),
                (self.tabConditionsAfterGrouping, ConditionsAfterGroupingWidget),
                )
        for tab, Widget in tabs:
            tabQuery = QWidget()
            tabQuery.setLayout(QHBoxLayout())
            tabQuery._object = query
            tab.tabsQueries.addTab(tabQuery, query.name)

            for i in range(tab.tabsQueries.count()):
                query = tab.tabsQueries.widget(i)._object
                tab.tabsQueries.setTabText(i, query.name)

            tabsUnion = QTabWidget()
            tabQuery.tabsUnion = tabsUnion
            tabsUnion.setTabBarAutoHide(True)
            tabsUnion.setTabPosition(QTabWidget.East)
            tabQuery.layout().addWidget(tabsUnion)
            widget = Widget(query)
            tabsUnion.addTab(widget, 'union1')

        tabs = ((self.tabUnionsAndAliases, UnionsAndAliases),
                (self.tabOrderBy, OrderBy),)
        #
        for tab, Widget in tabs:
            tabQuery = Widget(query)
            tabQuery._object = query
            tabQuery.updateData()
            tab.tabsQueries.addTab(tabQuery, query.name)

            query.changedFieldsQuery.connect(tabQuery.updateData)
            query.changedFieldsQuery.connect(tabQuery.updateData)
            query.changedSelectedTables.connect(tabQuery.updateData)
            query.changedFieldsOrderBy.connect(tabQuery.updateData)

            for i in range(tab.tabsQueries.count()):
                query = tab.tabsQueries.widget(i)._object
                tab.tabsQueries.setTabText(i, query.name)

        # self.updateUnions()
        self.queries.clear()
        self.queries.setColumnCount(2)
        self.queries.setHorizontalHeaderLabels(['Имя', 'Вложенный'])
        self.queries.setRowCount(len(self.XQuery.subqueries + self.XQuery.tablesTemp) + 1)

        for i, table in enumerate(self.XQuery.subqueries + self.XQuery.tablesTemp):
            itm = QTableWidgetItem()
            itm.setText(table.name)
            itm._object = table
            self.queries.setItem(i, 0, itm)

            itm = QCheckBox()
            itm._object = table
            itm.setChecked(table.query.type == 5)
            itm.stateChanged.connect(self.changeTypeTable)
            self.queries.setCellWidget(i, 1, itm)

        itm = QTableWidgetItem()
        itm.setText('**main**')
        itm.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        itm._object = self.XQuery.mainQuery
        self.queries.setItem(self.queries.rowCount() - 1, 0, itm)

    def changeTypeTable(self, state):
        table = self.sender()._object
        isTemp = state == 0

        if isTemp and table in self.XQuery.subqueries:
            self.XQuery.subqueries.remove(table)
            self.XQuery.tablesTemp.insert(0, table)
            table.query.type = self.TypesQuery.temp
        elif not isTemp and table in self.XQuery.tablesTemp:
            self.XQuery.tablesTemp.remove(table)
            self.XQuery.subqueries.append(table)
            table.query.type = self.TypesQuery.subQuery
        self.XQuery.updateTextQueries()
        self.textQuery.setText(self.XQuery.mainQuery.textQuery)
        # table.query.needUpdateTextQuery.emit()

    def addUnionQuery(self, query):

        tabs = ((self.tabTablesAndFields, TablesAndFieldsWidget),
                (self.tabJoins, JoinsWidget),
                (self.tabConditions, ConditionsWidget),
                (self.tabConditionsAfterGrouping, ConditionsAfterGroupingWidget),
                )
        for tab, Widget in tabs:
            widget = Widget(query)
            tab.tabsQueries.currentWidget().tabsUnion.addTab(widget,
                                                             query.name + str(len(self.currentQuery.unions) + 1))

    @staticmethod
    def getAddressInStorage(_object) -> str:
        """NoDocumentation"""
        address = str(randint(0, 100))
        QueryConstructor.dragAndDrop.clear()
        QueryConstructor.dragAndDrop[address] = _object
        return address

    @staticmethod
    def getObjectFromStorage(address) -> object:
        """NoDocumentation"""
        if address in QueryConstructor.dragAndDrop:
            res = QueryConstructor.dragAndDrop[address]
        else:
            res = None

        QueryConstructor.dragAndDrop.clear()
        return res

    def deleteObject(self) -> None:
        """NoDocumentation"""
        if self.unions.hasFocus():
            currentItem = self.unions.currentItem()
            currentRow = self.unions.currentRow()
            if currentItem == None:
                return
            query = currentItem._object
            self.unions.removeRow(currentRow)
            self.query.deleteUnionQuery(query)

            self.tabsUnionsTablesAndFields.removeTab(currentRow)
            self.tabsJoins.removeTab(currentRow)
            self.tabsConditions.removeTab(currentRow)
            self.tabsGrouping.removeTab(currentRow)
            self.tabsConditionsAfterGrouping.removeTab(currentRow)

        elif self.fieldsOrderBy.hasFocus():
            currentItem = self.fieldsOrderBy.currentItem()
            currentRow = self.fieldsOrderBy.currentRow()
            if currentItem == None:
                return
            orderBy = currentItem._object
            self.fieldsOrderBy.removeRow(currentRow)
            self.query.deleteFieldOrderBy(orderBy, True)
