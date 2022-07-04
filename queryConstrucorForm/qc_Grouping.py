from PyQt5.QtWidgets import QWidget, QSplitter, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTreeWidget, \
    QCheckBox, QLabel, QSizePolicy, QTableWidgetItem, QComboBox, QLineEdit, QShortcut
from PyQt5.QtCore import Qt
from widgets.xTableWidget import XTableWidget
from PyQt5 import QtCore


class GroupingWidget(QWidget):
    def __init__(self, query):
        super().__init__()
        self.query = query
        self.query.changedFieldsQuery.connect(self.updateGroupingData)
        self.query.changedGroupingData.connect(self.updateGroupingData)

        self.deleteshortcut = QShortcut(self)
        self.deleteshortcut.setKey(Qt.Key_Delete)
        self.deleteshortcut.activated.connect(self.deleteObject)

        self.setLayout(QVBoxLayout())


        w = QWidget()
        w.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        w.setLayout(QHBoxLayout())
        w.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().addWidget(w)
        self.checkBoxGrouping = QCheckBox()
        self.checkBoxGrouping.stateChanged.connect(lambda state: self.query.setGroupingEnabled(bool(state)))
        w.layout().addWidget(self.checkBoxGrouping)
        w.layout().addWidget(QLabel('Группировка'))

        self.splitter = QSplitter()
        self.layout().addWidget(self.splitter)
        self.layout().addWidget(self.splitter)

        self.selectedFieldsForGrouping = XTableWidget()
        self.selectedFieldsForGrouping.setColumnCount(1)
        self.selectedFieldsForGrouping.verticalHeader().hide()
        self.selectedFieldsForGrouping.horizontalHeader().setStretchLastSection(True)
        self.selectedFieldsForGrouping.setHorizontalHeaderLabels(('Доступные поля',))
        self.splitter.addWidget(self.selectedFieldsForGrouping)

        self.aggregatedField = XTableWidget()
        self.aggregatedField.setColumnCount(2)
        self.aggregatedField.verticalHeader().hide()
        self.aggregatedField.horizontalHeader().setStretchLastSection(True)
        self.aggregatedField.setHorizontalHeaderLabels(('Поле', 'Функция агрегирования'))
        self.aggregatedField.dropped.connect(self.addedAggregatedFields)
        self.splitter.addWidget(self.aggregatedField)

    def deleteObject(self) -> None:
        """NoDocumentation"""
        if self.aggregatedField.hasFocus():
            currentItem = self.aggregatedField.currentItem()
            if currentItem == None:
                return
            expression = currentItem._object
            self.query.deleteAggregationField(expression)

    def updateGroupingData(self) -> None:
        """NoDocumentation"""
        self.checkBoxGrouping.setChecked(self.query.usingGrouping)

        self.selectedFieldsForGrouping.clear()
        self.selectedFieldsForGrouping.setColumnCount(1)
        self.selectedFieldsForGrouping.setHorizontalHeaderLabels(('Доступные поля',))
        self.selectedFieldsForGrouping.setRowCount(0)

        self.aggregatedField.clear()
        self.aggregatedField.setColumnCount(2)
        self.aggregatedField.setRowCount(0)
        self.aggregatedField.setHorizontalHeaderLabels(('Поле', 'Функция агрегирования'))
        for expression in self.query.fields:
            if not expression.hasAggregation:
                item = QTableWidgetItem()
                item._object = expression
                item.setText(expression.rawSqlText)
                # self.expressions[expression] = item
                self.selectedFieldsForGrouping.addString([item])
            else:
                itemField = QTableWidgetItem()
                itemField._object = expression
                itemField.setText(expression.rawSqlTextWithoutAgg)

                self.aggregatedField.addString((itemField, self.getComboBoxAggregationFunction(expression)))


    def getComboBoxAggregationFunction(self, expression) -> QComboBox:
        """NoDocumentation"""
        res = QComboBox()
        res.expression = expression
        res.setLineEdit(QLineEdit())
        res.lineEdit().expression = expression
        res.lineEdit().setReadOnly(True)
        res.setStyleSheet("QComboBox { qproperty-frame: false }");
        res.setEditable(True)
        for aggregationFunction in ('SUM', 'MIN', 'MAX', 'COUNT', 'AVG'):
            res.addItem(aggregationFunction)
        res.activated.connect(self.selectedAggregationFunction)
        return res

    def selectedAggregationFunction(self) -> None:
        """NoDocumentation"""
        comboBox: QComboBox = self.sender()
        comboBox.expression.setAggregationFunction(comboBox.currentText())

    def addedAggregatedFields(self, expression) -> None:
        """NoDocumentation"""
        self.query.addAggregaredFields(expression)
