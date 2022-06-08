# 没有实现消除左递归,仅测试了部分文法，个别文法可能测试不成功

# 由于 pyqt5 控件 适应窗口大小改变，会发生改变，因此初始运行弹出界面时，栈分析表部分没有全部漏出来得放大窗口

from PyQt5 import QtCore, QtGui, QtWidgets

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMessageBox

FIRST = {}  # first集

FOLLOW = {}  # follow 集

VT = []  # 终结符

VC = []  # 非终结符

STACK = ['#']  # 输入栈

STACK_INPUT = []  # 剩余输入串

# # 构建二维字典（类似于矩阵，可以像矩阵一样访问）存储分析表
# SELECT = {"": {"": ""}}

sentences = []


# 界面UI类
class LL1_UI(object):
    def __init__(self):
        self.SELECT = ''
    # 初始化界面
    def setupUi(self, Form):
        self.Form = Form
        Form.setWindowIcon(QIcon('./Img/logo.png'))
        Form.setObjectName("Form")
        Form.resize(1033, 837)
        self.gridLayout = QtWidgets.QGridLayout(Form)
        self.gridLayout.setObjectName("gridLayout")
        self.textEdit = QtWidgets.QTextEdit(Form)
        self.textEdit.setGeometry(QtCore.QRect(510, 0, 521, 191))

        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(28)
        font.setItalic(True)
        self.textEdit.setFont(font)
        self.textEdit.setObjectName("textEdit")

        self.gridLayout.addWidget(self.textEdit, 0, 2, 1, 1)

        self.pushButton = QtWidgets.QPushButton(Form)
        self.pushButton.setEnabled(True)
        self.pushButton.setGeometry(QtCore.QRect(510, 190, 521, 51))
        font = QtGui.QFont()
        font.setFamily("仿宋")
        font.setPointSize(18)
        font.setBold(False)
        font.setItalic(False)
        font.setUnderline(False)
        font.setWeight(50)
        self.pushButton.setFont(font)
        self.pushButton.setObjectName("pushButton")

        self.gridLayout.addWidget(self.pushButton, 1, 2, 1, 1)

        self.lineEdit = QtWidgets.QLineEdit(Form)
        self.lineEdit.setGeometry(QtCore.QRect(0, 790, 1031, 44))
        self.lineEdit.setReadOnly(True)
        self.lineEdit.setObjectName("lineEdit")

        self.gridLayout.addWidget(self.lineEdit, 4, 0, 1, 3)

        self.tableStack = QtWidgets.QTableWidget(Form)
        self.tableStack.setGeometry(QtCore.QRect(510, 240, 521, 550))
        self.tableStack.setObjectName("tableStack")

        self.gridLayout.addWidget(self.tableStack, 2, 2, 2, 1)

        self.tableStack.setColumnCount(4)

        # 设置tablewidget 栈分析表的表头
        self.tableStack.setHorizontalHeaderLabels(["输入栈", "剩余输入串", "所用表达式", "动作"])

        self.textEdit_2 = QtWidgets.QTextEdit(Form)
        self.textEdit_2.setGeometry(QtCore.QRect(0, 0, 511, 191))
        font = QtGui.QFont()
        font.setPointSize(7)
        self.textEdit_2.setFont(font)
        self.textEdit_2.setObjectName("textEdit_2")

        self.gridLayout.addWidget(self.textEdit_2, 0, 0, 1, 2)

        self.textFirst_set = QtWidgets.QTextBrowser(Form)
        self.textFirst_set.setGeometry(QtCore.QRect(0, 240, 256, 192))
        font = QtGui.QFont()
        font.setPointSize(13)
        self.textFirst_set.setFont(font)
        self.textFirst_set.setObjectName("textFirst_set")

        self.gridLayout.addWidget(self.textFirst_set, 2, 0, 1, 1)

        self.textFollow_set = QtWidgets.QTextBrowser(Form)
        self.textFollow_set.setGeometry(QtCore.QRect(255, 240, 256, 192))
        font = QtGui.QFont()
        font.setPointSize(13)
        self.textFollow_set.setFont(font)
        self.textFollow_set.setObjectName("textFollow_set")

        self.gridLayout.addWidget(self.textFollow_set, 2, 1, 1, 1)

        self.pushButton_2 = QtWidgets.QPushButton(Form)
        self.pushButton_2.setEnabled(True)
        self.pushButton_2.setGeometry(QtCore.QRect(0, 190, 511, 51))
        font = QtGui.QFont()
        font.setFamily("仿宋")
        font.setPointSize(18)
        font.setBold(False)
        font.setItalic(False)
        font.setUnderline(False)
        font.setWeight(50)
        self.pushButton_2.setFont(font)
        self.pushButton_2.setObjectName("pushButton_2")

        self.gridLayout.addWidget(self.pushButton_2, 1, 0, 1, 2)

        self.tableAnalyze = QtWidgets.QTableWidget(Form)
        self.tableAnalyze.setGeometry(QtCore.QRect(0, 430, 511, 361))
        self.tableAnalyze.setObjectName("tableAnalyze")

        self.gridLayout.addWidget(self.tableAnalyze, 3, 0, 1, 2)

        # 隐藏分析表的横纵表头
        self.tableAnalyze.verticalHeader().setVisible(False)  # 隐藏垂直表头
        self.tableAnalyze.horizontalHeader().setVisible(False)  # 隐藏水平表头

        # self.tableAnalyze.setColumnCount(0)
        # self.tableAnalyze.setRowCount(0)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

        # 设置响应槽（信号源 conect 槽）
        self.pushButton.clicked.connect(self.onClick_analyze_stack)
        self.pushButton_2.clicked.connect(self.onClick_create_first_follow_analyze_set)

    # 按下分析栈键 生成栈分析表
    def onClick_analyze_stack(self):
        STACK = ['#']
        STACK_INPUT.clear()
        self.tableStack.clear()
        try:
            # 获取输入串并加入‘#’结束标志
            layer_stack = 1
            # 先设置 table层数为1 后 动态增加
            self.tableStack.setRowCount(layer_stack)
            # 获取 输入串 输入框中的句子 并且保存在 STACK_INPUT 列表中
            for word in self.textEdit.toPlainText():
                STACK_INPUT.append(word)
            # 输入串列表尾端插入‘#’ 代表句子结束
            STACK_INPUT.append('#')
            # 输入栈初始化含 ‘E’
            STACK.append('E')

            # 打印分析栈表 的第一行 ，初始化的默认行
            # 打印输入串
            str_w = ''
            for word in STACK_INPUT:
                str_w += word
            item1 = QtWidgets.QTableWidgetItem(str_w)
            self.tableStack.setItem(0, 1, item1)
            str_w = ''
            # 打印输入栈
            for word in STACK:
                str_w += word
            item1 = QtWidgets.QTableWidgetItem(str_w)
            # 动作 初始化
            self.tableStack.setItem(0, 0, item1)
            item1 = QtWidgets.QTableWidgetItem("初始化")
            self.tableStack.setItem(0, 3, item1)

            # 后续LL(1)文法分析栈表的实现 分两个部分①输入串顶不为‘#’（还没到输入串结束符） ②输入串为‘#’（到输入串结束符）
            while STACK_INPUT[0] != '#':
                # 层数增加一层
                layer_stack = layer_stack + 1
                self.tableStack.setRowCount(layer_stack)

                # 如果符号栈的栈顶为大写字符（即非终结符）则执行下面的操作 符号出栈入栈 并打印相关表信息
                if STACK[-1].isupper():

                    # 获得预测分析表中，的数据，利用 M[S][VT]矩阵调用操作类型
                    str = self.SELECT[STACK[-1]][STACK_INPUT[0]].split("->")[1]
                    item1 = QtWidgets.QTableWidgetItem(self.SELECT[STACK[-1]][STACK_INPUT[0]])
                    self.tableStack.setItem(layer_stack - 1, 2, item1)
                    # print(SELECT[STACK[-1]][STACK_INPUT[0]])

                    # 如果 符号栈顶的动作不是是 S -> ε 则符号栈 出栈 入栈（逆序）
                    if str != 'ε':
                        ##逆置
                        STACK.remove(STACK[-1])
                        for word in str[::-1]:
                            STACK.append(word)
                        # print(STACK)
                        # 在表中显示动作
                        item1 = QtWidgets.QTableWidgetItem("POP,PUSH(" + str + ")")
                        self.tableStack.setItem(layer_stack - 1, 3, item1)

                    # 如果 符号栈顶的动作是 S -> ε 则符号栈 则直接出栈
                    else:
                        STACK.remove(STACK[-1])
                        # 在表中显示动作
                        item1 = QtWidgets.QTableWidgetItem("POP")
                        self.tableStack.setItem(layer_stack - 1, 3, item1)

                    # 在表中显示符号栈，剩余输入串
                    str_w = ''
                    for word in STACK:
                        str_w += word
                    item1 = QtWidgets.QTableWidgetItem(str_w)
                    self.tableStack.setItem(layer_stack - 1, 0, item1)
                    str_w = ''
                    for word in STACK_INPUT:
                        str_w += word
                    item1 = QtWidgets.QTableWidgetItem(str_w)
                    self.tableStack.setItem(layer_stack - 1, 1, item1)
                # 如果符号栈栈顶是 终结符（非大写） ，则比较符号栈栈顶 和 剩余输入串的第一个元素是否相同相同则都出栈
                else:
                    if STACK[-1] == STACK_INPUT[0]:
                        STACK.remove(STACK[-1])
                        STACK_INPUT.remove(STACK_INPUT[0])
                        # print(STACK)

                        # 显示 信息
                        str_w = ''
                        for word in STACK:
                            str_w += word
                        item1 = QtWidgets.QTableWidgetItem(str_w)
                        self.tableStack.setItem(layer_stack - 1, 0, item1)
                        str_w = ''
                        for word in STACK_INPUT:
                            str_w += word
                        item1 = QtWidgets.QTableWidgetItem(str_w)
                        self.tableStack.setItem(layer_stack - 1, 1, item1)

                        item1 = QtWidgets.QTableWidgetItem("GETNEXT(i)")
                        self.tableStack.setItem(layer_stack - 1, 3, item1)
            #  剩余输入串已经到‘# ’
            while STACK[-1] != '#':
                layer_stack = layer_stack + 1
                self.tableStack.setRowCount(layer_stack)
                # 如果分析表中的动作是 S->ε 则 打印 该表达式
                if self.SELECT[STACK[-1]][STACK_INPUT[0]][-1] == 'ε':
                    item1 = QtWidgets.QTableWidgetItem(self.SELECT[STACK[-1]][STACK_INPUT[0]])
                    self.tableStack.setItem(layer_stack - 1, 2, item1)
                STACK.remove(STACK[-1])
                # print(STACK)
                # 显示信息
                str_w = ''
                for word in STACK:
                    str_w += word
                item1 = QtWidgets.QTableWidgetItem(str_w)
                self.tableStack.setItem(layer_stack - 1, 0, item1)
                str_w = ''
                for word in STACK_INPUT:
                    str_w += word
                item1 = QtWidgets.QTableWidgetItem(str_w)
                self.tableStack.setItem(layer_stack - 1, 1, item1)

                item1 = QtWidgets.QTableWidgetItem("POP")
                self.tableStack.setItem(layer_stack - 1, 3, item1)
                print(1)
        except:
            t = '分析字符串输入错误！'
            QMessageBox.warning(self.Form, '提示', t)
        print("按下分析栈键")

    # 按下生成各类几个集合,first,follow,analyze set
    def onClick_create_first_follow_analyze_set(self):
        self.textFirst_set.clear()
        self.textFollow_set.clear()
        self.tableAnalyze.clear()
        self.tableStack.clear()
        print("按下生成各类几个键,first,follow,analyze set")
        try:
            sentences.clear()
            # 获得所输入框输入的文法
            for sentence in self.textEdit_2.toPlainText().split():
                # 将每行的含有‘|’ 的句型分成两句，获取文法，并储存在sentence
                if len(sentence.split('|')) < 2:
                    sentences.append(sentence)
                else:
                    part_head = sentence.split('|')[0]
                    sentences.append(part_head)
                    part_foot = sentence.split('|')[1]
                    sentences.append(part_head[0] + "->" + part_foot)
            # 初始化 First Follow 集合
            initail()
            # 获取First 集合
            getFirst()
            getFisrt_3()
            getFisrt_3()
            # print(  FIRST )
            # 获取Follow 集合
            getFOLLOW_3()
            getFOLLOW_3()
            ## 获取 终结符 非终结符
            getVT_VC()
            ## 获取 预测分析表
            SELECT = getSelect()
            self.SELECT = SELECT

            # 界面显示 first集
            for i, j in FIRST.items():
                str = j[0]
                for temp in j[1:]:
                    str = str + ',' + temp
                self.textFirst_set.setText(
                    "FIRST(" + i + ")" + " = {" + str + "}" + "\n" + self.textFirst_set.toPlainText())
            # 界面显示follow 集合
            for i, j in FOLLOW.items():
                str = j[0]
                for temp in j[1:]:
                    str = str + ',' + temp
                self.textFollow_set.setText(
                    "FOLLOW(" + i + ")" + " = {" + str + "}""\n" + self.textFollow_set.toPlainText())
            ## 设置预测分析表的列数 len(VT)+2 终结符的数量加2,2 为第一列非终结符占一列，最后#占一列
            self.tableAnalyze.setColumnCount(len(VT) + 2)
            layer_analyze = 1
            ## 设置预测分析表的层数
            self.tableAnalyze.setRowCount(layer_analyze)
            VT_1 = VT[:]
            VT_1.append('#')

            for size in range(len(VT_1)):
                self.tableAnalyze.setColumnWidth(size, 70)
                item1 = QtWidgets.QTableWidgetItem(VT_1[size])
                self.tableAnalyze.setItem(0, size + 1, item1)

            for i in range(len(VC)):
                # 没遍历一次增加一层
                layer_analyze = layer_analyze + 1
                self.tableAnalyze.setRowCount(layer_analyze)
                # 界面显示 预测分析表
                # 显示预测分析表的第一列 非终结符
                item1 = QtWidgets.QTableWidgetItem(VC[i])
                self.tableAnalyze.setItem(i + 1, 0, item1)
                # 显示预测分析表的每一行 动作
                for size in range(len(VT_1)):
                    if (VT_1[size] in SELECT[VC[i]]):
                        item1 = QtWidgets.QTableWidgetItem(SELECT[VC[i]][VT_1[size]])
                        self.tableAnalyze.setItem(i + 1, size + 1, item1)
                #
                # item1 = QtWidgets.QTableWidgetItem(VT_1[size])
                # self.tableAnalyze.setItem(0, size, item1)
        except:
            t = '文法输入错误！'
            QMessageBox.warning(self.Form, '提示', t)

    # 部分 界面 初始化数据
    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "LL1(1)文法"))
        self.textEdit.setHtml(_translate("Form",
                                         "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
                                         "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
                                         "p, li { white-space: pre-wrap; }\n"
                                         "</style></head><body style=\" font-family:\'Arial\'; font-size:28pt; font-weight:400; font-style:italic;\">\n"
                                         "<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p></body></html>"))
        self.pushButton.setText(_translate("Form", "一键分析"))
        self.textEdit_2.setHtml(_translate("Form",
                                           "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
                                           "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
                                           "p, li { white-space: pre-wrap; }\n"
                                           "</style></head><body style=\" font-family:\'SimSun\'; font-size:7pt; font-weight:400; font-style:normal;\">\n"
                                           "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">E-&gt;TG</span></p>\n"
                                           "<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">G-&gt;+TG|</span><span style=\" font-family:\'宋体\'; font-size:8pt;\">—</span><span style=\" font-size:8pt;\">TG </span></p>\n"
                                           "<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">G-&gt;</span><span style=\" font-family:\'宋体\'; font-size:8pt;\">ε</span><span style=\" font-size:8pt;\"> </span></p>\n"
                                           "<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">T-&gt;FS</span></p>\n"
                                           "<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">S-&gt;*FS|/FS</span></p>\n"
                                           "<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">S-&gt;</span><span style=\" font-family:\'宋体\'; font-size:8pt;\">ε</span><span style=\" font-size:8pt;\"> </span></p>\n"
                                           "<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">F-&gt;(E)</span></p>\n"
                                           "<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Times New Roman\'; font-size:8pt;\">F-&gt;i </span></p></body></html>"))
        self.textFirst_set.setHtml(_translate("Form",
                                              "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
                                              "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
                                              "p, li { white-space: pre-wrap; }\n"
                                              "</style></head><body style=\" font-family:\'SimSun\'; font-size:15pt; font-weight:400; font-style:normal;\">\n"
                                              "<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p></body></html>"))
        self.pushButton_2.setText(_translate("Form", "一键生成"))


