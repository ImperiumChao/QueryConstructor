from PyQt5.QtWidgets import QWidget, QSplitter, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTreeWidget, \
    QTextEdit, QTableWidgetItem, QComboBox, QLineEdit, QTreeWidgetItem, QShortcut
from PyQt5 import QtCore, QtGui
# from xQuery import XQuery
from table import SelectedTable
from widgets.xTableWidget import XTableWidget
from widgets.xTreeWidget import XTreeWidget
from typing import Dict
from collections import Counter
from PyQt5.QtCore import Qt, pyqtSignal
from expression import Expression
from widgets.expressionEditor import ExpressonEditor
import pandas as pd
import xQuery

class XComboBox(QComboBox):
    def __init__(self):
        super().__init__()

class XLineEdit(QLineEdit):
    selectedUnion = pyqtSignal(object)

    def __init__(self):
        super().__init__()

    def mousePressEvent(self, e: QtGui.QMouseEvent) -> None:
        self.selectedUnion.emit(self.union)
        super().mousePressEvent(e)

class UnionsWidget(QWidget):
    def __init__(self, query: "XQuery"):
        super().__init__()

        self.deleteshortcut = QShortcut(self)
        self.deleteshortcut.setKey(Qt.Key_Delete)
        self.deleteshortcut.activated.connect(self.deleteObject)

        self.currentUnion = None
        self.query = query
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        self.splitter = QSplitter()
        self.layout.addWidget(self.splitter)

        self.unionsWidget = QWidget()
        self.unionsWidget.setLayout(QVBoxLayout())
        self.splitter.addWidget(self.unionsWidget)

        self.unionsPanelWidget = QWidget()
        self.unionsPanelWidget.setLayout(QHBoxLayout())
        self.unionsWidget.layout().addWidget(self.unionsPanelWidget)

        self.addUnionButton = QPushButton('+')
        self.addUnionButton.clicked.connect(self.addUnion)
        self.unionsPanelWidget.layout().addWidget(self.addUnionButton)
        self.unionsPanelWidget.layout().addStretch()
        self.unionsPanelWidget.layout().setContentsMargins(0, 0, 0, 0)

        self.unions = XTableWidget()
        self.unionsWidget.layout().addWidget(self.unions)
        self.unions.setColumnCount(3)
        self.unions.setHorizontalHeaderLabels(['Таблица 1', 'Вид связи', 'Таблица 2'])
        self.unions.horizontalHeader().setStretchLastSection(True)
        # self.unions.verticalHeader().hide()

        self.conditionsWidget = QWidget()
        self.conditionsWidget.setLayout(QVBoxLayout())
        self.splitter.addWidget(self.conditionsWidget)

        self.conditionsPanelWidget = QWidget()
        self.conditionsPanelWidget.setLayout(QHBoxLayout())
        self.conditionsWidget.layout().addWidget(self.conditionsPanelWidget)

        self.addConditionButton = QPushButton('+')
        self.addConditionButton.clicked.connect(self.addCondition)
        self.conditionsPanelWidget.layout().addWidget(self.addConditionButton)
        self.conditionsPanelWidget.layout().addStretch()
        self.conditionsPanelWidget.layout().setContentsMargins(0, 0, 0, 0)

        self.conditionsUnions = XTableWidget()
        self.conditionsUnions.setColumnCount(1)
        self.conditionsUnions.setHorizontalHeaderLabels(['Условия'])
        self.conditionsUnions.horizontalHeader().setStretchLastSection(True)
        self.conditionsWidget.layout().addWidget(self.conditionsUnions)
        self.conditionsUnions.mouseDoubleClicked.connect(self.editExpression)

    def editExpression(self, expression: Expression) -> None:
        """NoDocumentation"""
        self.selectedTables = XTreeWidget()
        for name, table in self.query.selectedTables.items():
            itemTable = QTreeWidgetItem()
            itemTable.setText(0, name)
            itemTable._object = table
            for field in table.fields.values():
                itemChield = QTreeWidgetItem()
                itemChield.setText(0, field.name)
                itemChield._object = field
                itemTable.addChild(itemChield)
            self.selectedTables.addTopLevelItem(itemTable)

        self.expressonEditor = ExpressonEditor(self, self.selectedTables, expression)
        self.expressonEditor.show()
        self.expressonEditor.expressionEdited.connect(self.expressionEdited)

    def deleteObject(self) -> None:
        """NoDocumentation"""
        if self.conditionsUnions.hasFocus():
            currentItem = self.conditionsUnions.currentItem()
            currentRow = self.conditionsUnions.currentRow()
            if currentItem == None:
                return
            expression = currentItem._object
            self.conditionsUnions.removeRow(currentRow)
            self.currentUnion.conditions.remove(expression)
        else:
            currentRow = self.unions.currentRow()
            if currentRow < 0:
                return
            union = self.query.unions[currentRow]
            self.unions.removeRow(currentRow)
            self.query.deleteUnion(union)
            if self.unions.rowCount() != 0:
                self.unions.selectRow(0)
                self.setCurrentUnion(self.unions.cellWidget(0, 0).comboBox.union)
            else:
                self.setCurrentUnion(None)

        self.updateConditionsUnion()


    def addCondition(self) -> None:
        """NoDocumentation"""
        expression = Expression(self.query)
        self.currentUnion.addCondition(expression)
        self.updateConditionsUnion()
        self.selectedTables = XTreeWidget()
        for name, table in self.query.selectedTables.items():
            itemTable = QTreeWidgetItem()
            itemTable.setText(0, name)
            itemTable._object = table
            for field in table.fields.values():
                itemChield = QTreeWidgetItem()
                itemChield.setText(0, field.name)
                itemChield._object = field
                itemTable.addChild(itemChield)

            self.selectedTables.addTopLevelItem(itemTable)
        self.expressionEditor = ExpressonEditor(self, self.selectedTables, expression)
        self.expressionEditor.show()
        self.expressionEditor.expressionEdited.connect(self.expressionEdited)

    def expressionEdited(self, expression: Expression, text: str) -> None:
        """NoDocumentation"""
        expression.setRawSqlText(text)
        self.updateConditionsUnion()

    def addUnion(self) -> None:
        """NoDocumentation"""
        union = self.query.addAndGetUnionAuto()
        if union == None:
            return
        row = self.unions.rowCount()
        self.unions.setRowCount(row+1)

        w = QWidget()
        # w.setContentsMargins(0, 0, 0, 0)
        w.setLayout(QHBoxLayout())
        ch = self.getComboBoxTableSelection(union, row, 0)
        ch.setCurrentText(union.table1.alias)
        w.comboBox = ch
        w.layout().setContentsMargins(0, 0, 0, 0)
        w.layout().addWidget(ch)
        self.unions.setCellWidget(row, 0, w)

        w = QWidget()
        w.setLayout(QHBoxLayout())
        ch = self.getComboBoxTypeUnionSelection(union)
        w.comboBox = ch
        w.layout().addWidget(ch)
        w.layout().setContentsMargins(0, 0, 0, 0)
        self.unions.setCellWidget(row, 1, w)

        w = QWidget()
        w.setLayout(QHBoxLayout())
        ch = self.getComboBoxTableSelection(union, row, 2)
        ch.setCurrentText(union.table2.alias)
        w.comboBox = ch
        w.layout().addWidget(ch)
        w.layout().setContentsMargins(0, 0, 0, 0)
        self.unions.setCellWidget(row, 2, w)
        if self.currentUnion == None:
            self.currentUnion = self.query.unions[0]
            self.updateConditionsUnion()


    def getComboBoxTableSelection(self, union, row: int, column: int) -> XComboBox:
        """NoDocumentation"""
        res = XComboBox()
        res.union = union
        res.row = row
        res.column = column
        res.setLineEdit(XLineEdit())
        res.lineEdit().union = union
        res.lineEdit().setReadOnly(True)
        res.setStyleSheet("QComboBox { qproperty-frame: false }");
        for tableAlias, selectedTable in self.query.selectedTables.items():
            res.addItem(tableAlias, selectedTable)

        res.activated.connect(self.selectedTableUnion)
        res.lineEdit().selectedUnion.connect(self.setCurrentUnion)
        return res

    def selectedTableUnion(self) -> None:
        """NoDocumentation"""
        comboBox: XComboBox = self.sender()
        union: xQuery.Union = comboBox.union
        row: int = comboBox.row
        column: int = comboBox.column
        assert column in (0, 2)

        if column == 0:
            newTable1 = comboBox.currentData()
            if union.table2 == newTable1:
                comboBoxOtherTable = self.unions.cellWidget(row, 2).comboBox
                comboBoxOtherTable.setCurrentText(union.table1.alias)
                union.setTable2(union.table1)
            union.setTable1(newTable1)
        elif column == 2:
            newTable2 = comboBox.currentData()
            if union.table1 == newTable2:
                comboBoxOtherTable = self.unions.cellWidget(row, 0).comboBox
                comboBoxOtherTable.setCurrentText(union.table2.alias)
                union.setTable1(union.table2)
            union.setTable2(newTable2)


    def getComboBoxTypeUnionSelection(self, union) -> XComboBox:
        """NoDocumentation"""
        res = XComboBox()
        res.union = union
        res.setLineEdit(XLineEdit())
        res.lineEdit().union = union
        res.lineEdit().setReadOnly(True)
        res.setStyleSheet("QComboBox { qproperty-frame: false }");
        res.setEditable(True)
        for typeUnion in ('INNER', 'OUTER', 'LEFT', 'RIGHT'):
            res.addItem(typeUnion)
        res.activated.connect(self.selectedTypeUnion)
        res.lineEdit().selectedUnion.connect(self.setCurrentUnion)
        return res

    def setCurrentUnion(self, union) -> None:
        """NoDocumentation"""
        self.currentUnion = union
        if self.currentUnion != None:
            self.unions.selectRow(self.query.unions.index(union))
        self.updateConditionsUnion()

    def updateConditionsUnion(self) -> None:
        """NoDocumentation"""
        self.conditionsUnions.clear()
        self.conditionsUnions.setRowCount(0)
        self.conditionsUnions.setHorizontalHeaderLabels(['Условия'])
        if self.currentUnion == None:
            return
        for expression in self.currentUnion.conditions:
            item = QTableWidgetItem()
            item.setText(expression.rawSqlText)
            item._object = expression
            self.conditionsUnions.addString((item,))

    def selectedTypeUnion(self) -> None:
        """NoDocumentation"""
        comboBox: XComboBox = self.sender()
        union: xQuery.Union = comboBox.union
        union.setTypeUnion(comboBox.currentText())




