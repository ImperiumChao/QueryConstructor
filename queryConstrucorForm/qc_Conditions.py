from PyQt5.QtWidgets import QWidget, QSplitter, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTreeWidget
from widgets.xTableWidget import XTableWidget
# from queryConstrucorForm.queryConstructor import QueryConstructor

class ConditionsWidget(QWidget):
    def __init__(self, query):
        super().__init__()
        # self.queryConstructor = queryConstructor
        self.query = query
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        self.splitter = QSplitter()
        self.layout.addWidget(self.splitter)

        self.fieldsForСonditions = QTreeWidget()
        self.splitter.addWidget(self.fieldsForСonditions)

        self.conditionsWidget = QWidget()
        self.conditionsWidget.setLayout(QVBoxLayout())
        self.splitter.addWidget(self.conditionsWidget)

        self.conditionsPanelWidget = QWidget()
        self.conditionsPanelWidget.setLayout(QHBoxLayout())
        self.conditionsWidget.layout().addWidget(self.conditionsPanelWidget)

        self.addCondition = QPushButton()
        self.addCondition.setText("+")
        self.conditionsPanelWidget.layout().addWidget(self.addCondition)

        self.conditions = QTableWidget()
        self.conditionsWidget.layout().addWidget(self.conditions)