# 初始化 first 集 和follow集合字典的键值对中的 值 为空
def initail():
    FIRST.clear()
    FOLLOW.clear()
    for str in sentences:
        part_begin = str.split("->")[0]
        part_end = str.split("->")[1]
        FIRST[part_begin] = ""
        FOLLOW[part_begin] = "#"


###求first集 中第第一部分针对 ->  直接推出第一个字符为终结符 部分
def getFirst():
    for str in sentences:
        part_begin = str.split("->")[0]
        part_end = str.split("->")[1]
        if not part_end[0].isupper():
            FIRST[part_begin] = FIRST.get(part_begin) + part_end[0]


# 求first第二部分 针对 A -> B型  把B的first集加到A 的first集合中
def getFirst_2():
    for str in sentences:
        part_begin = ''
        part_end = ''
        part_begin += str.split('->')[0]
        part_end += str.split('->')[1]
        # 如果型如A ->B 则把B的first集加到A 的first集中去
        if part_end[0].isupper():
            FIRST[part_begin] = FIRST.get(part_begin) + FIRST.get(part_end[0])


# 求first第三部分，不断调用前面的求first集的方法使，得first不在增加为止
def getFisrt_3():
    while (1):
        test = FIRST
        getFirst_2()
        # 去除重复项
        for i, j in FIRST.items():
            temp = ""
            for word in list(set(j)):
                temp += word
            FIRST[i] = temp
        if test == FIRST:
            break


