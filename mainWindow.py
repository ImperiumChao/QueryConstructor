from PyQt5.QtWidgets import QWidget, QTabWidget, QTreeWidget, QListWidget, QPushButton, QVBoxLayout, \
    QHBoxLayout, QSplitter, QTableWidget, QTextEdit, QTableWidgetItem, QSplitter, QDialog, QLineEdit, \
    QMessageBox
# from queryConstrucorForm.queryConstructor import QueryConstructor

from PyQt5.QtSql import QSqlDatabase, QSqlQuery
from PyQt5.QtCore import Qt
from collections import namedtuple
from xQuery import XQuery

from types import SimpleNamespace
import re
import pickle


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Консоль запросов')
        self.ColumnTable = namedtuple('ColumnTable', 'name reference')
        self.connectDB()

        self.query = XQuery()

        self.setLayout(QVBoxLayout())
        self.splitter = QSplitter()
        self.splitter.setOrientation(Qt.Vertical)
        self.layout().addWidget(self.splitter)

        self.splitter.addWidget(self.query.getQueryConstructor())
        XQuery.queryConstructor.executeQuery.connect(self.executeQuery)

        self.table = QTableWidget()
        self.splitter.addWidget(self.table)

    def connectDB(self):
        self.fillInfoDB()

        self.db = QSqlDatabase.addDatabase(self.infoDB.Type)
        self.db.setDatabaseName(self.infoDB.DatabaseName)
        if self.infoDB.Type == 'QSQLITE':
            self.db.open()
            if len(self.infoDB.Tables) == 0:
                self.findTablesSQLITE()
                self.whiteInfoDBToFile()

            XQuery.updateTablesDB(self.infoDB.Tables)
            self.query.changedAvailableTables.emit()
            self.show()
        else:
            self.db.setHostName(self.infoDB.Host)
            self.db.setUserName(self.infoDB.UserName)

            self.setPasswordWidget = QDialog(self)
            self.setPasswordWidget.setWindowTitle('Введите пароль')
            self.setPasswordWidget.setLayout(QVBoxLayout())
            self.setPasswordWidget.lineEdit = QLineEdit()
            self.setPasswordWidget.lineEdit.setEchoMode(QLineEdit.Password)
            self.setPasswordWidget.layout().addWidget(self.setPasswordWidget.lineEdit)
            self.setPasswordWidget.lineEdit.returnPressed.connect(self.connectDBWithPassword)
            self.setPasswordWidget.show()

    def whiteInfoDBToFile(self):
        strings = []
        for title in ['Type', 'Host', 'DatabaseName', 'UserName']:
            value = getattr(self.infoDB, title)
            if value != None:
                strings.append(f'{title}: {value}')
        strings.append('')
        for name, fields in self.infoDB.Tables.items():
            strings.append('')
            strings.append(f'Table: {name}')
            for field in fields:
                if field.reference == None:
                    strings.append(field.name)
                else:
                    strings.append(f'{field.name} ({field.reference})')

        with open('db.txt', 'w') as file:
            file.write('\n'.join(strings))

    def connectDBWithPassword(self):
        self.db.setPassword(self.setPasswordWidget.lineEdit.text())
        if self.db.open():
            if len(self.infoDB.Tables) == 0 and self.infoDB.Type == 'QPSQL':
                self.findTablesPSQL()
                self.whiteInfoDBToFile()
            self.setPasswordWidget.hide()
            XQuery.updateTablesDB(self.infoDB.Tables)
            self.query.changedAvailableTables.emit()
            self.show()
        else:
            self.setPasswordWidget.lineEdit.setText('')

    def fillInfoDB(self):
        self.infoDB = SimpleNamespace()
        self.infoDB.Type = None
        self.infoDB.Host = None
        self.infoDB.DatabaseName = None
        self.infoDB.UserName = None
        self.infoDB.Tables = dict()

        sectionTables = False
        currentTable = None

        with open('db.txt', 'r') as file:

            for line in file:
                if line.strip() == '':
                    continue
                line = line.replace('\n', '')
                if ':' in line:
                    lst = [s.strip() for s in line.split(':')]
                    if lst[0] != 'Table':
                        setattr(self.infoDB, lst[0], lst[1])
                    else:
                        currentTable = lst[1]
                        self.infoDB.Tables[currentTable] = []
                elif currentTable != None:
                    if '(' in line:
                        lst = [s.strip() for s in line.split('(')]
                        self.infoDB.Tables[currentTable].append(self.ColumnTable(lst[0], lst[1].replace(')', '')))
                    else:
                        self.infoDB.Tables[currentTable].append(self.ColumnTable(line, None))

    def findTablesSQLITE(self):
        query = QSqlQuery()
        query.prepare('SELECT name, sql FROM sqlite_master WHERE type=\'table\' AND name <> \"sqlite_sequence\"')
        query.exec()

        while (query.next()):
            name = query.value('name')
            sqlText = query.value('sql')

            textInParentheses = sqlText[sqlText.find('('):sqlText.find(');')]
            textInParentheses = textInParentheses.replace('(', '')
            textInParentheses = textInParentheses.replace(')', '')
            textInParentheses = textInParentheses.replace('\"', '')
            textInParentheses = textInParentheses.replace('`', '')
            textInParentheses = textInParentheses.replace('\t', ' ')
            textInParentheses = textInParentheses.replace('\n', ' ')
            textInParentheses = textInParentheses.strip()

            for i in range(10):
                textInParentheses = textInParentheses.replace('  ', ' ')

            descriptionFields = textInParentheses.split(',')
            fields = list()

            for sqlField in descriptionFields:
                sqlField = sqlField.strip()
                if sqlField.find('FOREIGN KEY') == -1:
                    fields.append(self.ColumnTable(sqlField[0:sqlField.find(' ')], None))
            self.infoDB.Tables[name] = fields

    def findTablesPSQL(self):
        query = QSqlQuery()
        query.prepare(
            '''SELECT 
                columns.ordinal_position AS ordinal_position,
                columns.table_name AS table_name,
                columns.column_name AS column_name,
                pg_get_constraintdef(pg_constraint.oid) AS reference
            FROM
                information_schema.columns AS columns
                LEFT JOIN information_schema.key_column_usage AS key_column_usage
                    INNER JOIN pg_constraint AS pg_constraint
                    ON key_column_usage.constraint_name = pg_constraint.conname
                        AND pg_constraint.contype = 'f'
                ON columns.table_name=key_column_usage.table_name
                    AND columns.column_name = key_column_usage.column_name
                WHERE
                    NOT columns.table_schema IN('pg_catalog', 'information_schema')
                ORDER BY
                    table_name ,
                    ordinal_position''')
        query.exec()
        patternFK = 'KEY \(([\w, ]+)\)'
        patternTableRef = 'REFERENCES (\w+)\([\w, ]+\)'
        patternRef = 'REFERENCES \w+\(([\w, ]+)\)'

        while (query.next()):
            table_name = query.value('table_name')
            column_name = query.value('column_name')
            reference = str(query.value('reference'))

            if reference != '':
                columnsFK = re.search(patternFK, reference).group(1).split(', ')
                tableRef = re.search(patternTableRef, reference).group(1)
                columnsRef = re.search(patternRef, reference).group(1).split(', ')

                columnRef = columnsRef[columnsFK.index(column_name)]

            if self.infoDB.Tables.get(table_name) == None:
                self.infoDB.Tables[table_name] = []

            if reference == '':
                self.infoDB.Tables[table_name].append(self.ColumnTable(column_name, None))
            else:
                self.infoDB.Tables[table_name].append(self.ColumnTable(column_name, f'{tableRef}.{columnRef}'))

    def executeQuery(self):
        query = QSqlQuery()
        query.prepare(XQuery.mainQuery.textQuery)
        for param, value in XQuery.mainQuery.parameters.items():
            if value != None:
                query.bindValue(param, value)
        if not query.exec():
            QMessageBox.warning(self, 'Ошибка запроса', query.lastError().text())

        self.table.clear()
        self.table.setColumnCount(len(XQuery.mainQuery.fields))
        self.table.setHorizontalHeaderLabels([field.alias for field in XQuery.mainQuery.fields])
        self.table.horizontalHeader().setStretchLastSection(True)

        rowCount = 0
        while query.next():
            rowCount += 1

        self.table.setRowCount(rowCount)
        query.seek(-1)
        currentRow = 0
        while query.next():
            for currentColumn, field in enumerate(XQuery.mainQuery.fields):
                itm = QTableWidgetItem()
                itm.setText(str(query.value(field.alias)))
                itm.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                self.table.setItem(currentRow, currentColumn, itm)
            currentRow += 1
