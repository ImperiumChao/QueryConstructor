import sys

from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QApplication
from mainWindow import MainWindow


if __name__ == "__main__":
    app = QApplication([])

    mainWindow = MainWindow()
    mainWindow.show()

    sys.exit(app.exec_())