# 计算follow集的第一部分，先计算 S -> A b 类型的
def getFollow():
    for str in sentences:
        part_begin = str.split("->")[0]
        part_end = str.split("->")[1]
        ##如果是 S->a 直接推出终结符 则 continue
        if len(part_end) == 1:
            continue
        ##否则执行下面的操作
        else:
            # 将->后面的分开再倒序
            temp = []
            for i in part_end:
                temp.append(i)
            temp.reverse()
            # 如果非终结符在句型的末端则把"#" 加入进去
            if temp[0].isupper():
                FOLLOW[temp[0]] = FOLLOW.get(temp[0]) + FOLLOW.get(part_begin)
                temp1 = temp[0]
                for i in temp[1:]:
                    if not i.isupper():
                        temp1 = i
                    else:
                        if temp1.isupper():
                            FOLLOW[i] = FOLLOW.get(i) + FIRST.get(temp1).replace("ε", "")
                        if ('ε' in FIRST.get(temp1)):
                            FOLLOW[i] = FOLLOW.get(i) + FOLLOW.get(part_begin)
                        else:
                            FOLLOW[i] = FOLLOW.get(i) + temp1
                        temp1 = i
            # 如果终结符在句型的末端
            else:
                temp1 = temp[0]
                for i in temp[1:]:
                    if not i.isupper():
                        temp1 = i
                    else:
                        if temp1.isupper():
                            FOLLOW[i] = FOLLOW.get(i) + FIRST.get(temp1)
                        else:
                            FOLLOW[i] = FOLLOW.get(i) + temp1
                        temp1 = i


