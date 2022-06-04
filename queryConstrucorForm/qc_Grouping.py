from PyQt5.QtWidgets import QWidget, QSplitter, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTreeWidget
from PyQt5 import QtCore

class GroupingWidget(QWidget):
    def __init__(self, query):
        super().__init__()
        self.query = query
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        self.splitter = QSplitter()
        self.layout.addWidget(self.splitter)

        self.selectedFieldsForGrouping = QTableWidget()
        self.splitter.addWidget(self.selectedFieldsForGrouping)

        self.splitterGroupingFields = QSplitter()
        self.splitterGroupingFields.setOrientation(QtCore.Qt.Vertical)
        self.splitter.addWidget(self.splitterGroupingFields)

        self.groupingFields = QTableWidget()
        self.splitterGroupingFields.addWidget(self.groupingFields)

        self.aggregatedField = QTableWidget()
        self.splitterGroupingFields.addWidget(self.aggregatedField)