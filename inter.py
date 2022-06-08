import copy
import sys
import time


def write(value):
    if str(value).isdigit():
        print(value, end='')
    elif '-' in str(value) and str(value)[1:].isdigit():
        print(value, end='')
    elif '.' in str(value):
        t = str(value).split('.')
        if len(t) != 2:
            print(str(value)[1:-1].replace('\\n', '\n'), end='')
        else:
            print(value, end='')
    else:
        print(value[1:-1].replace('\\n', '\n'), end='')


class inter:
    def __init__(self, code, ident_all, func_place):
        self.code = code
        self.func_place = func_place
        self.ident_all = ident_all
        self.temp_T = {}
        self.now_func = 'main'
        self.now_ident = {}
        self.PC = self.func_place['main']['place'] + 1
        self.exit_code = 0

    def fix_value(self, op_num, func_field, values):
        while func_field >= 0:
            if func_field == 0 and 'all' in self.now_ident:
                ident = self.now_ident['all']
                s = 'all'
            else:
                ident = self.now_ident[self.now_func]
                s = self.now_func
            for i in range(len(ident)):
                if op_num in ident[i]:
                    value = ident[i][op_num]
                    for j in range(len(value)):
                        if func_field in value[j]:
                            self.now_ident[s][i][op_num][j][func_field] = values
                            return
            func_field -= 1

    def get_value(self, op_num, func_field):
        t = str(op_num)
        if t.isdigit():
            return eval(str(op_num))
        elif '-' in t and t[1:].isdigit():
            return eval(str(op_num))
        elif op_num in self.temp_T:
            v = self.temp_T[op_num]
            if str(v).isdigit():
                return eval(str(v))
            elif '-' in str(v) and str(v)[1:].isdigit():
                return eval(str(v))
            else:
                return v
        else:
            while func_field >= 0:
                if func_field == 0 and 'all' in self.now_ident:
                    ident = self.now_ident['all']
                elif self.now_func not in self.now_ident:
                    break
                else:
                    ident = self.now_ident[self.now_func]
                for i in ident:
                    if op_num in i:
                        value = i[op_num]
                        for j in value:
                            if func_field in j:
                                v = j[func_field]
                                if str(v):
                                    if str(v).isdigit():
                                        return eval(str(v))
                                    elif '-' in str(v) and str(v)[1:].isdigit():
                                        return eval(str(v))
                                    else:
                                        return v
                                else:
                                    break
                func_field -= 1
        if str(t).isdigit():
            return eval(str(t))
        elif '-' in str(t) and str(t)[1:].isdigit():
            return eval(str(t))
        else:
            return t

    def fix_now_ident(self):
        x = {}
        t = ''
        if 'all' in self.ident_all:
            x['all'] = self.ident_all['all']
        if self.now_func in self.ident_all:
            t = copy.deepcopy(self.ident_all[self.now_func])
        x[self.now_func] = t
        return x

    def run_code(self):
        a = time.time()
        try:
            return_T = []
            stack_para = []
            stack_pc = []
            stack_func = []
            stack_ident = []
            self.now_ident = self.fix_now_ident()
            while 1:
                now_code = self.code[self.PC]
                op = now_code[0]
                op_num1 = now_code[1]
                op_num2 = now_code[2]
                res = now_code[3]
                f = now_code[4]
                if op == 'sys':
                    print('\n程序结束，退出代码' + str(self.exit_code))
                    break
                elif op == '+':
                    value = self.get_value(op_num1, f) + self.get_value(op_num2, f)
                    self.temp_T[res] = value
                elif op == '-':
                    value = self.get_value(op_num1, f) - self.get_value(op_num2, f)
                    self.temp_T[res] = value
                elif op == '*':
                    value = self.get_value(op_num1, f) * self.get_value(op_num2, f)
                    self.temp_T[res] = value
                elif op == '/':
                    value = self.get_value(op_num1, f) // self.get_value(op_num2, f)
                    self.temp_T[res] = value
                elif op == '%':
                    value = self.get_value(op_num1, f) % self.get_value(op_num2, f)
                    self.temp_T[res] = value
                elif op == '&':
                    value = self.get_value(op_num1, f) & self.get_value(op_num2, f)
                    self.temp_T[res] = value
                elif op == '|':
                    value = self.get_value(op_num1, f) | self.get_value(op_num2, f)
                    self.temp_T[res] = value
                elif op == '^':
                    value = self.get_value(op_num1, f) ^ self.get_value(op_num2, f)
                    self.temp_T[res] = value
                elif op == '<':
                    if self.get_value(op_num1, f) < self.get_value(op_num2, f):
                        self.temp_T[res] = 1
                    else:
                        self.temp_T[res] = 0
                elif op == '<=':
                    if self.get_value(op_num1, f) <= self.get_value(op_num2, f):
                        self.temp_T[res] = 1
                    else:
                        self.temp_T[res] = 0
                elif op == '>':
                    if self.get_value(op_num1, f) > self.get_value(op_num2, f):
                        self.temp_T[res] = 1
                    else:
                        self.temp_T[res] = 0
                elif op == '>=':
                    if self.get_value(op_num1, f) >= self.get_value(op_num2, f):
                        self.temp_T[res] = 1
                    else:
                        self.temp_T[res] = 0
                elif op == '!=':
                    if self.get_value(op_num1, f) != self.get_value(op_num2, f):
                        self.temp_T[res] = 1
                    else:
                        self.temp_T[res] = 0
                elif op == '==':
                    if self.get_value(op_num1, f) == self.get_value(op_num2, f):
                        self.temp_T[res] = 1
                    else:
                        self.temp_T[res] = 0
                elif op == '=':
                    if res in self.temp_T:
                        self.temp_T[res] = self.get_value(op_num1, f)
                    else:
                        value = self.get_value(op_num1, f)
                        self.fix_value(res, f, value)
                elif op == '&&':
                    if self.get_value(op_num1, f) and self.get_value(op_num2, f):
                        self.temp_T[res] = 1
                    else:
                        self.temp_T[res] = 0
                elif op == '||':
                    if self.get_value(op_num1, f) or self.get_value(op_num2, f):
                        self.temp_T[res] = 1
                    else:
                        self.temp_T[res] = 0
                elif op == '!':
                    if not self.get_value(op_num1, f):
                        self.temp_T[res] = 1
                    else:
                        self.temp_T[res] = 0
                elif op == 'j':
                    self.PC = res
                    continue
                elif op == 'jnz':
                    value = self.get_value(op_num1, f)
                    if value:
                        self.PC = res
                        continue
                elif op == 'para':
                    value = self.get_value(op_num1, f)
                    stack_para.append(value)
                elif op == 'call' and op_num1 != 'read' and op_num1 != 'write':
                    return_T.append(res)
                    t = copy.deepcopy(self.now_ident)
                    stack_ident.append(t)
                    stack_func.append(self.now_func)
                    self.now_func = op_num1
                    self.now_ident = self.fix_now_ident()
                    para = self.func_place[op_num1]['para']
                    i = len(para) - 1
                    while i >= 0:
                        self.fix_value(para[i]['name'], 1, stack_para[-1])
                        stack_para.pop()
                        i -= 1
                    stack_pc.append(self.PC + 1)
                    self.PC = self.func_place[op_num1]['place'] + 1
                    continue
                elif op == 'call' and op_num1 == 'write':
                    stack_func.append(self.now_func)
                    self.now_func = 'write'
                    stack_pc.append(self.PC + 1)
                    write(stack_para[0])
                    del stack_para[0]
                    self.PC = stack_pc[-1]
                    stack_pc.pop()
                    self.now_func = stack_func[-1]
                    stack_func.pop()
                    continue
                elif op == 'call' and op_num1 == 'read':
                    return_T.append(res)
                    sys.stdin.flush()
                    s = input('请输入:')
                    self.temp_T[return_T[-1]] = s
                    return_T.pop()
                elif op == 'ret':
                    if self.now_func != 'main':
                        if op_num1:
                            self.temp_T[return_T[-1]] = self.get_value(op_num1, 1)
                            return_T.pop()
                            self.PC = stack_pc[-1]
                            stack_pc.pop()
                        else:
                            self.PC = stack_pc[-1]
                            stack_pc.pop()
                        self.now_func = stack_func[-1]
                        stack_func.pop()
                        if 'all' in self.ident_all:
                            self.ident_all['all'] = self.now_ident['all']
                        self.now_ident = stack_ident[-1]
                        if 'all' in self.ident_all:
                            self.now_ident['all'] = self.ident_all['all']
                        stack_ident.pop()
                    else:
                        if not op_num1:
                            op_num1 = 0
                        self.exit_code = op_num1
                        self.PC += 1
                    continue
                self.PC += 1
        except Exception as e:
            print('程序异常退出:\n' + str(e))
        finally:
            b = time.time()
            print('用时{}s'.format(b-a))
