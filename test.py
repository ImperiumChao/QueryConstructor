import sys

from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QPushButton, QLineEdit
# from mainWindow import MainWindow

class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.w = MyWidget(self)


class MyWidget(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.deleteshortcut = QShortcut(self)
        self.deleteshortcut.setKey(Qt.Key_Delete)
        self.deleteshortcut.activated.connect(self.deleteObject)

    def deleteObject(self) -> None:
        """NoDocumentation"""
        print('deleteObjectdfg')

if __name__ == "__main__":
    app = QApplication([])

    mainWindow = Window()
    mainWindow.show()

    sys.exit(app.exec_())



