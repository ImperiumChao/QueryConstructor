from PyQt5.QtWidgets import QDialog, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QDialogButtonBox, QSplitter
from PyQt5.QtCore import pyqtSignal
from widgets.xTreeWidget import XTreeWidget
from widgets.xTableWidget import XTableWidget
from copy import copy
from typing import Union
from expression import Expression
from table import SelectedFieldTable


class ExpressonEditor(QDialog):
    expressionEdited = pyqtSignal(object, str)

    def __init__(self, parent: QWidget, availablesFields: Union[XTreeWidget, XTableWidget], expression: Expression,
                 fieldForDraging: str = 'path'):
        super().__init__(parent)
        self.setWindowTitle(' ')
        self.expression = expression
        self.setLayout(QVBoxLayout())
        self.area1 = QWidget()
        self.layout().addWidget(self.area1)
        self.area1.setLayout(QHBoxLayout())
        self.splitter = QSplitter()
        self.area1.layout().addWidget(self.splitter)

        self.availableFields = availablesFields
        self.availableFields.fieldForDraging = fieldForDraging

        if type(self.availableFields) == XTreeWidget:
            self.availableFields.setHeaderLabel('Поля')
        else:
            self.availableFields.setHorizontalHeaderLabels(['Поля'])
            self.availableFields.verticalHeader().hide()
            self.availableFields.horizontalHeader().setStretchLastSection(True)

        self.splitter.addWidget(self.availableFields)
        self.textEdit = QTextEdit(expression.rawSqlText)
        self.splitter.addWidget(self.textEdit)
        self.buttons = QDialogButtonBox()
        self.buttons.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        self.layout().addWidget(self.buttons)
        self.buttons.rejected.connect(lambda: self.close())
        self.buttons.accepted.connect(self.acceptExpression)
        self.textEdit.setFocus()

    def acceptExpression(self) -> None:
        """NoDocumentation"""
        # self.expression.setRawSqlTextWithoutAgg(self.textEdit.toPlainText())
        self.expressionEdited.emit(self.expression, self.textEdit.toPlainText())
        self.close()
