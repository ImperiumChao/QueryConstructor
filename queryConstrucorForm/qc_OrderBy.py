from PyQt5.QtWidgets import QWidget, QSplitter, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTreeWidget, \
    QTreeWidgetItem, QSpacerItem, QTableWidgetItem, QShortcut, QComboBox, QLineEdit
from table import Table, FieldTable, SelectedTable, SelectedFieldTable

import xQuery as qc
from widgets.xTreeWidget import XTreeWidget
from widgets.xTableWidget import XTableWidget
from PyQt5.QtCore import pyqtSignal, Qt
from expression import Expression
from typing import Union
from widgets.expressionEditor import ExpressonEditor


class OrderBy(QWidget):
    def __init__(self, query):
        super().__init__()
        self.query = query
        self.setLayout(QHBoxLayout())
        self.splitterOrderBy = QSplitter()
        self.layout().addWidget(self.splitterOrderBy)

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

    def addFieldOrderBy(self, _object: Union[Expression, SelectedTable, SelectedFieldTable]) -> None:
        """NoDocumentation"""
        if type(_object) in (Expression, SelectedFieldTable):
            self.query.addFieldOrderBy(_object)

    def updateData(self) -> None:
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
