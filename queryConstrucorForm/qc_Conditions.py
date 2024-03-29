from PyQt5.QtWidgets import QWidget, QSplitter, QVBoxLayout, QHBoxLayout, QPushButton, QTreeWidget, QTreeWidgetItem, \
    QTableWidgetItem, QShortcut
from expression import Expression
from PyQt5.QtCore import Qt
from widgets.xTreeWidget import XTreeWidget
from widgets.xTableWidget import XTableWidget
from widgets.expressionEditor import ExpressonEditor
from table import SelectedTable, SelectedFieldTable
from typing import Union

# from queryConstrucorForm.queryConstructor import QueryConstructor

class ConditionsWidget(QWidget):


    def __init__(self, query):
        super().__init__()

        self.deleteshortcut = QShortcut(self)
        self.deleteshortcut.setKey(Qt.Key_Delete)
        self.deleteshortcut.activated.connect(self.deleteObject)

        self.query = query
        self.query.changedSelectedTables.connect(self.updateSelectedFields)
        self.query.changedConditions.connect(self.updateConditions)
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        self.splitter = QSplitter()
        self.layout.addWidget(self.splitter)

        self.fieldsForСonditions = XTreeWidget()
        self.fieldsForСonditions.setHeaderLabel('Доступные поля')
        self.splitter.addWidget(self.fieldsForСonditions)

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

        self.conditions = XTableWidget()
        self.conditions.setColumnCount(1)
        self.conditions.verticalHeader().hide()
        self.conditions.horizontalHeader().setStretchLastSection(True)
        self.conditions.setHorizontalHeaderLabels(('Условия',))
        self.conditionsWidget.layout().addWidget(self.conditions)
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
            self.query.deleteCondition(expression, True)

    def editExpression(self, expression: Expression) -> None:
        """NoDocumentation"""
        self.expressonEditor = ExpressonEditor(self, self.fieldsForСonditions.clone(), expression)
        self.expressonEditor.show()
        self.expressonEditor.expressionEdited.connect(self.expressionEdited)

    def expressionEdited(self, expression: Expression, text: str) -> None:
        """NoDocumentation"""
        expression.setRawSqlText(text)
        for row in range(self.conditions.rowCount()):
            item = self.conditions.item(row, 0)
            if item._object == expression:
                item.setText(text)
                break

    def addConditionFromSelectedFields(self, _object: Union[SelectedTable, SelectedFieldTable]) -> None:
        """NoDocumentation"""
        if type(_object) is SelectedFieldTable:
            item = QTableWidgetItem()
            expression = self.query.addCondition(_object, True)
            item._object = expression
            item.setText(expression.rawSqlText)
            # self.expressions[expression] = item
            self.conditions.addString([item])

    def updateSelectedFields(self) -> None:
        """NoDocumentation"""
        self.fieldsForСonditions.clear()
        for selectedTable in self.query.selectedTables:
            itemTable = QTreeWidgetItem()
            itemTable.setText(0, selectedTable.alias)
            itemTable._object = selectedTable
            for field in selectedTable.fields:
                itemChield = QTreeWidgetItem()
                itemChield.setText(0, field.name)
                itemChield._object = field
                itemTable.addChild(itemChield)
            self.fieldsForСonditions.addTopLevelItem(itemTable)

    def updateConditions(self) -> None:
        """NoDocumentation"""
        self.conditions.clear()
        self.conditions.setColumnCount(1)
        self.conditions.setRowCount(0)
        self.conditions.setHorizontalHeaderLabels(('Условия',))
        for expression in self.query.conditions:
            item = QTableWidgetItem()
            item._object = expression
            item.setText(expression.rawSqlText)
            self.conditions.addString([item])

    def addCondition(self) -> None:
        """NoDocumentation"""
        expression = self.query.addCondition(noSignal=True)
        item = QTableWidgetItem()
        item._object = expression
        item.setText(expression.rawSqlText)
        self.conditions.addString([item])

        self.expressionEditor = ExpressonEditor(self, self.fieldsForСonditions.clone(), expression)
        self.expressionEditor.show()
        self.expressionEditor.expressionEdited.connect(self.expressionEdited)