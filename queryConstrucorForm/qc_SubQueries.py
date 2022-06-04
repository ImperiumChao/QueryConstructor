from PyQt5.QtWidgets import QWidget, QSplitter, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTreeWidget, \
    QTextEdit

class SubQueriesWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        self.subQueries = QTableWidget()
        self.layout.addWidget(self.subQueries)

        self.textSubQueriesWidget = QWidget()
        self.textSubQueriesWidget.setLayout(QVBoxLayout())
        self.layout.addWidget(self.textSubQueriesWidget)

        self.textSubQueriesPanelWidget = QWidget()
        self.textSubQueriesPanelWidget.setLayout(QHBoxLayout())
        self.textSubQueriesWidget.layout().addWidget(self.textSubQueriesPanelWidget)

        self.openQueryConstructor = QPushButton()
        self.openQueryConstructor.setText("Открыть конструктор запроса")
        self.textSubQueriesPanelWidget.layout().addWidget(self.openQueryConstructor)

        self.textSubQueries = QTextEdit()
        self.textSubQueriesWidget.layout().addWidget(self.textSubQueries)