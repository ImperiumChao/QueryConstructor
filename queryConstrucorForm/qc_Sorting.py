from PyQt5.QtWidgets import QWidget, QSplitter, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTreeWidget

class SortingWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        self.aliasesOrderBy = QTableWidget()
        self.layout.addWidget(self.aliasesOrderBy)

        self.sortingFieldsWidget = QWidget()
        self.sortingFieldsWidget.setLayout(QVBoxLayout())
        self.layout.addWidget(self.sortingFieldsWidget)

        self.sortingFieldsPanelWidget = QWidget()
        self.sortingFieldsPanelWidget.setLayout(QHBoxLayout())
        self.sortingFieldsWidget.layout().addWidget(self.sortingFieldsPanelWidget)

        self.moveUpSorting = QPushButton()
        self.moveUpSorting.setText("↑")
        self.sortingFieldsPanelWidget.layout().addWidget(self.moveUpSorting)

        self.moveDownSorting = QPushButton()
        self.moveDownSorting.setText("↓")
        self.sortingFieldsPanelWidget.layout().addWidget(self.moveDownSorting)

        self.sortingFields = QTableWidget()
        self.sortingFieldsWidget.layout().addWidget(self.sortingFields)