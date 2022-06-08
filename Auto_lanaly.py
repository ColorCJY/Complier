import json

import ply.lex as lex


def load(s):  # 加载文件
    with open(s, 'r') as f:
        return json.load(f)


keywords = {'auto': '000', 'break': '001', 'case': '002', 'char': '003', 'const': '004',
            'continue': '005', 'default': '006', 'do': '007', 'double': '008', 'else': '009',
            'enum': '010', 'extern': '011', 'float': '012', 'for': '013', 'goto': '014',
            'if': '015', 'int': '016', 'long': '017', 'register': '018', 'return': '019',
            'short': '020', 'signed': '021', 'sizeof': '022', 'static': '023', 'struct': '024',
            'switch': '025', 'typedef': '026', 'union': '027', 'unsigned': '028', 'void': '029',
            'volatile': '030', 'while': '031', "integers": "081", "strings": "083", "floats": "084",
            "identifiers": "086", "octals": "087", "hexes": "088", "{": "072", "}": "073", ";": "074",
            ",": "075", "chars": "082", "#include": "091", "head_file": "092", "#define": "093"
            }
op = load('Data//operator.json')
keywords.update(op)

tokens = [
             # 数据类型
             'error_num',  # 数字错误
             'num_error',  # 数字错误
             'error_symbol',  # 符号错误
             'error_match',  # 匹配错误
             'identifier',  # 标识符
             'integer',  # 十进制整数
             'octal',  # 八进制
             'hex',  # 十六进制
             'float',  # 浮点数
             'string',  # 字符串
             'char',  # 字符
             'annotation',  # 注释
             'op1',  # 运算符1
             'op2',  # 运算符2
             'delimiters',  # 分隔符
             'backspace',  # 空格或制表
             'pre'  # 预处理
             'error_an'  # 错误注释
         ] + list(keywords.values())


def t_pre(t):  # 预处理
    r"""\#include[ ]*<.*[.]h>|\#include[ ]*".*[.]h"|\#define"""
    if t.value in keywords:
        t.type = keywords.get(t.value, 'pre')
    return t


# 标记的正则表达
def t_delimiters(t):
    r"""[,{};]"""
    t.type = keywords.get(t.value, 'delimiters')
    return t


def t_annotation(t):  # 识别注释
    r"""(/\*(.|\n)*?\*/)|([/][/].*(\n)?)"""
    t.lexer.lineno += t.value.count("\n")
    return t


def t_backspace(t):
    r"""[ ]|[\t]"""


def t_error_an(t):
    r"""/\*(.|\n)+"""


def t_error_num(t):  # 十六进制不匹配 八进制不匹配 小数
    r"""(0(x|X)[0-9a-fA-F]*[G-Zg-z]+)[0-9a-fA-F]*|(0[0-7]*[9]+[0-7]*.*)|00+[.]?.*|([1-9][0-9]*|0)[.]$|
    ([1-9][0-9]*(\D*^\n)+[0-9]*|0(\D*^\n))+[.][0-9]+|([1-9][0-9]*|0)[.][0-9]*[a-df-zA-DF-Z]+.*|([1-9][0-9]*|0)[.]
    [0-9]+(E|e)([-+]?[0-9]*[a-zA-Z@#\$]+[0-9]*[\n ;,]|[a-zA-Z].*)|
    ([1-9][0-9]*|0)[.][1-9][0-9]*[eE][-+]?([,;]*[\n ]|[,;])"""
    t.lexer.lineno += t.value.count("\n")
    return t


def t_hex(t):  # 十六进制
    r"""0(x|X)[0-9a-fA-F]+"""
    t.type = keywords.get('hexes', 'hex')
    return t


def t_float(t):  # 浮点数
    r"""([1-9][0-9]*|0)[.][0-9]+(E|e[-+]?[0-9]+)?"""
    t.type = keywords.get('floats', 'float')
    return t


def t_num_error(t):  # 十进制数错误
    r"""([1-9][0-9]*|0)([a-df-zA-DF-Z]+.*|[Ee][A-Za-z].*)|[1-9][0-9]*[eE][-+]?([,;]*[\n ]|[,;])"""
    t.lexer.lineno += t.value.count("\n")
    return t


def t_integer(t):  # 整数
    r"""([1-9][0-9]*)(E|e[-\+]?[0-9]+)?|0"""
    t.type = keywords.get('integers', 'integer')
    return t


def t_identifier(t):  # 识别标识符
    r"""[a-z_A-Z][A-Za-z_0-9]*"""
    if t.value in keywords:
        t.type = keywords.get(t.value, 'identifier')
    else:
        t.type = keywords.get('identifiers', 'identifier')
    return t


def t_op2(t):
    r""">>=|<<=|\+\+|--|>>|<<|>=|<=|==|!=|&&|\|\||/=|\*=|%=|\+=|-=|&=|\^=|\|="""
    t.type = keywords.get(t.value, 'op2')
    return t


def t_op1(t):
    r"""->|\*|/|\+|-|%|<|>|=|\.|~|&|\^|\||\(|\)|\[|\]|!"""
    t.type = keywords.get(t.value, 'op1')
    return t


def t_char(t):
    r"""['](.|\'|\n|\t)?[']"""
    t.type = keywords.get('chars', 'char')
    return t


def t_string(t):  # 字符串
    r"""["](.*|(\")|\n)?["]"""
    t.type = keywords.get('strings', 'string')
    return t


def t_error_match(t):  # 符号不匹配问题
    r"""([/][*].*)|(["].*)|(['].*)"""
    return t


def t_octal(t):  # 八进制
    r"""(0[0-7]+)"""
    t.type = keywords.get('octals', 'octal')
    return t


# 如果遇到 \n 则将其设为新的一行
def t_newline(t):
    r"""\n+"""
    t.lexer.lineno += t.value.count("\n")


# 未定义规则字符的错误处理
def t_error(t):
    # 此处的 t.value 包含未标记的其余输入
    t.lexer.skip(1)
    return t


class auto:
    def __init__(self, s):
        lexer = lex.lex()
        lexer.input(s)
        self.toke = ''
        self.errors = ''
        self.line = 0
        while tok := lexer.token():
            s = str(tok)
            s = s.split('LexToken')
            t1 = s[1]
            t2 = (s[1].split(','))[0].split('(')
            if t2[1] == 'annotation':
                self.toke = self.toke
            elif t2[1] == 'error':
                error = 'illegal character'
                m = (s[1].split(','))
                self.line = m[len(m) - 2]
                self.errors += error + "(line:" + str(self.line) + '): ' + m[1][1] + '\n'
            elif t2[1] in ['num_error', 'error_num', 'error_match', 'error_symbol']:
                m = (s[1].split(','))
                error = m[1]
                self.line = m[2]
                self.errors += t2[1] + "(line:" + str(self.line) + '): ' + str(error) + '\n'
            elif t2[1] == 'pre':
                t1 = t1.replace('pre', '091')
                self.toke = self.toke + t1 + '\n'
            elif t2[1] == 'error_an':
                m = (s[1].split(','))
                error = m[1]
                self.line = m[2]
                self.errors += t2[1] + "(line:" + str(self.line) + '): ' + str(error) + '\n'
            else:
                self.toke = self.toke + t1 + '\n'