def getFOLLOW_3():
    while (1):
        test = FOLLOW
        getFollow()
        # 去除重复项
        for i, j in FOLLOW.items():
            temp = ""
            for word in list(set(j)):
                temp += word
            FOLLOW[i] = temp
        if test == FOLLOW:
            break


# 获得终结符
def getVT_VC():
    VT.clear()
    VC.clear()
    temp = []
    for sentence in sentences:
        for word in sentence:
            if not word.isupper():
                temp.append(word)
    for i in temp:
        if not i in VT:
            VT.append(i)
    VT.remove('ε')
    ##求 非终结符
    VT.sort()
    temp = []
    for sentence in sentences:
        temp.append(sentence[0])
    for i in temp:
        if not i in VC:
            VC.append(i)
    VC.sort()


##获得文法预测分析表 利用select = first（s) 如果 first集中包含空字 'ε'  则select = first + follow

##二维字典添加 键值函数

##构建预测分析表
# 二维字典，插入（新建）数据函数
def addDict_2D(thedict, key_a, key_b, val):
    if key_a in thedict:
        thedict[key_a].update({key_b: val})
    else:
        thedict.update({key_a: {key_b: val}})


# 获得分析表
def getSelect():  # 如果first（s)中有空字的 在矩阵 M（S，follow（S)）填 S - > ε
    SELECT = {"": {"": ""}}
    for i, j in FIRST.items():
        if 'ε' in j:
            for follow in FOLLOW.get(i):
                addDict_2D(SELECT, i, follow, i + "->ε")
    for str in sentences:
        part_begin = str.split("->")[0]
        part_end = str.split("->")[1]
        ############################
        ##需要改进
        ###############################
        if not part_end[0].isupper():
            if part_end[0] != 'ε':
                addDict_2D(SELECT, part_begin, part_end[0], str)
        else:
            for i in FIRST.get(part_begin):
                addDict_2D(SELECT, part_begin, i, str)
    return SELECT

# print(VT)
# print(FIRST)
# print(VC)
# print(FOLLOW)

##打印 first集 和follow 集合
# for i ,j in FIRST.items() :
#     str = j[0]
#     for temp in j[1:]:
#         str = str+ ',' +temp
#     print("FIRST("+ i + ")" + " = {"+str+"}")
#
# for i ,j in FOLLOW.items():
#     str = j[0]
#     for temp in j[1:]:
#         str = str + ',' + temp
#     print("FOLLOW("+ i + ")" + " = {"+str+"}")


##打印 分析表
# print(FIRST)
# print(FOLLOW)
# for i in SELECT:
#     print(SELECT[i])
# #     # for j in SELECT[i]:
# #     #     print(SELECT[i][j])
