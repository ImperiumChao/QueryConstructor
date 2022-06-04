from PyQt5.QtWidgets import QWidget, QTabWidget, QTreeWidget, QListWidget, QPushButton, QVBoxLayout, \
    QHBoxLayout, QSplitter, QTableWidget, QTextEdit

from PyQt5 import QtCore

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        #ВСТАВКА КОДА UI
        
        self.setLayout(QVBoxLayout())
        
        self.tabsConstructorQuery = QTabWidget()
        self.layout().addWidget(self.tabsConstructorQuery)
        
        self.tabTablesAndFields = QWidget()
        self.tabTablesAndFields.setLayout(QHBoxLayout())
        self.tabsConstructorQuery.addTab(self.tabTablesAndFields, "Таблицы и поля")
        
        self.tabsTablesAndFieldsJoins = QTabWidget()
        self.tabsTablesAndFieldsJoins.setTabPosition(QTabWidget.East)
        self.tabTablesAndFields.layout().addWidget(self.tabsTablesAndFieldsJoins)
        
        self.tabTablesAndFieldsJoin1 = QWidget()
        self.tabTablesAndFieldsJoin1.setLayout(QVBoxLayout())
        self.tabsTablesAndFieldsJoins.addTab(self.tabTablesAndFieldsJoin1, "Запрос 1")
        
        self.splitterTablesAndFields = QSplitter()
        self.tabTablesAndFieldsJoin1.layout().addWidget(self.splitterTablesAndFields)
        
        self.availableTablesWidget = QWidget()
        self.availableTablesWidget.setLayout(QVBoxLayout())
        self.splitterTablesAndFields.addWidget(self.availableTablesWidget)
        
        self.availableTablesPanelWidget = QWidget()
        self.availableTablesPanelWidget.setLayout(QHBoxLayout())
        self.availableTablesWidget.layout().addWidget(self.availableTablesPanelWidget)
        
        self.addSubQuery = QPushButton()
        self.addSubQuery.setText("+")
        self.availableTablesPanelWidget.layout().addWidget(self.addSubQuery)
        
        self.availableTables = QTreeWidget()
        self.availableTablesWidget.layout().addWidget(self.availableTables)
        
        self.selectedTablesWidget = QWidget()
        self.selectedTablesWidget.setLayout(QVBoxLayout())
        self.splitterTablesAndFields.addWidget(self.selectedTablesWidget)
        
        self.selectedTablesPanelWidget = QWidget()
        self.selectedTablesPanelWidget.setLayout(QHBoxLayout())
        self.selectedTablesWidget.layout().addWidget(self.selectedTablesPanelWidget)
        
        self.replaceTable = QPushButton()
        self.replaceTable.setText("=")
        self.selectedTablesPanelWidget.layout().addWidget(self.replaceTable)
        
        self.selectedTables = QTreeWidget()
        self.selectedTablesWidget.layout().addWidget(self.selectedTables)
        
        self.selectedFieldsWidget = QWidget()
        self.selectedFieldsWidget.setLayout(QVBoxLayout())
        self.splitterTablesAndFields.addWidget(self.selectedFieldsWidget)
        
        self.selectedFieldsPanelWidget = QWidget()
        self.selectedFieldsPanelWidget.setLayout(QHBoxLayout())
        self.selectedFieldsWidget.layout().addWidget(self.selectedFieldsPanelWidget)
        
        self.addExpression = QPushButton()
        self.addExpression.setText("+")
        self.selectedFieldsPanelWidget.layout().addWidget(self.addExpression)
        
        self.selectedFields = QListWidget()
        self.selectedFieldsWidget.layout().addWidget(self.selectedFields)
        
        self.tabUnions = QWidget()
        self.tabUnions.setLayout(QVBoxLayout())
        self.tabsConstructorQuery.addTab(self.tabUnions, "Связи")
        
        self.tabsUnionsJoins = QTabWidget()
        self.tabsUnionsJoins.setTabPosition(QTabWidget.East)
        self.tabUnions.layout().addWidget(self.tabsUnionsJoins)
        
        self.tabUnionsJoin1 = QWidget()
        self.tabUnionsJoin1.setLayout(QHBoxLayout())
        self.tabsUnionsJoins.addTab(self.tabUnionsJoin1, "Запрос 1")
        
        self.splitterUnions = QSplitter()
        self.tabUnionsJoin1.layout().addWidget(self.splitterUnions)
        
        self.unionsWidget = QWidget()
        self.unionsWidget.setLayout(QVBoxLayout())
        self.splitterUnions.addWidget(self.unionsWidget)
        
        self.unionsPanelWidget = QWidget()
        self.unionsPanelWidget.setLayout(QHBoxLayout())
        self.unionsWidget.layout().addWidget(self.unionsPanelWidget)
        
        self.addUnion = QPushButton()
        self.addUnion.setText("+")
        self.unionsPanelWidget.layout().addWidget(self.addUnion)
        
        self.unions = QTableWidget()
        self.unionsWidget.layout().addWidget(self.unions)
        
        self.splitterConditionsUnions = QSplitter()
        self.splitterConditionsUnions.setOrientation(QtCore.Qt.Vertical)
        self.splitterUnions.addWidget(self.splitterConditionsUnions)
        
        self.ordinaryConditionsUnions = QTableWidget()
        self.splitterConditionsUnions.addWidget(self.ordinaryConditionsUnions)
        
        self.conditionsUnions = QTextEdit()
        self.splitterConditionsUnions.addWidget(self.conditionsUnions)
        
        self.tabConditions = QWidget()
        self.tabConditions.setLayout(QVBoxLayout())
        self.tabsConstructorQuery.addTab(self.tabConditions, "Условия")
        
        self.tabConditionsJoins = QTabWidget()
        self.tabConditionsJoins.setTabPosition(QTabWidget.East)
        self.tabConditions.layout().addWidget(self.tabConditionsJoins)
        
        self.tabConditionsJoin1 = QWidget()
        self.tabConditionsJoin1.setLayout(QHBoxLayout())
        self.tabConditionsJoins.addTab(self.tabConditionsJoin1, "Запрос 1")
        
        self.splitterConditions = QSplitter()
        self.tabConditionsJoin1.layout().addWidget(self.splitterConditions)
        
        self.fieldsForСonditions = QTreeWidget()
        self.splitterConditions.addWidget(self.fieldsForСonditions)
        
        self.conditionsWidget = QWidget()
        self.conditionsWidget.setLayout(QVBoxLayout())
        self.splitterConditions.addWidget(self.conditionsWidget)
        
        self.conditionsPanelWidget = QWidget()
        self.conditionsPanelWidget.setLayout(QHBoxLayout())
        self.conditionsWidget.layout().addWidget(self.conditionsPanelWidget)
        
        self.addCondition = QPushButton()
        self.addCondition.setText("+")
        self.conditionsPanelWidget.layout().addWidget(self.addCondition)
        
        self.conditions = QListWidget()
        self.conditionsWidget.layout().addWidget(self.conditions)
        
        self.tabGrouping = QWidget()
        self.tabGrouping.setLayout(QHBoxLayout())
        self.tabsConstructorQuery.addTab(self.tabGrouping, "Группировка")
        
        self.tabGroupingJoins = QTabWidget()
        self.tabGroupingJoins.setTabPosition(QTabWidget.East)
        self.tabGrouping.layout().addWidget(self.tabGroupingJoins)
        
        self.tabGroupingJoin1 = QWidget()
        self.tabGroupingJoin1.setLayout(QHBoxLayout())
        self.tabGroupingJoins.addTab(self.tabGroupingJoin1, "Запрос 1")
        
        self.splitterGrouping = QSplitter()
        self.tabGroupingJoin1.layout().addWidget(self.splitterGrouping)
        
        self.selectedFieldsForGrouping = QListWidget()
        self.splitterGrouping.addWidget(self.selectedFieldsForGrouping)
        
        self.splitterGroupingFields = QSplitter()
        self.splitterGroupingFields.setOrientation(QtCore.Qt.Vertical)
        self.splitterGrouping.addWidget(self.splitterGroupingFields)
        
        self.groupingFields = QListWidget()
        self.splitterGroupingFields.addWidget(self.groupingFields)
        
        self.aggregatedField = QTableWidget()
        self.splitterGroupingFields.addWidget(self.aggregatedField)
        
        self.tabConditionsAfterGrouping = QWidget()
        self.tabConditionsAfterGrouping.setLayout(QVBoxLayout())
        self.tabsConstructorQuery.addTab(self.tabConditionsAfterGrouping, "Условия после группировки")
        
        self.tabConditionsAfterGroupingJoins = QTabWidget()
        self.tabConditionsAfterGroupingJoins.setTabPosition(QTabWidget.East)
        self.tabConditionsAfterGrouping.layout().addWidget(self.tabConditionsAfterGroupingJoins)
        
        self.tabConditionsAfterGroupingJoin1 = QWidget()
        self.tabConditionsAfterGroupingJoin1.setLayout(QHBoxLayout())
        self.tabConditionsAfterGroupingJoins.addTab(self.tabConditionsAfterGroupingJoin1, "Запрос 1")
        
        self.splitterConditionsAfterGrouping = QSplitter()
        self.tabConditionsAfterGroupingJoin1.layout().addWidget(self.splitterConditionsAfterGrouping)
        
        self.fieldsForСonditionsAfterGrouping = QListWidget()
        self.splitterConditionsAfterGrouping.addWidget(self.fieldsForСonditionsAfterGrouping)
        
        self.conditionsAfterGroupingWidget = QWidget()
        self.conditionsAfterGroupingWidget.setLayout(QVBoxLayout())
        self.splitterConditionsAfterGrouping.addWidget(self.conditionsAfterGroupingWidget)
        
        self.conditionsAfterGroupingPanelWidget = QWidget()
        self.conditionsAfterGroupingPanelWidget.setLayout(QHBoxLayout())
        self.conditionsAfterGroupingWidget.layout().addWidget(self.conditionsAfterGroupingPanelWidget)
        
        self.addCondition = QPushButton()
        self.addCondition.setText("+")
        self.conditionsAfterGroupingPanelWidget.layout().addWidget(self.addCondition)
        
        self.conditions = QListWidget()
        self.conditionsAfterGroupingWidget.layout().addWidget(self.conditions)
        
        self.tabJoinsAndAliases = QWidget()
        self.tabJoinsAndAliases.setLayout(QHBoxLayout())
        self.tabsConstructorQuery.addTab(self.tabJoinsAndAliases, "Объединения и псевдонимы")
        
        self.joins = QTableWidget()
        self.tabJoinsAndAliases.layout().addWidget(self.joins)
        
        self.aliasesWidget = QWidget()
        self.aliasesWidget.setLayout(QVBoxLayout())
        self.tabJoinsAndAliases.layout().addWidget(self.aliasesWidget)
        
        self.aliasesPanelWidget = QWidget()
        self.aliasesPanelWidget.setLayout(QHBoxLayout())
        self.aliasesWidget.layout().addWidget(self.aliasesPanelWidget)
        
        self.moveAliasUp = QPushButton()
        self.moveAliasUp.setText("↑")
        self.aliasesPanelWidget.layout().addWidget(self.moveAliasUp)
        
        self.moveAliasDown = QPushButton()
        self.moveAliasDown.setText("↓")
        self.aliasesPanelWidget.layout().addWidget(self.moveAliasDown)
        
        self.aliases = QTableWidget()
        self.aliasesWidget.layout().addWidget(self.aliases)
        
        self.query1Widget = QWidget()
        self.query1Widget.setLayout(QVBoxLayout())
        self.tabJoinsAndAliases.layout().addWidget(self.query1Widget)
        
        self.query1PanelWidget = QWidget()
        self.query1PanelWidget.setLayout(QHBoxLayout())
        self.query1Widget.layout().addWidget(self.query1PanelWidget)
        
        self.moveQuery1Down = QPushButton()
        self.moveQuery1Down.setText("↓")
        self.query1PanelWidget.layout().addWidget(self.moveQuery1Down)
        
        self.moveQuery1Up = QPushButton()
        self.moveQuery1Up.setText("↑")
        self.query1PanelWidget.layout().addWidget(self.moveQuery1Up)
        
        self.query1 = QTableWidget()
        self.query1Widget.layout().addWidget(self.query1)
        
        self.TabOrder = QWidget()
        self.TabOrder.setLayout(QHBoxLayout())
        self.tabsConstructorQuery.addTab(self.TabOrder, "Порядок")
        
        self.aliasesOrderBy = QListWidget()
        self.TabOrder.layout().addWidget(self.aliasesOrderBy)
        
        self.sortingFieldsWidget = QWidget()
        self.sortingFieldsWidget.setLayout(QVBoxLayout())
        self.TabOrder.layout().addWidget(self.sortingFieldsWidget)
        
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
        
        self.tabSubQueries = QWidget()
        self.tabSubQueries.setLayout(QHBoxLayout())
        self.tabsConstructorQuery.addTab(self.tabSubQueries, "Подзапросы")
        
        self.subQueries = QTableWidget()
        self.tabSubQueries.layout().addWidget(self.subQueries)
        
        self.textSubQueriesWidget = QWidget()
        self.textSubQueriesWidget.setLayout(QVBoxLayout())
        self.tabSubQueries.layout().addWidget(self.textSubQueriesWidget)
        
        self.textSubQueriesPanelWidget = QWidget()
        self.textSubQueriesPanelWidget.setLayout(QHBoxLayout())
        self.textSubQueriesWidget.layout().addWidget(self.textSubQueriesPanelWidget)
        
        self.openQueryConstructor = QPushButton()
        self.openQueryConstructor.setText("Открыть конструктор запроса")
        self.textSubQueriesPanelWidget.layout().addWidget(self.openQueryConstructor)
        
        self.textSubQueries = QTextEdit()
        self.textSubQueriesWidget.layout().addWidget(self.textSubQueries)
        #ВСТАВКА КОДА UI
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       