from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class assem_code_UI(QMainWindow):
    def __init__(self):
        super().__init__()

    def init_UI(self, codes):
        self.setWindowTitle('汇编代码')
        self.resize(640, 640)
        widget = QWidget()
        self.setCentralWidget(widget)
        self.setWindowIcon(QIcon('./Img/logo.png'))
        layout = QHBoxLayout()
        text = QTextBrowser()
        layout.addWidget(text)
        widget.setLayout(layout)
        text.setFont(QFont('微软雅黑', 11))
        text.setLineWrapMode(0)
        text.setText(codes)
