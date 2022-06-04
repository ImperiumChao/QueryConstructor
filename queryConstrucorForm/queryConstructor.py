from PyQt5.QtWidgets import QWidget, QTabWidget, QTreeWidget, QListWidget, QPushButton, QVBoxLayout, \
    QHBoxLayout, QSplitter, QTableWidget, QTextEdit, QShortcut

from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from queryConstrucorForm.qc_Conditions import ConditionsWidget
from queryConstrucorForm.qc_Grouping import GroupingWidget
from queryConstrucorForm.qc_Joins import JoinsWidget
from queryConstrucorForm.qc_Sorting import SortingWidget
from queryConstrucorForm.qc_SubQueries import SubQueriesWidget
from queryConstrucorForm.qc_TablesAndFields import TablesAndFieldsWidget
from queryConstrucorForm.qc_Unions import UnionsWidget
from queryConstrucorForm.qc_СonditionsAfterGrouping import ConditionsAfterGroupingWidget
from random import randint

class QueryConstructor(QWidget):
    dragAndDrop = dict()

    def __init__(self, xQuery):
        super().__init__()

        # self.deleteshortcut = QShortcut(self)
        # self.deleteshortcut.setKey(Qt.Key_Delete)
        # self.deleteshortcut.activated.connect(self.deleteObject)
        self.setWindowTitle('Конструктор запросов')
        self.query = xQuery
        self.joinsTablesAndFields = list()
        self.joinsUnions = list()
        self.joinsConditions = list()
        self.joinsGrouping = list()
        self.joinsConditionsAfterGrouping = list()

        self.setLayout(QVBoxLayout())
        self.tabsConstructorQuery = QTabWidget()
        self.layout().addWidget(self.tabsConstructorQuery)

        self.tabTablesAndFields = QWidget()
        self.tabTablesAndFields.setLayout(QHBoxLayout())
        self.tabsConstructorQuery.addTab(self.tabTablesAndFields, "Таблицы и поля")
        self.tabsTablesAndFieldsJoins = QTabWidget()
        self.tabsTablesAndFieldsJoins.setTabPosition(QTabWidget.East)
        self.tabTablesAndFields.layout().addWidget(self.tabsTablesAndFieldsJoins)

        self.tabUnions = QWidget()
        self.tabUnions.setLayout(QVBoxLayout())
        self.tabsConstructorQuery.addTab(self.tabUnions, "Связи")
        self.tabsUnionsJoins = QTabWidget()
        self.tabsUnionsJoins.setTabPosition(QTabWidget.East)
        self.tabUnions.layout().addWidget(self.tabsUnionsJoins)

        self.tabConditions = QWidget()
        self.tabConditions.setLayout(QVBoxLayout())
        self.tabsConstructorQuery.addTab(self.tabConditions, "Условия")
        self.tabConditionsJoins = QTabWidget()
        self.tabConditionsJoins.setTabPosition(QTabWidget.East)
        self.tabConditions.layout().addWidget(self.tabConditionsJoins)

        self.tabGrouping = QWidget()
        self.tabGrouping.setLayout(QHBoxLayout())
        self.tabsConstructorQuery.addTab(self.tabGrouping, "Группировка")
        self.tabGroupingJoins = QTabWidget()
        self.tabGroupingJoins.setTabPosition(QTabWidget.East)
        self.tabGrouping.layout().addWidget(self.tabGroupingJoins)

        self.tabConditionsAfterGrouping = QWidget()
        self.tabConditionsAfterGrouping.setLayout(QVBoxLayout())
        self.tabsConstructorQuery.addTab(self.tabConditionsAfterGrouping, "Условия после группировки")
        self.tabConditionsAfterGroupingJoins = QTabWidget()
        self.tabConditionsAfterGroupingJoins.setTabPosition(QTabWidget.East)
        self.tabConditionsAfterGrouping.layout().addWidget(self.tabConditionsAfterGroupingJoins)

        self.tabJoinsAndAliases = JoinsWidget()
        self.tabsConstructorQuery.addTab(self.tabJoinsAndAliases, "Объединения и псевдонимы")

        self.TabOrder = SortingWidget()
        self.tabsConstructorQuery.addTab(self.TabOrder, "Порядок")

        self.tabSubQueries = SubQueriesWidget()
        self.tabsConstructorQuery.addTab(self.tabSubQueries, "Подзапросы")

        self.addQuery(self.query)

    def addQuery(self, query) -> None:
        """Добавляем либо первый запрос, либо еще один на объединение"""
        widget = TablesAndFieldsWidget(query)
        self.joinsTablesAndFields.append(widget)
        self.tabsTablesAndFieldsJoins.addTab(widget, "Запрос 1")

        widget = UnionsWidget(query)
        self.joinsUnions.append(widget)
        self.tabsUnionsJoins.addTab(widget, "Запрос 1")

        widget = ConditionsWidget(query)
        self.joinsConditions.append(widget)
        self.tabConditionsJoins.addTab(widget, "Запрос 1")

        widget = GroupingWidget(query)
        self.joinsGrouping.append(widget)
        self.tabGroupingJoins.addTab(widget, "Запрос 1")

        widget = ConditionsAfterGroupingWidget(query)
        self.joinsConditionsAfterGrouping.append(widget)
        self.tabConditionsAfterGroupingJoins.addTab(widget, "Запрос 1")

    @staticmethod
    def getAddressInStorage(_object) -> str:
        """NoDocumentation"""
        address = str(randint(0, 100))
        QueryConstructor.dragAndDrop.clear()
        QueryConstructor.dragAndDrop[address] = _object
        return address

    @staticmethod
    def getObjectFromStorage(address) -> object:
        """NoDocumentation"""
        if address in QueryConstructor.dragAndDrop:
            res = QueryConstructor.dragAndDrop[address]
        else:
            res = None

        QueryConstructor.dragAndDrop.clear()
        return res

    def deleteObject(self) -> None:
        """NoDocumentation"""
        print('deleteObjectqueryConstructor.py')
