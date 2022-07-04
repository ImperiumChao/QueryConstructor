import typing

from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QTreeWidget, QAbstractItemView, QTreeWidgetItem, QShortcut
from PyQt5.QtGui import QDrag, QMouseEvent
from PyQt5.QtCore import QMimeData, pyqtSignal
from PyQt5.QtCore import Qt
import queryConstrucorForm.queryConstructor as qc

class XTreeWidget(QTreeWidget):
    # dragged = pyqtSignal(object)
    dropped = pyqtSignal(object)
    mouseRightButtonPressed = pyqtSignal(object)
    mouseDoubleClicked = pyqtSignal(object)
    mouseMiddleButtonPressed = pyqtSignal(object)
    delete = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.setDragDropMode(QAbstractItemView.DragDrop)
        self.fieldForDraging = ''

        # self.deleteshortcut = QShortcut(self)
        # self.deleteshortcut.setKey(Qt.Key_Delete)
        # self.deleteshortcut.activated.connect(self.deleteObject)

    def dragEnterEvent(self, event) -> None:
        event.accept()

    def startDrag(self, supportedActions) -> None:
        drag = QDrag(self)
        data = QMimeData()
        if self.fieldForDraging != '':
            data.setText(getattr(self.currentItem()._object, self.fieldForDraging))
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

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        currentItem = self.currentItem()
        if currentItem == None:
            super().mousePressEvent(event)
            return
        button = event.button()
        if button == Qt.RightButton:
            self.mouseRightButtonPressed.emit(currentItem._object)
        elif button == Qt.MiddleButton:
            self.mouseMiddleButtonPressed.emit(currentItem._object)
        else:
            super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, e: QtGui.QMouseEvent) -> None:
        currentItem = self.currentItem()
        if currentItem == None:
            return
        self.mouseDoubleClicked.emit(currentItem._object)


    def deleteBranch(self, _object) -> None:
        """NoDocumentation"""

        for index in range(self.topLevelItemCount()):
            item = self.topLevelItem(index)
            if item._object == _object:
                self.invisibleRootItem().removeChild(item)
                break

    def clone(self) -> "XTreeWidget":
        """NoDocumentation"""
        res = XTreeWidget()
        for index in range(self.topLevelItemCount()):
            item = self.topLevelItem(index)
            newItem = QTreeWidgetItem()
            newItem.setText(0, item.text(0))
            newItem._object = item._object
            for index in range(item.childCount()):
                child = item.child(index)
                itemChield = QTreeWidgetItem()
                itemChield.setText(0, child.text(0))
                itemChield._object = child._object
                newItem.addChild(itemChield)

            res.addTopLevelItem(newItem)

        return res






