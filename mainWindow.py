from PyQt5.QtWidgets import QWidget, QTabWidget, QTreeWidget, QListWidget, QPushButton, QVBoxLayout, \
    QHBoxLayout, QSplitter, QTableWidget, QTextEdit
from PyQt5.QtSql import QSqlDatabase
from xQuery import XQuery

from types import SimpleNamespace

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Консоль запросов')
        self.db = QSqlDatabase.addDatabase('QSQLITE')
        self.db.setDatabaseName('task.db')
        self.db.open()

        self.query = XQuery()

        self.ui = SimpleNamespace()
        self.ui.layout = QVBoxLayout()
        l = self.ui.layout
        self.ui.button = QPushButton('Конструктор')
        self.ui.button.clicked.connect(self.query.openQueryConstructor)
        self.ui.textQuery = QTextEdit()

        l.addWidget(self.ui.button)
        l.addWidget(self.ui.textQuery)
        self.setLayout(l)
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       