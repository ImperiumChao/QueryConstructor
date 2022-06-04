from PyQt5.QtWidgets import QWidget, QSplitter, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTreeWidget

class ConditionsAfterGroupingWidget(QWidget):
    def __init__(self, query):
        super().__init__()
        self.query = query
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        self.splitter = QSplitter()
        self.layout.addWidget(self.splitter)

        self.fieldsForСonditionsAfterGrouping = QTableWidget()
        self.splitter.addWidget(self.fieldsForСonditionsAfterGrouping)

        self.conditionsAfterGroupingWidget = QWidget()
        self.conditionsAfterGroupingWidget.setLayout(QVBoxLayout())
        self.splitter.addWidget(self.conditionsAfterGroupingWidget)

        self.conditionsAfterGroupingPanelWidget = QWidget()
        self.conditionsAfterGroupingPanelWidget.setLayout(QHBoxLayout())
        self.conditionsAfterGroupingWidget.layout().addWidget(self.conditionsAfterGroupingPanelWidget)

        self.addCondition = QPushButton()
        self.addCondition.setText("+")
        self.conditionsAfterGroupingPanelWidget.layout().addWidget(self.addCondition)

        self.conditions = QTableWidget()
        self.conditionsAfterGroupingWidget.layout().addWidget(self.conditions)