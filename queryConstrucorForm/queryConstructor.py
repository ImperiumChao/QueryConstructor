from PyQt5.QtWidgets import QWidget, QTabWidget, QTreeWidget, QListWidget, QPushButton, QVBoxLayout, \
    QHBoxLayout, QSplitter, QTableWidget, QTextEdit, QShortcut, QTableWidgetItem, QLineEdit, QComboBox, QTreeWidgetItem

from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from queryConstrucorForm.qc_Conditions import ConditionsWidget
from queryConstrucorForm.qc_Grouping import GroupingWidget
from queryConstrucorForm.qc_SubQueries import SubQueriesWidget
from queryConstrucorForm.qc_TablesAndFields import TablesAndFieldsWidget
from queryConstrucorForm.qc_Joins import JoinsWidget
from queryConstrucorForm.qc_СonditionsAfterGrouping import ConditionsAfterGroupingWidget
from widgets.xTreeWidget import XTreeWidget
from widgets.xTableWidget import XTableWidget
from table import SelectedTable, SelectedFieldTable
from expression import Expression
from random import randint
from typing import Union


class QueryConstructor(QWidget):
    dragAndDrop = dict()

    def __init__(self, query):
        super().__init__()

        self.deleteshortcut = QShortcut(self)
        self.deleteshortcut.setKey(Qt.Key_Delete)
        self.deleteshortcut.activated.connect(self.deleteObject)

        self.setWindowTitle('Конструктор запросов')
        self.query = query
        self.query.changedFieldsQuery.connect(self.updateUnions)
        self.query.changedFieldsQuery.connect(self.updateOrderBy)
        self.query.changedSelectedTables.connect(self.updateOrderBy)
        self.query.changedFieldsOrderBy.connect(self.updateOrderBy)

        self.setLayout(QHBoxLayout())
        self.textQuery = QTextEdit()
        self.textQuery.setReadOnly(True)
        self.layout().addWidget(self.textQuery)
        self.tabsConstructorQuery = QTabWidget()
        self.layout().addWidget(self.tabsConstructorQuery)

        self.tabTablesAndFields = QWidget()
        self.tabTablesAndFields.setLayout(QHBoxLayout())
        self.tabsConstructorQuery.addTab(self.tabTablesAndFields, "Таблицы и поля")
        self.tabsTablesAndFields = QTabWidget()
        self.tabsTablesAndFields.setTabPosition(QTabWidget.East)
        self.tabTablesAndFields.layout().addWidget(self.tabsTablesAndFields)

        self.tabJoins = QWidget()
        self.tabJoins.setLayout(QVBoxLayout())
        self.tabsConstructorQuery.addTab(self.tabJoins, "Связи")
        self.tabsJoins = QTabWidget()
        self.tabsJoins.setTabPosition(QTabWidget.East)
        self.tabJoins.layout().addWidget(self.tabsJoins)

        self.tabConditions = QWidget()
        self.tabConditions.setLayout(QVBoxLayout())
        self.tabsConstructorQuery.addTab(self.tabConditions, "Условия")
        self.tabsConditions = QTabWidget()
        self.tabsConditions.setTabPosition(QTabWidget.East)
        self.tabConditions.layout().addWidget(self.tabsConditions)

        self.tabGrouping = QWidget()
        self.tabGrouping.setLayout(QHBoxLayout())
        self.tabsConstructorQuery.addTab(self.tabGrouping, "Группировка")
        self.tabsGrouping = QTabWidget()
        self.tabsGrouping.setTabPosition(QTabWidget.East)
        self.tabGrouping.layout().addWidget(self.tabsGrouping)

        self.tabConditionsAfterGrouping = QWidget()
        self.tabConditionsAfterGrouping.setLayout(QVBoxLayout())
        self.tabsConstructorQuery.addTab(self.tabConditionsAfterGrouping, "Условия после группировки")
        self.tabsConditionsAfterGrouping = QTabWidget()
        self.tabsConditionsAfterGrouping.setTabPosition(QTabWidget.East)
        self.tabConditionsAfterGrouping.layout().addWidget(self.tabsConditionsAfterGrouping)


        self.tabUnionsAndAliases = QWidget()
        self.tabUnionsAndAliases.setLayout(QHBoxLayout())
        layout = self.tabUnionsAndAliases.layout()

        self.unionsWidget = QWidget()
        self.unionsWidget.setLayout(QVBoxLayout())

        self.unionsPanelWidget = QWidget()
        self.unionsPanelWidget.setLayout(QHBoxLayout())
        self.addUnionButton = QPushButton('+')
        self.addUnionButton.pressed.connect(self.addQuery)
        self.unionsPanelWidget.layout().addWidget(self.addUnionButton)
        self.unionsPanelWidget.layout().addStretch()
        self.unionsPanelWidget.layout().setContentsMargins(0, 0, 0, 0)
        self.unionsWidget.layout().addWidget(self.unionsPanelWidget)

        self.unions = QTableWidget()
        self.unions.cellClicked.connect(self.selectedCurrentQuery)

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

        self.tabsConstructorQuery.addTab(self.tabUnionsAndAliases, "Объединения и псевдонимы")


        self.tabOrderBy = QWidget()
        self.tabOrderBy.setLayout(QHBoxLayout())
        self.splitterOrderBy = QSplitter()
        self.tabOrderBy.layout().addWidget(self.splitterOrderBy)

        self.availableFieldsOrderBy = XTreeWidget()
        self.splitterOrderBy.addWidget(self.availableFieldsOrderBy)

        self.fieldsOrderByWidget = QWidget()
        self.fieldsOrderByWidget.setLayout(QVBoxLayout())
        self.splitterOrderBy.addWidget(self.fieldsOrderByWidget)

        self.fieldsOrderByPanelWidget = QWidget()
        self.fieldsOrderByPanelWidget.setLayout(QHBoxLayout())
        self.fieldsOrderByWidget.layout().addWidget(self.fieldsOrderByPanelWidget)

        self.moveUpOrderByButton = QPushButton('↑')
        self.fieldsOrderByPanelWidget.layout().addWidget(self.moveUpOrderByButton)

        self.moveDownSorting = QPushButton('↓')
        self.fieldsOrderByPanelWidget.layout().addWidget(self.moveDownSorting)

        self.fieldsOrderByPanelWidget.layout().addStretch()
        self.fieldsOrderByPanelWidget.layout().setContentsMargins(0, 0, 0, 0)

        self.fieldsOrderBy = XTableWidget()
        self.fieldsOrderBy.verticalHeader().hide()
        self.fieldsOrderBy.horizontalHeader().setStretchLastSection(True)
        self.fieldsOrderBy.dropped.connect(self.addFieldOrderBy)
        self.fieldsOrderByWidget.layout().addWidget(self.fieldsOrderBy)
        self.tabsConstructorQuery.addTab(self.tabOrderBy, "Порядок")


        self.addQuery(self.query)
        self.currentQuery = self.query


    def addFieldOrderBy(self, _object: Union[Expression, SelectedTable, SelectedFieldTable]) -> None:
        """NoDocumentation"""
        if type(_object) in (Expression, SelectedFieldTable):
            self.query.addFieldOrderBy(_object)

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

    def updateOrderBy(self) -> None:
        """NoDocumentation"""
        self.availableFieldsOrderBy.clear()
        self.availableFieldsOrderBy.setHeaderLabel('Поля')
        for expression in self.query.fields:
            if self.query.find(self.query.orderBy, 'field', expression) != None:
                continue

            itemTable = QTreeWidgetItem()
            itemTable.setText(0, expression.alias)
            itemTable._object = expression
            self.availableFieldsOrderBy.addTopLevelItem(itemTable)

        if not self.query.usingGrouping and len(self.query.unions) == 0:
            for selectedTable in self.query.selectedTables:
                itemTable = QTreeWidgetItem()
                itemTable.setText(0, selectedTable.alias)
                itemTable._object = selectedTable

                for selectedField in selectedTable.fields:
                    itemChield = QTreeWidgetItem()
                    itemChield.setText(0, selectedField.path)
                    itemChield._object = selectedField
                    itemTable.addChild(itemChield)

                self.availableFieldsOrderBy.addTopLevelItem(itemTable)

        self.fieldsOrderBy.clear()
        self.fieldsOrderBy.setColumnCount(2)
        self.fieldsOrderBy.setRowCount(len(self.query.orderBy))
        self.fieldsOrderBy.setHorizontalHeaderLabels(('Поле', 'Сортировка'))

        for row, orderBy in enumerate(self.query.orderBy):
            field: Union[Expression, SelectedFieldTable] = orderBy.field
            item = QTableWidgetItem()
            if type(field) == Expression:
                item.setText(field.alias)
            elif type(field) == SelectedFieldTable:
                item.setText(field.path)
            item._object = orderBy
            self.fieldsOrderBy.setItem(row, 0, item)

            comboBox = self.getComboBoxTypeOfSorting(orderBy)
            comboBox.setCurrentText(orderBy.typeOfSorting)
            self.fieldsOrderBy.setCellWidget(row, 1, comboBox)


    def getComboBoxTypeOfSorting(self, _object) -> QComboBox:
        """NoDocumentation"""
        res = QComboBox()
        res._object = _object
        res.setLineEdit(QLineEdit())
        res.lineEdit()._object = _object
        res.lineEdit().setReadOnly(True)
        res.setStyleSheet("QComboBox { qproperty-frame: false }");
        res.addItem('ASC')
        res.addItem('DESC')

        res.activated.connect(self.selectedTypeOfSorting)
        # res.lineEdit().selectedJoin.connect(self.setCurrentJoin)
        return res

    def selectedTypeOfSorting(self) -> None:
        """NoDocumentation"""
        comboBox: QComboBox = self.sender()
        self.query.setTypeOfSorting(comboBox._object, comboBox.currentText(), True)

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
        self.query.moveField(row, up, True)

    def setAliasForExpression(self, itm) -> None:
        """NoDocumentation"""
        expression = itm._object
        expression.alias = itm.text()

    def selectedCurrentQuery(self, row, column) -> None:
        """NoDocumentation"""
        self.currentQuery = self.unions.item(row, 1)._object
        self.updateUnions()
        currentItem = self.unions.item(row, column)
        self.unions.setCurrentItem(currentItem)
        self.fieldsCurrentQuery.setHorizontalHeaderLabels((currentItem.text(),))


    def updateUnions(self) -> None:
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

            self.unions.setCellWidget(n+1, 0, self.getComboBoxTypeUnionSelection(union))

            itm = QTableWidgetItem()
            itm.setText(f'Запрос {str(n+2)}')
            itm.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            itm._object = union.query
            self.unions.setItem(n+1, 1, itm)


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
        for expression in self.currentQuery.fields:
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

    def addQuery(self, query=None) -> None:
        """Добавляем либо первый запрос, либо еще один на объединение"""
        if query==None:
            query = self.query.addUnionQuery()
            query.changedFieldsQuery.connect(self.updateUnions)

        numQuery = len(self.query.unions)+1
        nameQuery = f'Запрос {str(numQuery)}'
        widget = TablesAndFieldsWidget(query)
        self.tabsTablesAndFields.addTab(widget, nameQuery)

        widget = JoinsWidget(query)
        self.tabsJoins.addTab(widget, nameQuery)

        widget = ConditionsWidget(query)
        self.tabsConditions.addTab(widget, nameQuery)

        widget = GroupingWidget(query)
        self.tabsGrouping.addTab(widget, nameQuery)

        widget = ConditionsAfterGroupingWidget(query)
        self.tabsConditionsAfterGrouping.addTab(widget, nameQuery)
        self.tabsConstructorQuery.setCurrentIndex(0)
        self.tabsTablesAndFields.setCurrentIndex(numQuery-1)


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

            self.tabsTablesAndFields.removeTab(currentRow)
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

