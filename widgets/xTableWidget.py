import typing

from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QTableWidget, QAbstractItemView, QShortcut, QTableWidgetItem, QWidget
from PyQt5.QtGui import QDrag
from PyQt5.QtCore import QMimeData, pyqtSignal, Qt
import queryConstrucorForm.queryConstructor as qc
from typing import Union

class XTableWidget(QTableWidget):
    dropped = pyqtSignal(object)
    mouseRightButtonPressed = pyqtSignal(object)
    mouseDoubleClicked = pyqtSignal(object)
    mouseMiddleButtonPressed = pyqtSignal(object)
    mouseLeftButtonPressed = pyqtSignal(object)
    delete = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.setDragDropMode(QAbstractItemView.DragDrop)
        self.fieldForDraging = ''

        # self.objects = list()


    def dragEnterEvent(self, event) -> None:
        event.accept()

    def startDrag(self, supportedActions) -> None:
        drag = QDrag(self)
        data = QMimeData()
        if self.fieldForDraging != '':
            data.setText(getattr(self.currentItem(), self.fieldForDraging))
        else:
            data.setText(qc.QueryConstructor.getAddressInStorage(self.currentItem()._object))
        drag.setMimeData(data)
        drag.exec_()

    def dragMoveEvent(self, event: QtGui.QDragMoveEvent) -> None:
        event.accept()

    def dropEvent(self, event: QtGui.QDropEvent) -> None:
        _object = qc.QueryConstructor.getObjectFromStorage(event.mimeData().text())
        if _object != None:
            self.dropped.emit(_object)

    def addString(self, string: Union[list, tuple]) -> None:
        """Добавляем строчку в таблицу"""
        lastRow = self.rowCount()+1
        self.setRowCount(lastRow)

        for column, item in enumerate(string):

            if type(item) == QTableWidgetItem:
                self.setItem(lastRow-1, column, item)
                # self.objects.append(item._object)
            else:
                self.setCellWidget(lastRow-1, column, item)

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        currentItem = self.currentItem()
        if currentItem == None:
            return
        button = event.button()
        if button == Qt.RightButton:
            self.mouseRightButtonPressed.emit(currentItem._object)
            print('mouseRightButtonPressed')
        elif button == Qt.MiddleButton:
            self.mouseMiddleButtonPressed.emit(currentItem._object)
            print('mouseMiddleButtonPressed')
        else:
            self.mouseLeftButtonPressed.emit(currentItem._object)
            print('mouseLeftButtonPressed')
            super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, e: QtGui.QMouseEvent) -> None:
        currentItem = self.currentItem()
        if currentItem == None:
            return
        self.mouseDoubleClicked.emit(currentItem._object)

    def deleteObject(self) -> None:
        """NoDocumentation"""
        print('deleteObject')
        currentItem = self.currentItem()
        if currentItem == None:
            return
        self.delete.emit(currentItem._object)


    def deleteString(self, _object) -> None:
        """NoDocumentation"""
        index = self.objects.index(_object)
        self.objects.pop(index)
        self.removeRow(index)

    def clone(self) -> "XTableWidget":
        """NoDocumentation"""
        res = XTableWidget()
        res.setRowCount(self.rowCount())
        res.setColumnCount(self.columnCount())

        for row in range(self.rowCount()):
            for column in range(self.columnCount()):
                item = self.item(row, column)
                newItem = item.clone()
                newItem._object = item._object
                res.setItem(row, column, newItem)

        return res



