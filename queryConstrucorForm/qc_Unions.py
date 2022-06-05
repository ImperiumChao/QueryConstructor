from PyQt5.QtWidgets import QWidget, QSplitter, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTreeWidget, \
    QTextEdit, QTableWidgetItem, QComboBox, QItemDelegate, QLineEdit
from PyQt5 import QtCore, QtGui
# from xQuery import XQuery
from table import SelectedTable
from widgets.xTableWidget import XTableWidget
from typing import Dict
from collections import Counter
from PyQt5.QtCore import Qt
import pandas as pd
import xQuery


class UnionsWidget(QWidget):
    def __init__(self, query: "XQuery"):
        super().__init__()
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
        self.conditionsWidget.layout().addWidget(self.conditionsUnions)

    def addCondition(self) -> None:
        """NoDocumentation"""
        pass

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
        ch = self.getComboBoxTableSelection()
        ch.setCurrentText(union.table1.alias)
        w.layout().setContentsMargins(0, 0, 0, 0)
        w.layout().addWidget(ch)
        self.unions.setCellWidget(row, 0, w)

        w = QWidget()
        w.setLayout(QHBoxLayout())
        ch = self.getComboBoxTypeUnionSelection()
        w.layout().addWidget(ch)
        w.layout().setContentsMargins(0, 0, 0, 0)
        self.unions.setCellWidget(row, 1, w)

        w = QWidget()
        w.setLayout(QHBoxLayout())
        ch = self.getComboBoxTableSelection()
        ch.setCurrentText(union.table2.alias)
        w.layout().addWidget(ch)
        w.layout().setContentsMargins(0, 0, 0, 0)
        self.unions.setCellWidget(row, 2, w)





    def getComboBoxTableSelection(self) -> QComboBox:
        """NoDocumentation"""
        res = QComboBox()
        res.setLineEdit(QLineEdit())
        res.lineEdit().setReadOnly(True)
        res.setStyleSheet("QComboBox { qproperty-frame: false }");
        for tableAlias, selectedTable in self.query.selectedTables.items():
            res.addItem(tableAlias, selectedTable)
        return res

    def getComboBoxTypeUnionSelection(self) -> QComboBox:
        """NoDocumentation"""
        res = QComboBox()
        res.setLineEdit(QLineEdit())
        res.lineEdit().setReadOnly(True)
        res.setStyleSheet("QComboBox { qproperty-frame: false }");
        res.setEditable(True)
        # res.setStyleSheet('QComboBox::drop-down {width: 20px;}')
        # res.setEditable(True)
        for typeUnion in ('INNER', 'OUTER', 'LEFT', 'RIGHT'):
            res.addItem(typeUnion)
        return res

    def alowedAddTableForUnion(self, aliasTable: str, row: int, firstColumn: bool) -> bool:
        """NoDocumentation"""

        table = pd.DataFrame(columns=('aliasTable1', 'union', 'aliasTable2'))

        for index in range(self.unions.rowCount()):
            aliasTable1 = self.unions.cellWidget(index, 0)._object.alias
            aliasTable2 = self.unions.cellWidget(index, 2)._object.alias
            union = self.unions.cellWidget(index, 1).comboBox.currentText()

            if index == row:
                currentAliasTable1 = self.unions.cellWidget(index, 0)._object.alias
                currentAliasTable2 = self.unions.cellWidget(index, 2)._object.alias
                currentUnion = self.unions.cellWidget(index, 1).comboBox.currentText()
            else:
                table.append({'aliasTable1': aliasTable1, 'union': union, 'aliasTable2': aliasTable2})

        if firstColumn:
            return not table.query(f'aliasTable1 == \'{currentAliasTable1}\' AND union == \'RIGHT\'').empty
        else:
            if currentAliasTable1 == currentAliasTable2:
                return False
            else:
                unionsTable2 = table.query(
                    f'aliasTable1 == \'{currentAliasTable2}\' OR aliasTable2 == \'{currentAliasTable2}\'')
                for row in unionsTable2:
                    if row.aliasTable1 == currentAliasTable2:
                        anotherAliasTable = row.aliasTable2
                    else:
                        anotherAliasTable = row.aliasTable1
                    return not table.query(
                        f'(aliasTable1 == \'{currentAliasTable1}\' AND aliasTable2 == \'{anotherAliasTable}\') OR'
                        f'(aliasTable1 == \'{anotherAliasTable}\' AND aliasTable2 == \'{currentAliasTable1}\')')

            # currentUnionAliasTable1 = self.unions.cellWidget(row, 0)._object.alias
            #     for index in range(self.unions.rowCount()):
            #         aliasTable1 = self.unions.cellWidget(index, 0)._object.alias
            #         aliasTable2 = self.unions.cellWidget(index, 2)._object.alias
            #         typeUnion = self.unions.cellWidget(index, 1).currentText()
            #         if index == row:
            #             if aliasTable1 == aliasTable:
            #                 return False
            #             else:
            #                 counter = Counter()
            #                 for i in range(self.unions.rowCount()):
            #                     if i == row:
            #                         continue
            #         elif (aliasTable1 == currentUnionAliasTable1 and aliasTable2 == aliasTable) or \
            #                 (aliasTable2 == currentUnionAliasTable1 and aliasTable1 == aliasTable):
            #             return False
            #         elif
        return True

    def getComboBox(self, selectedTables: Dict[str, SelectedTable], column: int) -> None:
        """NoDocumentation"""
        pass




