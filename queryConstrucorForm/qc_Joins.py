from PyQt5.QtWidgets import QWidget, QSplitter, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTreeWidget

class JoinsWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        self.joins = QTableWidget()
        self.layout.addWidget(self.joins)

        self.aliasesWidget = QWidget()
        self.aliasesWidget.setLayout(QVBoxLayout())
        self.layout.addWidget(self.aliasesWidget)

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
        self.layout.addWidget(self.query1Widget)

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