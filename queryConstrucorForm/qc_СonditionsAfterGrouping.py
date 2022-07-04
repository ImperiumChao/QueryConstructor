from PyQt5.QtWidgets import QWidget, QSplitter, QVBoxLayout, QHBoxLayout, QPushButton, QShortcut, QTableWidgetItem
from PyQt5.QtCore import Qt
from widgets.xTableWidget import XTableWidget
from widgets.expressionEditor import ExpressonEditor
from expression import Expression
from typing import Union
from table import SelectedFieldTable, SelectedTable



class ConditionsAfterGroupingWidget(QWidget):
    def __init__(self, query):
        super().__init__()

        self.deleteshortcut = QShortcut(self)
        self.deleteshortcut.setKey(Qt.Key_Delete)
        self.deleteshortcut.activated.connect(self.deleteObject)

        self.query = query
        self.query.changedGroupingData.connect(self.updateData)
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        self.splitter = QSplitter()
        self.layout.addWidget(self.splitter)

        self.fieldsForСonditionsAfterGrouping = XTableWidget()
        self.fieldsForСonditionsAfterGrouping.verticalHeader().hide()
        self.fieldsForСonditionsAfterGrouping.setColumnCount(1)
        self.fieldsForСonditionsAfterGrouping.horizontalHeader().setStretchLastSection(True)
        self.fieldsForСonditionsAfterGrouping.setHorizontalHeaderLabels(('Доступные поля',))
        self.splitter.addWidget(self.fieldsForСonditionsAfterGrouping)

        self.conditionsAfterGroupingWidget = QWidget()
        self.conditionsAfterGroupingWidget.setLayout(QVBoxLayout())
        self.splitter.addWidget(self.conditionsAfterGroupingWidget)

        self.conditionsAfterGroupingPanelWidget = QWidget()
        self.conditionsAfterGroupingPanelWidget.setLayout(QHBoxLayout())
        self.conditionsAfterGroupingWidget.layout().addWidget(self.conditionsAfterGroupingPanelWidget)

        self.addConditionButton = QPushButton('+')
        self.addConditionButton.clicked.connect(self.addCondition)
        self.conditionsAfterGroupingPanelWidget.layout().addWidget(self.addConditionButton)
        self.conditionsAfterGroupingPanelWidget.layout().addStretch()
        self.conditionsAfterGroupingPanelWidget.layout().setContentsMargins(0, 0, 0, 0)

        self.conditions = XTableWidget()
        self.conditionsAfterGroupingWidget.layout().addWidget(self.conditions)
        self.conditions.setColumnCount(1)
        self.conditions.verticalHeader().hide()
        self.conditions.horizontalHeader().setStretchLastSection(True)
        self.conditions.setHorizontalHeaderLabels(('Условия',))
        self.conditions.dropped.connect(self.addConditionFromSelectedFields)
        self.conditions.mouseDoubleClicked.connect(self.editExpression)



    def deleteObject(self) -> None:
        """NoDocumentation"""
        if self.conditions.hasFocus():
            currentItem = self.conditions.currentItem()
            currentRow = self.conditions.currentRow()
            if currentItem == None:
                return
            expression = currentItem._object
            self.conditions.removeRow(currentRow)
            self.query.deleteConditionAfterGrouping(expression)

    def editExpression(self, expression: Expression) -> None:
        """NoDocumentation"""
        fields = XTableWidget()
        fields.setColumnCount(1)
        fields.setRowCount(0)
        fields.setHorizontalHeaderLabels(('Доступные поля',))
        for expression_ in self.query.fields:
            if not expression_.hasAggregation:
                continue

            itemTable = QTableWidgetItem()
            itemTable.setText(expression_.rawSqlText)
            itemTable.path = expression_.rawSqlText
            itemTable._object = expression_

            fields.addString((itemTable,))

        self.expressonEditor = ExpressonEditor(self, fields, expression)
        self.expressonEditor.show()
        self.expressonEditor.expressionEdited.connect(self.expressionEdited)

    def expressionEdited(self, expression: Expression, text: str) -> None:
        """NoDocumentation"""
        expression.setRawSqlText(text)
        self.updateData()

    def addConditionFromSelectedFields(self, _object: Expression) -> None:
        """NoDocumentation"""

        item = QTableWidgetItem()
        expression = self.query.addConditionAfterGrouping(_object)
        item._object = expression
        item.setText(expression.rawSqlText)
        # self.expressions[expression] = item
        self.conditions.addString([item])

    def updateData(self) -> None:
        """NoDocumentation"""
        self.fieldsForСonditionsAfterGrouping.clear()
        self.fieldsForСonditionsAfterGrouping.setColumnCount(1)
        self.fieldsForСonditionsAfterGrouping.setRowCount(0)
        self.fieldsForСonditionsAfterGrouping.setHorizontalHeaderLabels(('Доступные поля',))

        for expression in self.query.fields:
            if not expression.hasAggregation:
                continue

            itemTable = QTableWidgetItem()
            itemTable.setText(expression.rawSqlText)
            itemTable._object = expression

            self.fieldsForСonditionsAfterGrouping.addString((itemTable,))

        self.conditions.clear()
        self.conditions.setColumnCount(1)
        self.conditions.setRowCount(0)
        self.conditions.setHorizontalHeaderLabels(('Условия',))

        for expression in self.query.conditionsAfterGrouping:
            item = QTableWidgetItem()
            item._object = expression
            item.setText(expression.rawSqlText)
            # self.expressions[expression] = item
            self.conditions.addString([item])

    def addCondition(self) -> None:
        """NoDocumentation"""
        expression = self.query.addConditionAfterGrouping()
        self.updateData()
        self.editExpression(expression)
