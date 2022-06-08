import json

delimiters = '{},;\n'
backspace = ' \t'
operator = '()[]!*/%+-<>=.~&|^'
fen = delimiters + backspace + operator  # 分隔符
fen = fen.replace('.', '')


def load(s):  # 加载文件
    with open(s, 'r') as f:
        return json.load(f)


class word:
    def __init__(self, s):
        self.line = 1  # 行数
        self.column = 1  # 列数
        self.token = []  # 存取分析的结果
        # 加载错误信息
        self.code_error = load('Data//word_error.json')
        # 加载操作符种别码
        self.code_op = load('Data//operator.json')
        # 加载界符种别码
        self.code_de = load('Data//delimiters.json')
        # 加载预处理的
        self.code_pr = load('Data//head.json')
        # 加载关键词的
        self.code_key = load('Data//keywords.json')
        self.error = []  # 错误
        self.s = s + ' \n'  # 代码文件，附加的结束标志

    # 判断行数
    def judge_line(self, i):
        self.column += 1
        if self.s[i] == '\n':
            self.line += 1  # 当前行数+1
            self.column = 1
        i = i + 1  # 下一个字符
        return i

    # 错误处理
    def error_deal(self, n, code):
        i = n
        line = '(line ' + str(self.line) + ', col:' + str(self.column) + '): '  # 行数列数
        if code not in ['800', '408', '409', '405', '402'] and i < len(self.s):
            while self.s[i] not in fen:  # 跳过这个单词
                i = i + 1
            e = 'error ' + code + ': ' + self.code_error[code] + self.s[n:i]  # 错误信息
        else:
            e = 'error ' + code + ': ' + self.code_error[code]
        self.error.append(line + e)  # 添加信息
        return i

    def cut(self):
        i = 0
        while i < len(self.s):
            if self.s[i] in (' ', '\t'):  # 空格和制表符跳过
                i = self.judge_line(i)
                continue
            if self.s[i] == '_' or self.s[i].isalpha():  # 获取标识符
                i = self.get_ident(i)
                continue
            if self.s[i].isdigit():  # 获取数字
                i = self.get_num(i)
                continue
            if self.s[i] in '+-&|%^=!*':  # 获取四则逻辑等运算符
                i = self.get_op(i, 1)
                continue
            if self.s[i] in '<>':  # 不等运算符和位运算符
                i = self.get_op(i, 2)
                continue
            if self.s[i] in '()[]~':  # ( ) [ ] . ~
                self.token.append((self.code_op[self.s[i]], self.s[i], self.line, self.column))
                i = self.judge_line(i)
                continue
            if self.s[i] in '{};,':  # 分隔符
                self.token.append((self.code_de[self.s[i]], self.s[i], self.line, self.column))
                i = self.judge_line(i)
                continue
            if self.s[i] == '#':  # 预处理
                i = self.get_pre(i)
                continue
            if self.s[i] == '/':  # 判断注释还是除号
                i = self.get_comments(i)
                continue
            if self.s[i] == '"':  # 处理字符串
                i = self.get_string(i)
                continue
            if self.s[i] == "'":  # 处理字符
                i = self.get_char(i)
                continue
            if self.s[i] != '\n':
                line = '(line ' + str(self.line) + ', col:' + str(self.column) + '): '  # 行数列数
                self.error.append(line + "error 404: unknown character, not use " + self.s[i])
            i = self.judge_line(i)

    def get_ident(self, n):  # 获取标识符
        state = 0  # 初始状态
        column = self.column
        i = n
        while i < len(self.s):
            if state == 0:  # 初始取下一个字符
                state = 1
                i = self.judge_line(i)
                continue
            if state == 1:
                # 标识符由_、字母、数字组成
                if self.s[i] == '_' or self.s[i].isalpha() or self.s[i].isdigit():
                    state = 1
                    i = self.judge_line(i)
                # 构词结束
                else:
                    x = self.s[n:i]
                    if x in self.code_key:  # 关键词
                        op = self.code_key[x]
                        self.token.append((op, x, self.line, column))
                    else:  # 自定义标识符
                        self.token.append(('086', self.s[n:i], self.line, column))  # 加入token串
                    break
        return i  # 返回下一个字符所在下标

    def get_num(self, n):  # 获取数字
        column = self.column
        i = n  # 便于记录
        state = 0  # 状态
        m = '081'  # 区分小数整数(以E|e前的数区分科学计数法是小数还是整数)
        t = 0  # 科学计数法的结束标志
        while i < len(self.s):
            if state == 0:
                if '1' <= self.s[i] <= '9':  # 10进制数最高位1-9
                    state = 1
                else:
                    if self.s[i] == '0':  # 0或八、十六进制
                        state = 3
                i = self.judge_line(i)  # 去下一个字符
                continue

            if state == 1:
                if '0' <= self.s[i] <= '9':  # 十进制
                    state = 1
                else:
                    if self.s[i] in fen:  # 正确10进制
                        self.token.append((m, self.s[n:i], self.line, column))
                        break
                    if self.s[i] == 'e' or self.s[i] == 'E':  # 科学计数
                        state = 10
                    elif self.s[i] == '.':  # >1的小数
                        m = '084'
                        state = 8
                    else:  # 其余错误
                        i = self.error_deal(n, "403")
                        break
                i = self.judge_line(i)
                continue

            if state == 3:  # 以0开头的数
                if self.s[i] in fen:  # 10进制0
                    self.token.append((m, self.s[n:i], self.line, column))
                    break
                if self.s[i] == 'X' or self.s[i] == 'x':  # 16进制
                    state = 5
                elif '1' <= self.s[i] <= '7':  # 8进制
                    state = '3'
                elif self.s[i] == '.':  # 0.小数
                    m = '084'
                    state = 8
                else:
                    i = self.error_deal(n, "403")
                    break
                i = self.judge_line(i)
                continue

            if state == '3':  # 8进制
                if self.s[i] in fen:
                    self.token.append(('087', self.s[n:i], self.line, column))
                    break
                if '0' <= self.s[i] <= '7':  # 8进制正常的数
                    state = '3'
                    i = self.judge_line(i)
                    continue
                else:  # 其余错误
                    i = self.error_deal(n, "403")
                    break

            if state == 5:  # 十六进制开头
                x = '123456789abcdefABCDEF'
                if self.s[i] in x:
                    state = 6
                    i = self.judge_line(i)
                    continue
                else:
                    i = self.error_deal(n, "403")
                    break

            if state == 6:  # 十六进制后部分
                x = '0123456789abcdefABCDEF'
                if self.s[i] in fen:
                    self.token.append(('088', self.s[n:i], self.line, column))
                    break
                if self.s[i] in x:
                    state = 6
                    i = self.judge_line(i)
                    continue
                else:
                    i = self.error_deal(n, "403")
                    break

            if state == 8:
                if self.s[i].isdigit():
                    state = 9
                    i = self.judge_line(i)
                    continue
                else:
                    i = self.error_deal(n, "403")
                    break

            if state == 9:  # 小数的小数部分
                if self.s[i] in fen:
                    self.token.append((m, self.s[n:i], self.line, column))
                    break
                elif self.s[i].isdigit():
                    state = 9
                    i = self.judge_line(i)
                    continue
                elif self.s[i] == 'e' or self.s[i] == 'E':
                    state = 10
                    i = self.judge_line(i)
                    continue
                else:
                    i = self.error_deal(n, "403")
                    break

            if state == 10:  # 指数指出正负或者不带符号(为正)
                if self.s[i] == '+' or self.s[i] == '-' or self.s[i].isdigit():
                    if self.s[i].isdigit():
                        t = 1
                    state = 11
                    i = self.judge_line(i)
                    continue
                else:
                    i = self.error_deal(n, "403")
                    break

            if state == 11:  # 指数部分
                if self.s[i] in fen and t == 1:
                    self.token.append((m, self.s[n:i], self.line, column))
                    break
                if self.s[i].isdigit():
                    state = 11
                    t = 1
                    i = self.judge_line(i)
                    continue
                else:
                    i = self.error_deal(n, "403")
                    break
        return i

    def get_comments(self, n):  # 去除注释
        column = self.column
        state = 1  # 初始状态
        i = n
        while i < len(self.s):
            i = self.judge_line(i)
            if i >= len(self.s):
                break
            if state == 1:
                if self.s[i] == '/':  # 单行注释
                    state = 2
                    continue
                if self.s[i] == '*':  # 多行注释
                    state = 3
                    continue
                else:  # 除号
                    if self.s[i] == '=':
                        self.token.append((self.code_op['/='], '/=', self.line, column))
                        i = self.judge_line(i)
                    else:
                        self.token.append((self.code_op['/'], '/', self.line, column))
                    break

            if state == 2:
                while i < len(self.s) and self.s[i] != '\n':
                    i = self.judge_line(i)
                break

            if state == 3:
                if self.s[i] == '*':
                    state = 4
                    continue
                else:
                    continue
            if state == 4:
                if self.s[i] == '/':
                    i = self.judge_line(i)
                    break
                elif self.s[i] == '*':
                    continue
                else:
                    state = 3
        if i >= len(self.s):
            self.error_deal(i, '800')
        return i

    def get_op(self, n, m):  # 识别运算符
        column = self.column
        i = self.judge_line(n)
        if m == 1:
            if self.s[i - 1] in '%^!*':
                if self.s[i] == '=':  # %= *= /= != ^=
                    x = self.s[i - 1] + self.s[i]
                    self.token.append((self.code_op[x], x, self.line, column))
                    i = self.judge_line(i)
                else:  # % * / ! ^
                    x = self.s[i - 1]
                    self.token.append((self.code_op[x], x, self.line, column))
                return i

            # ++ -- && || ->  == += -= &= |=
            if self.s[i] == self.s[i - 1] or self.s[i] == '=' or (self.s[i - 1] == '-' and self.s[i] == '>'):
                x = self.s[i - 1] + self.s[i]
                self.token.append((self.code_op[x], x, self.line, column))
                i = self.judge_line(i)
            else:  # 单个 + - & | =
                x = self.s[i - 1]
                self.token.append((self.code_op[x], x, self.line, column))
            return i

        if m == 2:
            if self.s[i] == '=':  # >= <=
                x = self.s[i - 1] + self.s[i]
                self.token.append((self.code_op[x], x, self.line, column))
                i = self.judge_line(i)
                return i

            elif self.s[i] == self.s[i - 1] and self.s[i + 1] == '=':  # >>= <<=
                x = self.s[i - 1] + self.s[i] + self.s[i + 1]
                self.token.append((self.code_op[x], x, self.line, column))
                i = self.judge_line(i)
                i = self.judge_line(i)
                return i

            elif self.s[i] == self.s[i - 1]:  # >> <<
                x = self.s[i - 1] + self.s[i]
                self.token.append((self.code_op[x], x, self.line, column))
                i = self.judge_line(i)
                return i

            elif self.s[i] != self.s[i - 1]:  # > <
                x = self.s[i - 1]
                self.token.append((self.code_op[x], x, self.line, column))
                return i

    def get_pre(self, n):  # 获取define 和 include
        column = self.column
        column1 = self.column  # 头文件前的 '<' or '"' 所在列
        i = n
        line = self.line
        state = 0
        s1 = 'include'
        s2 = 'define'
        x = 0
        y = 0
        file = ''
        t = ''
        d = 0
        judge = 0  # 区分是否为头文件前头文件与 '<' or '"' 之间的空格
        num = 0  # 用于统计头文件与 '<' or '"' 之间的空格数的
        while i < len(self.s):
            if self.s[i] == '\n':  # 匹配到了define 和 include但没有后续或为子串
                if x != len(s1) and state == 3:
                    b = 0
                    break
                if y != len(s2) and state == 4:
                    b = 0
                    break
                b = 1
                break

            # 初始
            if state == 0:
                i = self.judge_line(i)
                state = 2
                continue

            if state == 2:
                if self.s[i] == s1[x]:  # 'i'
                    state = 3
                    x += 1
                elif self.s[i] == s2[y]:  # 'd'
                    d = i
                    state = 4
                    y += 1
                else:  # error
                    self.line = line
                    i = self.error_deal(n, '403')
                    return i
                i = self.judge_line(i)
                continue

            if state == 3:  # 判断include
                if x == len(s1):
                    state = 5  # 'include'
                    continue
                if self.s[i] == s1[x]:  # 'nclude'
                    state = 3
                    x += 1
                    i = self.judge_line(i)
                    continue
                else:  # 有不同
                    self.line = line
                    i = self.error_deal(n, '403')
                    return i

            if state == 4:  # 判断define
                if y == len(s2):
                    state = 6  # 'define'
                    continue
                if self.s[i] == s2[y]:  # 'efine'
                    state = 4
                    y += 1
                    i = self.judge_line(i)
                    continue
                else:  # 有不同
                    self.line = line
                    i = self.error_deal(n, '403')
                    return i

            if state == 5:  # 记录头文件
                if self.s[i] == '<' or self.s[i] == '\"':  # <"开始记录
                    column1 = self.column
                    state = 7
                    t = self.s[i]
                    i = self.judge_line(i)
                    continue
                elif self.s[i] in backspace:  # 空格跳过
                    state = 5
                    i = self.judge_line(i)
                else:  # 其他错误符号
                    i = self.error_deal(i, '409')
                    return i

            if state == 6:  # define
                tx = i
                if self.s[i] == ' ':
                    while self.s[tx] != '\n' and tx < len(self.s):
                        tx += 1  # 一行内
                    ts = self.s[d:tx]
                    m = ts.split(' ')  # 空格切割确定参数个数
                    xi = 0
                    while xi < len(m):
                        if m[xi] == '':  # 去除空字符
                            m.remove(m[xi])
                            xi -= 1
                        xi += 1
                    if len(m) != 3:  # 不等于三报错
                        b = 1
                        break
                    self.token.append((self.code_pr['#' + s2], '#' + s2, self.line, column))  # 正确添加
                    i = self.judge_line(i)
                    return i
                else:  # 没有空格错误
                    self.line = line
                    i = self.error_deal(n, '403')
                    return i

            if state == 7:
                if self.s[i] == '>' or self.s[i] == '"':  # >" end
                    self.token.append((self.code_pr['#' + s1], '#' + s1, self.line, column))  # 添加#include
                    if t == '"' and self.s[i] == '"':  # 区别添加"和><
                        x = self.code_de[t]
                        y = x
                    elif t == "<" and self.s[i] == '>':
                        x = self.code_op[t]
                        y = self.code_op[self.s[i]]
                    else:
                        return self.error_deal(i, '409') + 1
                    self.token.append((x, t, self.line, column1))
                    file = file.replace(' ', '')  # 去除空格,便于后面的操作
                    if file:
                        self.token.append((self.code_pr['head_file'], file, self.line, column1 + num + 1))  # 头文件名
                    self.token.append((y, self.s[i], self.line, self.column))
                    i = self.judge_line(i)
                    return i
                else:
                    if self.s[i] != ' ':
                        judge = 1
                        file += self.s[i]
                    if not judge:
                        num += 1
                i = self.judge_line(i)
        if (state == 4 or state == 3) and b != 1:  # 比较的串为define or include的子串
            self.line = line
            return self.error_deal(n, '403')
        if b == 1 and (state == 6 or state == 4):  # define 使用错误 缺少间隔
            return self.error_deal(i, '408')
        # include使用错误 依次为缺少< > 头文件的引用
        if b == 1 and (state == 5 or state == 7 or state == 3):
            return self.error_deal(i, '409')

    def get_string(self, n):  # 获取字符（串）
        column = self.column
        i = n
        state = 0
        while i < len(self.s):
            if state == 0:  # 初始开始获取字符
                state = 2
                i = self.judge_line(i)
                continue

            if state == 2:
                if self.s[i] != '"':
                    if i >= len(self.s):
                        state = 4
                        continue
                    if self.s[i] == '\n':
                        state = 4
                        continue
                    state = 2
                    i = self.judge_line(i)
                    continue
                else:
                    if self.s[i - 1] == '\\':
                        state = 2
                        i = self.judge_line(i)
                        continue
                    else:
                        self.token.append(('083', self.s[n:i + 1], self.line, column))
                        i = self.judge_line(i)
                        return i

            if state == 4:
                return self.error_deal(i, '405')

    def get_char(self, n):
        column = self.column
        i = n
        state = 0
        while i < len(self.s):
            if state == 0:
                state = 1
                i = self.judge_line(i)
                continue

            if state == 1:
                if self.s[i] == "'":
                    i = self.judge_line(i)
                    return self.error_deal(i, '402')
                if self.s[i] == '\\':
                    state = 7
                    i = self.judge_line(i)
                    continue
                state = 2
                i = self.judge_line(i)
                continue

            if state == 2:
                if self.s[i] == "'":
                    state = 3
                    i = self.judge_line(i)
                else:
                    while i < len(self.s) and self.s[i] not in ",;'\n{}()[]":
                        i = self.judge_line(i)
                    if i < len(self.s) and self.s[i] == "'":
                        i = self.judge_line(i)
                    e = 'error ' + '401' + ': ' + self.code_error['401'] + self.s[n:i]
                    line = '(line ' + str(self.line) + ', col:' + str(self.column) + '): '  # 行数列数
                    self.error.append(line + e)  # 添加信息
                    return i

            if state == 3:
                self.token.append(('082', self.s[n:i], self.line, column))
                return i

            if state == 7:
                i = self.judge_line(i)
                state = 2
                continue
