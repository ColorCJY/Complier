from PyQt5.QtWidgets import QWidget, QHBoxLayout, QTableWidget, QAbstractItemView, QTableWidgetItem
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon


class Mid_code_UI(QWidget):
    def __init__(self):
        super().__init__()
        self.tableWidget = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle('中间代码')
        self.resize(820, 640)
        self.setWindowIcon(QIcon('./Img/logo.png'))
        layout = QHBoxLayout()
        # 表格对象
        self.tableWidget = QTableWidget()

        self.tableWidget.verticalHeader().setVisible(False)
        # # 设置表格字段
        self.tableWidget.setHorizontalHeaderLabels(['id', 'op', 'op_num1', 'op_num2', 'result'])

        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        layout.addWidget(self.tableWidget)
        self.tableWidget.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

    def set_code(self, code):
        self.tableWidget.setRowCount(len(code))
        self.tableWidget.setColumnCount(5)
        for i in range(len(code)):
            new_item = QTableWidgetItem(str(i))
            new_item.setTextAlignment(Qt.AlignCenter | Qt.AlignBottom)
            self.tableWidget.setItem(i, 0, new_item)
            new_item = QTableWidgetItem(str(code[i][0]))
            new_item.setTextAlignment(Qt.AlignCenter | Qt.AlignBottom)
            self.tableWidget.setItem(i, 1, new_item)
            new_item = QTableWidgetItem(str(code[i][1]))
            new_item.setTextAlignment(Qt.AlignCenter | Qt.AlignBottom)
            self.tableWidget.setItem(i, 2, new_item)
            new_item = QTableWidgetItem(str(code[i][2]))
            new_item.setTextAlignment(Qt.AlignCenter | Qt.AlignBottom)
            self.tableWidget.setItem(i, 3, new_item)
            new_item = QTableWidgetItem(str(code[i][3]))
            new_item.setTextAlignment(Qt.AlignCenter | Qt.AlignBottom)
            self.tableWidget.setItem(i, 4, new_item)
