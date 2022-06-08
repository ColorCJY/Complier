# coding=utf-8
import chardet

from inter import inter
from Mid_code_UI import *
from assem_code_UI import *
from Word_Analysis import *
from Result_Deal import *
from Auto_lanaly import *
from NFA import *
from Grammar_Analysis import *
from Assem_Code import *
from LL1_UI import *

import threading
import sys
import os
import ctypes


class main(QMainWindow):
    def __init__(self):  # 初始化一些全局
        super().__init__()
        self.grammar = None
        self.inter = None
        self.word_analysis = None
        self.assem_code = None
        self.grammar_analysis = None
        self.text2 = QTextBrowser()  # 结果
        self.text1 = QTextBrowser()  # 错误
        self.text = QTextEdit()  # 编辑框
        self.line = QTextBrowser()  # 行数框
        self.we1 = QWidget()  # 放置行数框
        self.file_type = "Text Files (*.txt);;MyC Files (*.myc);;C Files (*.c)"  # 文件类型
        self.line_num = 1  # 文件行数
        self.sc2 = self.line.verticalScrollBar()  # 行数框滚动条
        self.sc1 = self.text.verticalScrollBar()  # 文本框滚动条
        self.s_file = ''  # 记录当前保存文件位置
        self.now_file = ''  # 记录当前文件位置
        self.token = ''  # 词法分析的符号串
        self.code = ''  # 中间代码
        self.InitUI()  # 初始化主界面
        self.mid = Mid_code_UI()  # 中间代码界面
        self.ass = assem_code_UI()  # 汇编代码界面
        self.widget = QtWidgets.QWidget()
        self.LL1_ui = LL1_UI()
        self.LL1_ui.setupUi(self.widget)

    def init_menu(self):  # 初始化菜单栏
        # 菜单栏
        menubar = self.menuBar()

        # 文件菜单
        file_menu = menubar.addMenu('文件(&F)')
        # 新建文件
        create_file = QAction('新建(&N)', self)
        create_file.setShortcut('Ctrl+N')
        create_file.setStatusTip('新建文件')
        file_menu.addAction(create_file)
        create_file.triggered.connect(lambda: self.create_file(1))
        # 加载文件
        loadfile = QAction('打开(&O)', self)
        loadfile.setShortcut('Ctrl+O')
        loadfile.setStatusTip('加载文件')
        file_menu.addAction(loadfile)
        loadfile.triggered.connect(lambda: self.open_file(1))
        # 保存文件
        save_f = QAction('保存(&S)', self)
        save_f.setShortcut('Ctrl+S')
        save_f.setStatusTip('保存文件')
        file_menu.addAction(save_f)
        save_f.triggered.connect(self.save_file)
        # 另外保存文件
        save_f1 = QAction('另存为...', self)
        save_f1.setStatusTip('另存为...')
        save_f1.setShortcut('Ctrl+Shift+S')
        file_menu.addAction(save_f1)
        save_f1.triggered.connect(self.other_file)
        # 分隔
        file_menu.addSeparator()

        # 退出
        exit_act = QAction('退出(&E)', self)
        exit_act.setShortcut('Ctrl+Q')
        exit_act.setStatusTip('退出程序')
        exit_act.triggered.connect(self.exit_sys)
        file_menu.addAction(exit_act)

        # 编辑菜单
        edit_menu = menubar.addMenu('编辑(&E)')
        # 撤销
        undo = QAction('撤销(&U)', self)
        undo.setShortcut('Ctrl+Z')
        undo.setStatusTip('撤销输入')
        undo.triggered.connect(lambda: self.e_menu('undo'))
        edit_menu.addAction(undo)
        # 重做
        redo = QAction('重做(&R)', self)
        redo.setShortcut('Ctrl+Y')
        redo.setStatusTip('重做')
        redo.triggered.connect(lambda: self.e_menu('redo'))
        edit_menu.addAction(redo)
        # 分隔
        edit_menu.addSeparator()
        # 剪切
        tx = QAction('剪切(&X)', self)
        tx.setShortcut('Ctrl+X')
        tx.setStatusTip('剪切')
        tx.triggered.connect(lambda: self.e_menu('cut'))
        edit_menu.addAction(tx)
        # 复制
        copy = QAction('复制(&C)', self)
        copy.setShortcut('Ctrl+C')
        copy.setStatusTip('复制')
        copy.triggered.connect(lambda: self.e_menu('copy'))
        edit_menu.addAction(copy)
        # 粘贴
        paste = QAction('粘贴(&P)', self)
        paste.setShortcut('Ctrl+V')
        paste.setStatusTip('粘贴')
        paste.triggered.connect(lambda: self.e_menu('paste'))
        edit_menu.addAction(paste)
        # 全选
        all_select = QAction('全选(&A)', self)
        all_select.setShortcut('Ctrl+A')
        all_select.setStatusTip('全选')
        all_select.triggered.connect(lambda: self.e_menu('s_all'))
        edit_menu.addAction(all_select)

        # RexToMfa
        to_mfa = QAction('REXtoDFA(&R)', self)
        to_mfa.setShortcut('Ctrl+Shift+F1')
        to_mfa.setStatusTip('转换正则表达式')
        to_mfa.triggered.connect(self.REXToDFA)
        menubar.addAction(to_mfa)

        # LL1预测分析
        ll1 = QAction('LL1预测分析(&L)', self)
        ll1.setShortcut('Ctrl+Shift+F2')
        ll1.setStatusTip('LL1预测分析')
        ll1.triggered.connect(self.ll1_pre)
        menubar.addAction(ll1)

        # 词法分析
        self.word_analysis = menubar.addMenu('词法分析(&A)')
        # 单词识别
        word_re = QAction('单词识别', self)
        word_re.setShortcut('Ctrl+Shift+F3')
        word_re.setStatusTip('单词识别')
        word_re.triggered.connect(self.word_a)
        # 自动生成
        auto1 = QAction('自动生成', self)
        auto1.setStatusTip('自动生成')
        auto1.setShortcut('Ctrl+Shift+F4')
        auto1.triggered.connect(self.auto_word)

        self.word_analysis.addAction(word_re)
        self.word_analysis.addAction(auto1)
        self.word_analysis.setEnabled(False)

        # 语法分析
        self.grammar_analysis = QAction('语法分析(&G)', self)
        self.grammar_analysis.setStatusTip('语法分析')
        self.grammar_analysis.setShortcut('Ctrl+Shift+F5')
        self.grammar_analysis.triggered.connect(self.grammar_a)
        self.grammar_analysis.setEnabled(False)
        menubar.addAction(self.grammar_analysis)

        # 生成目标代码
        self.assem_code = QAction('目标代码(&M)', self)
        self.assem_code.setStatusTip('生成目标代码')
        self.assem_code.setShortcut('Ctrl+Shift+F6')
        self.assem_code.triggered.connect(self.build_code)
        self.assem_code.setEnabled(False)
        menubar.addAction(self.assem_code)

        # 中间代码解释
        self.inter = QAction('运行(&U)')
        self.inter.setShortcut('Ctrl+Shift+F7')
        self.inter.setStatusTip('运行')
        self.inter.triggered.connect(self.run)
        self.inter.setEnabled(False)
        menubar.addAction(self.inter)

        # 设置
        settings = menubar.addMenu('设置(&T)')
        # 字体
        font = settings.addMenu('字体')
        font1 = QAction('编辑框', self)
        font1.setShortcut('Ctrl+E')
        font1.setStatusTip('修改编辑框的字体')
        font1.triggered.connect(lambda: self.fix_font(1))

        font2 = QAction("错误框", self)
        font2.setShortcut('Ctrl+Shift+E')
        font2.setStatusTip('修改错误框的字体')
        font2.triggered.connect(lambda: self.fix_font(2))

        font3 = QAction("结果框", self)
        font3.setShortcut('Ctrl+Shift+R')
        font3.setStatusTip('修改结果框的字体')
        font3.triggered.connect(lambda: self.fix_font(3))

        font.addAction(font1)
        font.addAction(font2)
        font.addAction(font3)

        # 关于
        help_m = menubar.addMenu('帮助(&H)')
        about = QAction('关于(&A)', self)
        about.setStatusTip('关于')
        about.setShortcut('Ctrl+Shift+F8')
        about.triggered.connect(self.about)
        update = QAction('检查更新(&U)', self)
        update.setStatusTip('检查更新')
        update.setShortcut('Ctrl+Shift+F9')
        update.triggered.connect(self.update_C)
        help_m.addAction(about)
        help_m.addAction(update)

    def init_tool(self):  # 初始化工具栏
        tool_bur = self.addToolBar('工具')
        new_file = QAction(QIcon('./img/new.png'), '新建', self)
        new_file.setStatusTip('新建')
        new_file.triggered.connect(self.create_file)
        open_f = QAction(QIcon('./img/open.png'), '打开', self)
        open_f.setStatusTip('打开')
        open_f.triggered.connect(lambda: self.open_file(1))
        save = QAction(QIcon('./img/save.png'), '保存', self)
        save.triggered.connect(self.save_file)
        save.setStatusTip('保存')
        copy_t = QAction(QIcon('./img/copy.png'), '复制', self)
        copy_t.setStatusTip('复制')
        copy_t.triggered.connect(lambda: self.e_menu('copy'))
        paste_t = QAction(QIcon('./img/paste.png'), '粘贴', self)
        paste_t.setStatusTip('粘贴')
        paste_t.triggered.connect(lambda: self.e_menu('paste'))
        cut_t = QAction(QIcon('./img/cut.png'), '剪切', self)
        cut_t.setStatusTip('复制')
        cut_t.triggered.connect(lambda: self.e_menu('cut'))
        undo_t = QAction(QIcon('./img/undo.png'), '撤销', self)
        undo_t.setStatusTip('撤销')
        undo_t.triggered.connect(lambda: self.e_menu('undo'))
        redo_t = QAction(QIcon('./img/redo.png'), '重做', self)
        redo_t.setStatusTip('重做')
        redo_t.triggered.connect(lambda: self.e_menu('redo'))
        tool_bur.addAction(save)
        tool_bur.addAction(new_file)
        tool_bur.addAction(open_f)
        tool_bur.addAction(copy_t)
        tool_bur.addAction(paste_t)
        tool_bur.addAction(cut_t)
        tool_bur.addAction(undo_t)
        tool_bur.addAction(redo_t)
        tool_bur.setIconSize(QSize(25, 25))

    # 初始化界面
    def InitUI(self):
        # 主窗口
        widget = QWidget()
        self.setCentralWidget(widget)
        # 主窗口大小16:9
        self.setGeometry(0, 0, 1440, 810)
        # 初始居中
        self.center()
        # 界面标题
        self.setWindowTitle('C-Example')
        self.setWindowIcon(QIcon('./Img/logo.png'))

        # 状态栏
        self.statusBar()
        # 初始菜单和工具栏
        self.init_menu()
        self.init_tool()

        # 主布局，用于放置显示文件的文本框和结果显示框
        main_box = QVBoxLayout()
        # 设置距离边缘的间距左、上、右、下，留有功能行
        main_box.setContentsMargins(0, 0, 0, 0)

        # 显示源文件布局，水平，还有显示行数框
        file_box = QHBoxLayout()
        file_box.addWidget(self.we1)

        # 放置行数框
        line_box = QHBoxLayout()
        line_box.addWidget(self.line)
        line_box.setContentsMargins(0, 0, 0, 0)
        self.we1.setLayout(line_box)

        # 默认字体
        self.text.setFont(QFont('微软雅黑', 11))
        self.line.setFont(QFont('微软雅黑', 11))
        # 不自动换行
        self.text.setLineWrapMode(0)
        # 行数框隐藏滚动条
        self.line.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        # 放置文本框
        file_box.addWidget(self.text)
        file_box.setContentsMargins(0, 0, 0, 0)

        # 结果显示，水平放置
        result_box = QHBoxLayout()
        # 默认字体
        self.text1.setFont(QFont('微软雅黑', 10))
        self.text2.setFont(QFont('微软雅黑', 10))
        # 不自动换行
        self.text1.setLineWrapMode(0)
        self.text2.setLineWrapMode(0)
        # 添加
        result_box.addWidget(self.text1)
        result_box.addWidget(self.text2)
        result_box.setStretch(0, 2)
        result_box.setStretch(1, 1)

        # 添加三个框
        main_box.addLayout(file_box)
        main_box.addLayout(result_box)
        main_box.setSpacing(0)  # 彼此间距0
        # 0 1的长度比2 1
        main_box.setStretch(0, 2)
        main_box.setStretch(1, 1)

        # 初始化行数框宽度
        space = int(1.8 * self.line.fontMetrics().width('9') * len(str(self.line_num)))
        self.we1.setFixedWidth(space)

        self.line.setStyleSheet("background-color:lightGray;")
        self.line.installEventFilter(self)
        # 窗口添加
        widget.setLayout(main_box)
        # 监控修改
        self.text.textChanged.connect(self.text_change)
        # 显示
        self.show()

    def csc1(self):  # 行数框跟随文本框
        self.sc2.setValue(self.sc1.value())

    def csc2(self):  # 文本框跟随行数框
        self.sc1.setValue(self.sc2.value())

    # 主窗口初始居中
    def center(self):
        # 获取屏幕尺寸
        screen = QDesktopWidget().screenGeometry()
        # 窗口大小
        size = self.geometry()
        # 移至中间(参数整数)
        self.move((screen.width() - size.width()) // 2,
                  (screen.height() - size.height()) // 2)

    # 加载文件
    def open_file(self, mode):
        if mode:
            # 调用资源管理选择文件
            file_name = QFileDialog.getOpenFileName(self, '打开文件', './', self.file_type)
        else:  # 新建文件打开文件
            file_name = [self.now_file]
        # 文件不为空
        if file_name[0]:
            try:
                with open(file_name[0], 'rb') as f:
                    s = f.read()
                    encoding_type = chardet.detect(s)['encoding']
                with open(file_name[0], 'r', encoding=encoding_type) as f:
                    data = f.read()  # 读取
                    self.text.setText(data)
                    cursor = self.text.textCursor()  # 光标
                    cursor.movePosition(QTextCursor.Start)  # 光标移至开头
                    self.text.setTextCursor(cursor)  # 设置光标位置
                    self.now_file = file_name[0]
                    self.s_file = file_name[0]
                    self.word_analysis.setEnabled(True)
                    self.setWindowTitle('C-Example - ' + os.path.basename(self.now_file))
                    self.text1.clear()
                    self.text2.clear()
            except:
                self.text.setText("打开文件失败，可能是文件类型错误")

    # 新建文件
    def create_file(self, mode):
        file_name = QFileDialog.getSaveFileName(self, '选择新建文件的路径', './', self.file_type)
        # 选择了路径，没有直接返回
        if file_name[0]:
            if mode == 1:
                self.text.clear()
            self.now_file = file_name[0]
            self.s_file = file_name[0]
            self.save_file()
            self.open_file(0)

    # 保存文件
    def save_file(self):
        if self.s_file:
            with open(self.s_file, 'w', encoding='UTF-8') as f:
                s = self.text.toPlainText()
                f.write(s)
        else:
            self.create_file(0)

    # 另存文件
    def other_file(self):
        if self.s_file:
            file_name = QFileDialog.getSaveFileName(self, '选择另存文件的路径', './', self.file_type)
            # 选择了路径，没有直接返回
            if file_name[0]:
                self.s_file = file_name[0]
                self.save_file()

    def e_menu(self, s):  # 编辑菜单
        if self.now_file:
            if s == 'undo':  # 撤销
                self.text.undo()
                return
            if s == 'redo':  # 重做
                self.text.redo()
                return
            if s == 's_all':  # 全选
                self.text.selectAll()
                return
            if s == 'copy':  # 复制
                self.text.copy()
                return
            if s == 'paste':  # 粘贴
                self.text.paste()
                return
            if s == 'cut':  # 剪切
                self.text.cut()
                return

    def REXToDFA(self):
        s1 = self.text.toPlainText()
        s1 = s1.replace('\n', '')
        t = '警告：需要自己的系统中有设置默认打开pdf文件的应用，否则会显示输入错误！'
        QMessageBox.warning(self, '提示', t)
        try:
            if s1:
                nfa = To_NFA(s1)
                graph = nfa.to_nfa()
                if not graph:
                    self.text1.setText('Error Input:' + s1 + '!')
                else:
                    draw_graph(graph, 'NFA')
                    dfa = To_DFA(graph)
                    graph = dfa.to_dfa()
                    draw_graph(graph, 'DFA')
                    min_dfa = To_min(graph)
                    graph = min_dfa.min_dfa()
                    draw_graph(graph, 'MFA')
        except Exception as e:
            self.text1.setText('Error Input:' + s1 + '!')

    def word_a(self):  # 利用状态转换图进行词法分析
        if self.now_file:
            try:
                self.save_file()
            except Exception as e:
                t = str(e) + '!\n进行分析前会自动保存文件\n但该文件无法保存, 请注意自己保存文件！'
                QMessageBox.warning(self, '提示', t)
            finally:
                s = self.text.toPlainText()
                tx = word(s)
                tx.cut()
                r = result()
                error, token = r.result_word(tx.error, tx.token, self.now_file)
                self.text1.setText(error)
                self.text2.setText(token)
                if error == '0 error(s)':
                    self.token = tx.token
                    self.grammar_analysis.setEnabled(True)

    def auto_word(self):  # 利用lex进行词法分析
        if self.now_file:
            try:
                self.save_file()
            except Exception as e:
                t = str(e) + '!\n进行分析前会自动保存文件\n但该文件无法保存, 请注意自己保存文件！'
                QMessageBox.warning(self, '提示', t)
            finally:
                s = self.text.toPlainText()
                tx = auto(s)
                self.text2.setText(tx.toke)
                if tx.errors == '':
                    self.token = tx.toke
                    self.text1.setText('词法错误:\n0 error(s)')
                else:
                    self.text1.setText('词法错误:\n' + str(tx.errors.count('\n')) + ' error(s)\n' + tx.errors)

    def grammar_a(self):
        self.grammar = Grammar(self.token)
        self.grammar.analysis_main()
        self.code = self.grammar.semantic.temp_code
        self.text1.clear()
        self.text2.clear()
        if self.grammar.error_num == 0 and self.grammar.semantic.error_num == 0:
            self.text1.setText(self.grammar.message)
            self.text2.setText('语法错误:\n' + str(self.grammar.error_num) + ' error(s)' + self.grammar.error)
            self.text2.append(
                '语义错误:\n' + str(self.grammar.semantic.error_num) + ' error(s)\n' + self.grammar.semantic.error)
            self.mid.set_code(self.code)
            self.mid.show()
            with open('./Debug/mid_code.txt', 'w', encoding='utf-8') as f1:
                for code in range(len(self.grammar.semantic.temp_code)):
                    f1.write(str(code) + ': ' + str(self.grammar.semantic.temp_code[code]) + '\n')
            self.assem_code.setEnabled(True)
            self.inter.setEnabled(True)
        else:
            self.text1.setText('语法错误:\n' + str(self.grammar.error_num) + ' error(s)\n' + self.grammar.error)
            if self.grammar.semantic.error_num != 0:
                self.text1.append(
                    '语义错误:\n' + str(self.grammar.semantic.error_num) + ' error(s)\n' + self.grammar.semantic.error)
            self.inter.setEnabled(False)

    def build_code(self):
        assem = Assem_Code(self.code)
        s = assem.first_step()
        self.ass.init_UI(s)
        self.ass.show()

    def ll1_pre(self):
        self.LL1_ui.textFirst_set.clear()
        self.LL1_ui.textFollow_set.clear()
        self.LL1_ui.tableAnalyze.clear()
        self.LL1_ui.tableStack.clear()
        self.LL1_ui.textEdit.clear()
        self.widget.show()

    def run(self):
        temp_code = self.grammar.semantic.temp_code
        ident_all = self.grammar.semantic.ident_all
        func_place = self.grammar.semantic.get_func_place(temp_code)
        inte = inter(temp_code, ident_all, func_place)
        t = threading.Thread(target=inte.run_code)
        t.setDaemon(True)
        t.start()

    def fix_font(self, mode):  # 修改字体
        if mode == 1:
            font = self.text.font()
            font, changed = QFontDialog.getFont(font, self, "字体设置")
            if changed:
                self.text.setFont(font)
                self.line.setFont(font)
                space = int(1.8 * self.line.fontMetrics().width('9') * len(str(self.line_num)))
                self.we1.setFixedWidth(space)
                return
        if mode == 2:
            font = self.text1.font()
            font, changed = QFontDialog.getFont(font, self, "字体设置")
            if changed:
                self.text1.setFont(font)
        if mode == 3:
            font = self.text2.font()
            font, changed = QFontDialog.getFont(font, self, "字体设置")
            if changed:
                self.text2.setFont(font)

    def about(self):
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("./Img/logo.png"), QtGui.QIcon.Normal,
                       QtGui.QIcon.Off)
        qw = QtWidgets.QWidget()
        qw.setWindowIcon(icon)
        reply = QMessageBox.about(qw, 'C-Example',
                                  'This is my own App\nversion: 0.0.0\n如有问题，请邮件联系\nE-mail: jiangyichen@gmail.com')

    def update_C(self):
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("./Img/logo.png"), QtGui.QIcon.Normal,
                       QtGui.QIcon.Off)
        qw = QtWidgets.QWidget()
        qw.setWindowIcon(icon)
        reply = QMessageBox.about(qw, 'C-Example',
                                  '已安装最新版本,如有bug或有推荐的请邮件联系\nE-mail: jiangyichen@gmail.com')

    def exit_sys(self):  # 按键退出
        reply = QMessageBox.question(self, '提示', "是否退出？", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            app.quit()

    def closeEvent(self, event):  # 关闭事件
        reply = QMessageBox.question(self, '提示', "是否退出？", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:  # 接收退出
            event.accept()
        else:  # 忽略不退出
            event.ignore()

    def text_change(self):  # 行数控制
        self.grammar_analysis.setEnabled(False)
        self.assem_code.setEnabled(False)
        self.inter.setEnabled(False)
        self.line_num = 1
        lines = str(self.line_num) + '\n'
        s = self.text.toPlainText()
        len1 = len(s)
        for x in range(len1):
            if s[x] == '\n':
                self.line_num += 1
                lines = lines + str(self.line_num) + '\n'
        space = int(1.8 * self.line.fontMetrics().width('9') * len(str(self.line_num)))
        self.we1.setFixedWidth(space)
        lines = lines.strip('\n')
        self.line.setText(lines)
        self.token = ''

    # 鼠标滚轮移动文本框
    def wheelEvent(self, event):
        # 控制一起滚动
        self.sc1.valueChanged.connect(self.csc1)
        self.sc2.valueChanged.connect(self.csc2)


if __name__ == '__main__':
    # 任务栏图标
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("my_appid")
    app = QApplication(sys.argv)
    test = main()
    sys.exit(app.exec_())
