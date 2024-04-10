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
    selectedJoin = pyqtSignal(object)

    def __init__(self):
        super().__init__()

    def mousePressEvent(self, e: QtGui.QMouseEvent) -> None:
        self.selectedJoin.emit(self.join)
        super().mousePressEvent(e)


class JoinsWidget(QWidget):
    def __init__(self, query: "XQuery"):
        super().__init__()

        self.deleteshortcut = QShortcut(self)
        self.deleteshortcut.setKey(Qt.Key_Delete)
        self.deleteshortcut.activated.connect(self.deleteObject)

        self.currentJoin = None
        self.query = query
        self.query.changedJoins.connect(self.updateData)
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        self.splitter = QSplitter()
        self.layout.addWidget(self.splitter)

        self.joinsWidget = QWidget()
        self.joinsWidget.setLayout(QVBoxLayout())
        self.splitter.addWidget(self.joinsWidget)

        self.joinsPanelWidget = QWidget()
        self.joinsPanelWidget.setLayout(QHBoxLayout())
        self.joinsWidget.layout().addWidget(self.joinsPanelWidget)

        self.addJoinButton = QPushButton('+')
        self.addJoinButton.clicked.connect(self.addJoinAuto)
        self.joinsPanelWidget.layout().addWidget(self.addJoinButton)
        self.joinsPanelWidget.layout().addStretch()
        self.joinsPanelWidget.layout().setContentsMargins(0, 0, 0, 0)

        self.joins = XTableWidget()
        self.joinsWidget.layout().addWidget(self.joins)
        self.joins.setColumnCount(3)
        self.joins.setHorizontalHeaderLabels(['Таблица 1', 'Вид связи', 'Таблица 2'])
        self.joins.horizontalHeader().setStretchLastSection(True)

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

        self.conditionsJoin = XTableWidget()
        self.conditionsJoin.setColumnCount(1)
        self.conditionsJoin.setHorizontalHeaderLabels(['Условия'])
        self.conditionsJoin.horizontalHeader().setStretchLastSection(True)
        self.conditionsWidget.layout().addWidget(self.conditionsJoin)
        self.conditionsJoin.mouseDoubleClicked.connect(self.editExpression)

    def updateData(self):
        for join in self.query.joins:
            self.addJoin(join)

    def editExpression(self, expression: Expression) -> None:
        """NoDocumentation"""
        self.selectedTables = XTreeWidget()
        for selectedTable in self.query.selectedTables:
            itemTable = QTreeWidgetItem()
            itemTable.setText(0, selectedTable.alias)
            itemTable._object = selectedTable
            for field in selectedTable.fields:
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
        if self.conditionsJoin.hasFocus():
            currentItem = self.conditionsJoin.currentItem()
            currentRow = self.conditionsJoin.currentRow()
            if currentItem == None:
                return
            expression = currentItem._object
            self.conditionsJoin.removeRow(currentRow)
            self.currentJoin.conditions.remove(expression)
            type(self.query).updateTextQueries()
        else:
            currentRow = self.joins.currentRow()
            if currentRow < 0:
                return
            join = self.query.joins[currentRow]
            self.joins.removeRow(currentRow)
            self.query.deleteJoin(join)
            if self.joins.rowCount() != 0:
                self.joins.selectRow(0)
                self.setCurrentJoin(self.joins.cellWidget(0, 0).comboBox.join)
            else:
                self.setCurrentJoin(None)

        self.updateConditionsJoin()

    def addCondition(self) -> None:
        """NoDocumentation"""
        expression = Expression(self.query)
        self.currentJoin.addCondition(expression)
        self.updateConditionsJoin()
        self.selectedTables = XTreeWidget()
        for selectedTable in self.query.selectedTables:
            itemTable = QTreeWidgetItem()
            itemTable.setText(0, selectedTable.alias)
            itemTable._object = selectedTable
            for field in selectedTable.fields:
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
        self.updateConditionsJoin()

    def addJoinAuto(self) -> None:
        """NoDocumentation"""
        join = self.query.addJoinAuto(True)
        if join != None:
            self.addJoin(join)

    def addJoin(self, join):
        row = self.joins.rowCount()
        self.joins.setRowCount(row + 1)

        w = QWidget()
        # w.setContentsMargins(0, 0, 0, 0)
        w.setLayout(QHBoxLayout())
        ch = self.getComboBoxTableSelection(join, row, 0)
        ch.setCurrentText(join.table1.alias)
        w.comboBox = ch
        w.layout().setContentsMargins(0, 0, 0, 0)
        w.layout().addWidget(ch)
        self.joins.setCellWidget(row, 0, w)

        w = QWidget()
        w.setLayout(QHBoxLayout())
        ch = self.getComboBoxTypeJoinSelection(join)
        w.comboBox = ch
        w.layout().addWidget(ch)
        w.layout().setContentsMargins(0, 0, 0, 0)
        self.joins.setCellWidget(row, 1, w)

        w = QWidget()
        w.setLayout(QHBoxLayout())
        ch = self.getComboBoxTableSelection(join, row, 2)
        ch.setCurrentText(join.table2.alias)
        w.comboBox = ch
        w.layout().addWidget(ch)
        w.layout().setContentsMargins(0, 0, 0, 0)
        self.joins.setCellWidget(row, 2, w)
        if self.currentJoin == None:
            self.currentJoin = self.query.joins[0]
            self.updateConditionsJoin()

    def getComboBoxTableSelection(self, join, row: int, column: int) -> XComboBox:
        """NoDocumentation"""
        res = XComboBox()
        res.join = join
        res.row = row
        res.column = column
        res.setLineEdit(XLineEdit())
        res.lineEdit().join = join
        res.lineEdit().setReadOnly(True)
        res.setStyleSheet("QComboBox { qproperty-frame: false }");
        for selectedTable in self.query.selectedTables:
            res.addItem(selectedTable.alias, selectedTable)

        res.activated.connect(self.selectedTableJoin)
        res.lineEdit().selectedJoin.connect(self.setCurrentJoin)
        return res

    def selectedTableJoin(self) -> None:
        """NoDocumentation"""
        comboBox: XComboBox = self.sender()
        join: xQuery.Join = comboBox.join
        row: int = comboBox.row
        column: int = comboBox.column
        assert column in (0, 2)

        if column == 0:
            newTable1 = comboBox.currentData()
            if join.table2 == newTable1:
                comboBoxOtherTable = self.joins.cellWidget(row, 2).comboBox
                comboBoxOtherTable.setCurrentText(join.table1.alias)
                join.setTable2(join.table1, noSignal=True)
            join.setTable1(newTable1)
        elif column == 2:
            newTable2 = comboBox.currentData()
            if join.table1 == newTable2:
                comboBoxOtherTable = self.joins.cellWidget(row, 0).comboBox
                comboBoxOtherTable.setCurrentText(join.table2.alias)
                join.setTable1(join.table2, noSignal=True)
            join.setTable2(newTable2)

    def getComboBoxTypeJoinSelection(self, join) -> XComboBox:
        """NoDocumentation"""
        res = XComboBox()
        res.join = join
        res.setLineEdit(XLineEdit())
        res.lineEdit().join = join
        res.lineEdit().setReadOnly(True)
        res.setStyleSheet("QComboBox { qproperty-frame: false }");
        res.setEditable(True)
        for typeJoin in ('INNER', 'OUTER', 'LEFT', 'RIGHT'):
            res.addItem(typeJoin)
        res.activated.connect(self.selectedTypeJoin)
        res.lineEdit().selectedJoin.connect(self.setCurrentJoin)
        return res

    def setCurrentJoin(self, join) -> None:
        """NoDocumentation"""
        self.currentJoin = join
        if self.currentJoin != None:
            self.joins.selectRow(self.query.joins.index(join))
        self.updateConditionsJoin()

    def updateConditionsJoin(self) -> None:
        """NoDocumentation"""
        self.conditionsJoin.clear()
        self.conditionsJoin.setRowCount(0)
        self.conditionsJoin.setHorizontalHeaderLabels(['Условия'])
        if self.currentJoin == None:
            return
        for expression in self.currentJoin.conditions:
            item = QTableWidgetItem()
            item.setText(expression.rawSqlText)
            item._object = expression
            self.conditionsJoin.addString((item,))

    def selectedTypeJoin(self) -> None:
        """NoDocumentation"""
        comboBox: XComboBox = self.sender()
        join = comboBox.join
        join.setTypeJoin(comboBox.currentText())
