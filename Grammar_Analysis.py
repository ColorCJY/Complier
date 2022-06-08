from op_first import *
from Semantic_Analysis import *


class Grammar:
    def __init__(self, token):
        self.code_error = load('Data//syntax_error.json')  # 错误代码
        self.token = token  # 符号串
        self.value_type = ['int', 'float', 'char', 'string', 'double']  # 定义变量类型
        self.value_type_code = ['081', '082', '083', '084', '085', '087', '088']  # 常数的类型码
        self.len_t = len(self.token)  # 符号串个数
        self.token_i = -1  # 下一个处理指针
        self.error = ''  # 错误
        self.return_type = ''  # 返回值类型
        self.semantic = Semantic()  # 语义分析
        self.error_num = 0  # 出现的错误数
        self.error_500 = 0  # 防止由于递归原因 500 错误会加入多次
        self.func_field = 0  # 空格数量
        self.now_func = 'all'  # 当前执行的函数
        self.message = ''  # 语法分析结果
        self.content = []  # 记录当前的控制语句
        self.loop_place = []  # 用于记录continue和break的跳转位置

    # 获取下一个符号串
    def GetNextToken(self):
        self.token_i += 1  # 指针+1
        if self.token_i >= self.len_t:
            return []
        token = self.token[self.token_i]  # 读取
        return token

    # 语法错误记录
    def SyntaxError(self, code):
        t = ''
        if code != '500':
            line = str(self.token[self.token_i][2])
            lie = str(self.token[self.token_i][3])
            t = 'SyntaxError ' + code + '(line: ' + line + ', col: ' + lie + '): '
        if code in ['502', '503', '504', '506', '527']:
            line = str(self.token[self.token_i - 1][2])
            lie = str(self.token[self.token_i - 1][3])
            t = 'SyntaxError ' + code + '(line: ' + line + ', col: ' + lie + '): '
            error = self.code_error[code] + "'" + self.token[self.token_i - 1][1] + '\' \n'
        elif code in ['518', '519', '520', '521', '522']:
            line = str(self.token[self.token_i][2])
            error = self.code_error[code] + '\n'
            t = 'SyntaxError ' + code + '(line: ' + line + '): '
            self.token_i -= 1
        elif code == '500':
            if self.error_500 == 0:
                self.error_num += 1
            self.error_500 = 1
            return
        elif code in ['513', '507']:
            error = self.code_error[code] + " '" + self.token[self.token_i][1] + '\' \n'
        else:
            error = self.code_error[code] + '\n'
        self.error_num += 1
        self.error += t + error

    # 处理预处理
    def analysis_pre(self):
        token = self.token[self.token_i]
        if token[1] == '#include':
            self.token_i += 1
            token = self.GetNextToken()
            if token[0] != '091':
                self.SyntaxError('001')
                self.token_i -= 1
            self.token_i += 1
            self.message += '\t' * self.func_field + '头文件引用\n'
        elif token[1] == "#define":
            token1 = self.GetNextToken()
            token2 = self.GetNextToken()
            if token1[0] != '086' and token2[0] not in self.value_type_code:
                self.SyntaxError('002')
            else:
                self.message += '\t' * self.func_field + '宏定义\n'

    # 入栈
    def push_stack(self):
        self.semantic.change_table.append([])
        self.semantic.const_table.append([])

    # 退栈
    def pop_stack(self):
        if self.semantic.const_table:
            self.semantic.const_table.pop()
        if self.semantic.change_table:
            self.semantic.change_table.pop()

    # 常量声明
    def analysis_const(self):  # 常量声明
        """
        const int x = 1;
        const int x = 1,y = 2;
        """
        # int...
        name = ''
        semantic_token = []
        self.message += '\t' * self.func_field + '常量声明语句: '
        token = self.GetNextToken()
        if not token:  # 符号串处理完
            self.SyntaxError('500')
            return
        if token[1] not in self.value_type:  # 是否有类型
            self.SyntaxError('505')
            self.token_i -= 1  # 错误回退
        else:
            semantic_token.append(token)  # 添加类型
            self.message += token[1] + ' '  # 语法分析的内容增加
        t = 0
        while 1:
            token = self.GetNextToken()
            if not token:  # 符号串处理完
                self.SyntaxError('500')
                return
            if token[0] != '086':
                if not t:  # 第一次循环
                    self.SyntaxError('509')  # 缺少标识符
                    self.token_i -= 1
                else:
                    if token[1] == '=':
                        self.SyntaxError('509')
                        self.token_i -= 1
                    else:
                        self.token_i -= 1
                        break
            else:
                semantic_token.append(token)  # 添加标识符
                name = token[1]
                self.message += '变量'
            token = self.GetNextToken()
            if not token:  # 符号串处理完
                self.SyntaxError('500')
                return
            if token[1] == '=':
                self.message += ' = '
                token = self.GetNextToken()
                if not token:  # 符号串处理完
                    self.SyntaxError('500')
                    return
                if token[0] not in self.value_type_code:
                    self.SyntaxError('510')
                    self.token_i -= 1
                else:
                    semantic_token.append(token)  # 添加常量值
                    self.semantic.temp_code.append(('=', token[1], '', name, self.func_field))
                    self.message += '值'
            token = self.GetNextToken()
            if not token:  # 符号串处理完
                self.SyntaxError('500')
                return
            if token[1] == ',':
                t += 1
                self.message += ', '
                continue
            break
        if token[1] != ';':
            self.SyntaxError('506')
            self.token_i -= 1
        else:
            self.semantic.const_define(semantic_token, self.func_field, self.now_func)  # 进行常量语义分析
            self.message += ';\n'

    # break,continue,return
    def analysis_other_control(self):
        token = self.token[self.token_i]
        if token[1] == 'return':
            self.message += '\t' * self.func_field + token[1] + ' '
            token = self.GetNextToken()
            if not token:  # 符号串处理完
                self.SyntaxError('500')
                return
            if token[1] == ';':
                self.semantic.analysis_return(self.now_func, '')
                self.message += ';\n'
                self.semantic.temp_code.append(('ret', '', '', '', self.func_field))
                return
            self.judge_expression()
            if not num_exp[1]:
                a = self.semantic.temp_code[-1][-2]
            else:
                a = num_exp[1]
            self.semantic.analysis_return(self.now_func, self.return_type)
            self.semantic.temp_code.append(('ret', a, '', '', self.func_field))
            return
        if token[1] == 'break':
            if self.semantic.analysis_break_continue(token, self.content):
                break_place = len(self.semantic.temp_code)
                self.semantic.temp_code.append(['j', '', '', '', self.func_field])
                self.loop_place[-1]['end'].append(break_place)
            token = self.GetNextToken()
            if not token:  # 符号串处理完
                self.SyntaxError('500')
                return
            if token[1] == ';':
                self.message += '\t' * self.func_field + 'break' + ';语句\n'
                return
            self.SyntaxError('506')
            self.token_i -= 1
            return
        if token[1] == 'continue':
            if self.semantic.analysis_break_continue(token, self.content):
                x = len(self.semantic.temp_code)
                if self.loop_place[-1]['start']:
                    start = self.loop_place[-1]['start']
                    self.semantic.temp_code.append(('j', '', '', start, self.func_field))
                else:
                    self.semantic.temp_code.append(['j', '', '', '', self.func_field])
                    self.loop_place[-1]['start'].append(x)
            token = self.GetNextToken()
            if not token:  # 符号串处理完
                self.SyntaxError('500')
                return
            if token[1] == ';':
                self.message += '\t' * self.func_field + 'continue' + ';语句\n'
                return
            self.SyntaxError('506')
            self.token_i -= 1
            return

    # 处理功能语句
    def analysis_sentence(self, where):
        token = self.GetNextToken()
        if not token:  # 符号串处理完
            self.SyntaxError('500')
            return
        if token[1] == 'const':
            self.analysis_const()
        elif token[1] in self.value_type:
            self.analysis_change_value('others')
        elif token[0] == '086':
            self.judge_expression()
        elif token[1] == 'for':
            self.analysis_for()
        elif token[1] == 'if':
            self.analysis_if()
        elif token[1] == 'while':
            self.analysis_while()
        elif token[1] == 'do':
            self.analysis_do()
        elif token[1] == '{':
            if where != 'for':
                self.func_field += 1
                self.push_stack()
            self.analysis_complex()
            if where != 'for':
                self.func_field -= 1
                self.pop_stack()
        elif token[1] in ['break', 'continue', 'return']:
            self.analysis_other_control()
        elif token[1] == '++':
            self.judge_expression()
        elif token[1] == '}':
            return
        else:
            self.SyntaxError('507')

    # 处理for语句
    def analysis_for(self):
        self.content.append('for')
        s = '('
        end = ('xxx', '#', '0', '0')
        token = self.GetNextToken()
        if not token:  # 符号串处理完
            self.SyntaxError('500')
            return
        if token[1] != '(':
            self.SyntaxError('502')
            self.token_i -= 1
        tmp = {1: [], 2: [], 3: []}  # 记录三个表达式
        index = 1  # ;个数
        token1 = self.GetNextToken()  # 因需要比较行数先读取一个
        if not token1:  # 符号串处理完
            self.SyntaxError('500')
            return
        n = self.token_i  # 记录此时的下标,用于分析for(int i=1;...)这种
        if token1[1] == ';':  # 第一个表达式可能为空
            tmp[index].append(end)
            index += 1
        else:
            tmp[index].append(token1)  # 不是;就是表达式符号
        line1 = token1[2]
        while 1:  # 循环记录
            token2 = self.GetNextToken()  # 读取下一个用作比较
            if not token2:  # 符号串处理完
                self.SyntaxError('500')
                return
            if token2[1] in ['(', ')']:
                s += token2[1]
            line2 = token2[2]  # 行数
            if token2[1] == ';':  # 之后遇到一个;表达式个数+1
                tmp[index].append(end)
                index += 1
            else:
                if line1 == line2:
                    if token2[1] == '{':
                        tmp[index][-1] = end
                        self.token_i -= 2
                        break
                    if index not in tmp:
                        tmp[index] = [token2]
                    else:
                        tmp[index].append(token2)
                else:
                    tmp[index][-1] = end
                    self.token_i -= 2
                    break
            line1 = line2
        if index == 1:  # 没有;
            self.SyntaxError('518')
            return
        if index == 2:  # 只有一个;
            self.SyntaxError('519')
            return
        if index > 3:
            self.SyntaxError('520')
            return
        t = is_valid(s)
        if t == 1:
            self.SyntaxError('522')
            return
        if t == 2:
            self.SyntaxError('521')
            return
        self.message += '\t' * self.func_field + 'for语句分析开始\n'
        self.message += '\t' * self.func_field + 'for('
        self.func_field += 1
        self.push_stack()
        start2 = 0  # 第二个表达式开始的地方
        end2 = 0  # 第二个表达式结束
        start3 = 0  # 第三个表达式
        false2 = 0  # 错误跳出的地方
        for index in tmp:  # 进行分析
            if tmp[index] and tmp[index][0] != end:
                if index == 1:
                    if tmp[index][0][1] in self.value_type:
                        t = self.token_i  # 记录此时的下标用于恢复
                        self.token_i = n  # 定义从int类型开始
                        self.analysis_change_value('for')  # 参数for表示为for状态的定义
                        start2 = len(self.semantic.temp_code)
                        self.message = self.message.strip('\n')
                        self.token_i = t  # 恢复之前的状态
                        continue
            self.analysis_expression(tmp[index], 'for')
            if index == 1:
                start2 = len(self.semantic.temp_code)
            if index == 2:
                if not num_exp[1]:
                    a = self.semantic.temp_code[-1][-2]
                else:
                    a = num_exp[1]
                    if not tmp[index] or tmp[index] == end:
                        a = '1'
                end2 = len(self.semantic.temp_code)
                self.semantic.temp_code.append(['jnz', a, '', '', self.func_field])
                false2 = end2 + 1
                self.semantic.temp_code.append(['j', '', '', '', self.func_field])
                start3 = len(self.semantic.temp_code)
            if index == 3:
                self.semantic.temp_code.append(('j', '', '', start2, self.func_field))
            if index != 3:
                self.message += ';'
            else:
                self.message += ')\n'
        self.semantic.temp_code[end2][3] = len(self.semantic.temp_code)
        self.semantic.temp_code[end2] = tuple(self.semantic.temp_code[end2])
        token = self.GetNextToken()
        if not token:  # 符号串处理完
            self.SyntaxError('500')
            return
        if token[1] != ')':  # 括号
            self.SyntaxError('503')
            self.token_i -= 1
        t = {'start': start3, 'end': []}
        self.loop_place.append(t)
        self.analysis_sentence('for')
        self.func_field -= 1
        self.pop_stack()
        self.message += '\t' * self.func_field + 'for语句分析结束\n'
        self.semantic.temp_code.append(('j', '', '', start3, self.func_field))
        false = len(self.semantic.temp_code)
        self.semantic.temp_code[false2][3] = false
        self.semantic.temp_code[false2] = tuple(self.semantic.temp_code[false2])
        for place in self.loop_place[-1]['end']:
            self.semantic.temp_code[place][3] = false
            self.semantic.temp_code[place] = tuple(self.semantic.temp_code[place])
        self.content.pop()
        self.loop_place.pop()

    # 处理if语句
    def analysis_if(self):
        self.content.append('if')
        self.message += '\t' * self.func_field + 'if语句分析开始\n'
        token = self.GetNextToken()
        if not token:  # 符号串处理完
            self.SyntaxError('500')
            return
        if token[1] != '(':
            self.SyntaxError('502')
            self.token_i -= 1
        token = self.GetNextToken()
        if not token:  # 符号串处理完
            self.SyntaxError('500')
            return
        if token[1] != ')':
            self.token_i -= 1
            self.message += '\t' * self.func_field + 'if('
            self.deal_expression('if')
            self.message += ')\n'
            if not num_exp[1]:
                a = self.semantic.temp_code[-1][-2]
            else:
                a = num_exp[1]
            num_exp[1] = ''
            true_jp = len(self.semantic.temp_code) + 2
            self.semantic.temp_code.append(('jnz', a, '', true_jp, self.func_field))
            false_jp = len(self.semantic.temp_code)
            self.semantic.temp_code.append(['j', '', '', '', self.func_field])
            token = self.GetNextToken()
            if not token:  # 符号串处理完
                self.SyntaxError('500')
                return
            if token[1] != '{':
                self.func_field += 1
                self.push_stack()
                self.token_i -= 1
                self.analysis_sentence('if')
                self.func_field -= 1
                self.pop_stack()
            else:
                self.token_i -= 1
                self.analysis_sentence('if')
            self.message += '\t' * self.func_field + 'if语句分析结束\n'
        else:
            self.SyntaxError('523')
            return
        self.content.pop()
        end_if = len(self.semantic.temp_code)
        self.semantic.temp_code.append(['j', '', '', '', self.func_field])
        false_num = len(self.semantic.temp_code)
        self.semantic.temp_code[false_jp][3] = false_num
        self.semantic.temp_code[false_jp] = tuple(self.semantic.temp_code[false_jp])
        token = self.GetNextToken()
        if not token:  # 符号串处理完
            self.SyntaxError('500')
            return
        if token[1] == 'else':
            self.content.append('if')
            self.message += '\t' * self.func_field + 'else语句分析开始\n'
            token = self.GetNextToken()
            if not token:  # 符号串处理完
                self.SyntaxError('500')
                return
            if token[1] != '{':
                self.func_field += 1
                self.push_stack()
                self.token_i -= 1
                self.analysis_sentence('if')
                self.func_field -= 1
                self.pop_stack()
            else:
                self.token_i -= 1
                self.analysis_sentence('if')
            self.content.pop()
            self.message += '\t' * self.func_field + 'else语句分析结束\n'
        else:
            self.token_i -= 1
        end_num = len(self.semantic.temp_code)
        self.semantic.temp_code[end_if][3] = end_num
        self.semantic.temp_code[end_if] = tuple(self.semantic.temp_code[end_if])

    # 处理while语句
    def analysis_while(self):
        self.content.append('while')
        token = self.GetNextToken()
        if not token:  # 符号串处理完
            self.SyntaxError('500')
            return
        if token[1] != '(':
            self.SyntaxError('502')
            self.token_i -= 1
        self.message += '\t' * self.func_field + 'while语句分析开始\n'
        token = self.GetNextToken()
        if not token:  # 符号串处理完
            self.SyntaxError('500')
            return
        start = len(self.semantic.temp_code)
        t = {'start': start, 'end': []}
        self.loop_place.append(t)
        if token[1] == ')':
            self.SyntaxError('523')
        else:
            self.token_i -= 1
            self.message += '\t' * self.func_field + 'while('
            self.deal_expression('while')
            self.message += ')\n'
        if not num_exp[1]:
            a = self.semantic.temp_code[-1][-2]
        else:
            a = num_exp[1]
        num_exp[1] = ''
        true_jp = len(self.semantic.temp_code) + 2
        self.semantic.temp_code.append(('jnz', a, '', true_jp, self.func_field))
        false_jp = len(self.semantic.temp_code)
        self.semantic.temp_code.append(['j', '', '', '', self.func_field])
        token = self.GetNextToken()
        if not token:  # 符号串处理完
            self.SyntaxError('500')
            return
        if token[1] != '{':
            self.func_field += 1
            self.push_stack()
            self.token_i -= 1
            self.analysis_sentence('while')
            self.func_field -= 1
            self.pop_stack()
        else:
            self.token_i -= 1
            self.analysis_sentence('while')
        self.message += '\t' * self.func_field + 'while语句分析结束\n'
        self.semantic.temp_code.append(('j', '', '', start, self.func_field))
        false_num = len(self.semantic.temp_code)
        self.semantic.temp_code[false_jp][3] = false_num
        self.semantic.temp_code[false_jp] = tuple(self.semantic.temp_code[false_jp])
        for place in self.loop_place[-1]['end']:
            self.semantic.temp_code[place][3] = false_num
            self.semantic.temp_code[place] = tuple(self.semantic.temp_code[place])
        self.content.pop()
        self.loop_place.pop()

    # 处理do_while语句
    def analysis_do(self):
        t = {'start': [], 'end': []}
        self.loop_place.append(t)
        self.content.append('do')
        token = self.GetNextToken()
        if not token:  # 符号串处理完
            self.SyntaxError('500')
            return
        start = len(self.semantic.temp_code)
        if token[1] != '{':
            self.SyntaxError('504')
            self.token_i -= 1
        self.message += '\t' * self.func_field + 'do_while语句分析开始\n'
        self.message += '\t' * self.func_field + 'do\n'
        self.token_i -= 1
        self.analysis_sentence('do')
        token = self.GetNextToken()
        if not token:  # 符号串处理完
            self.SyntaxError('500')
            return
        if token[1] != 'while':
            self.SyntaxError('512')
            return
        self.message += '\t' * self.func_field + 'while('
        token = self.GetNextToken()
        if not token:  # 符号串处理完
            self.SyntaxError('500')
            return
        if token[1] != '(':
            self.SyntaxError('502')
            self.token_i -= 1
        token = self.GetNextToken()
        do_start = len(self.semantic.temp_code)
        for place in self.loop_place[-1]['start']:
            self.semantic.temp_code[place][3] = do_start
            self.semantic.temp_code[place] = tuple(self.semantic.temp_code[place])
        if not token:  # 符号串处理完
            self.SyntaxError('500')
            return
        if token[1] == ')':
            self.SyntaxError('523')
        else:
            self.token_i -= 1
            self.deal_expression('do')
        if not num_exp[1]:
            a = self.semantic.temp_code[-1][-2]
        else:
            a = num_exp[1]
        self.semantic.temp_code.append(('jnz', a, '', start, self.func_field))
        false_jp = len(self.semantic.temp_code) + 1
        self.semantic.temp_code.append(('j', '', '', false_jp, self.func_field))
        for place in self.loop_place[-1]['end']:
            self.semantic.temp_code[place][3] = false_jp
            self.semantic.temp_code[place] = tuple(self.semantic.temp_code[place])
        token = self.GetNextToken()
        if not token:  # 符号串处理完
            self.SyntaxError('500')
            return
        if token[1] != ';':
            self.SyntaxError('506')
            self.token_i -= 1
        else:
            self.message += ');\n'
            self.message += '\t' * self.func_field + 'do_while语句分析结束\n'
        self.content.pop()
        self.loop_place.pop()

    # 函数定义参数
    def func_define_parameter(self, f_type, f_name, token):
        tmp = {'name': f_name, 'type': f_type, 'para': [], 'token': token}
        token = self.GetNextToken()  # 取下一个符号串
        if not token:  # 符号串处理完
            self.SyntaxError('500')
            return
        if token[1] != ')':
            while 1:
                one = {}
                if token[1] not in self.value_type:
                    self.SyntaxError('515')
                    self.token_i -= 1
                else:
                    one['type'] = token[1]
                token = self.GetNextToken()  # 取下一个符号串
                if not token:  # 符号串处理完
                    self.SyntaxError('500')
                    return
                if token[0] != '086':
                    self.SyntaxError('516')
                    self.token_i -= 1
                else:
                    one['name'] = token[1]
                token = self.GetNextToken()  # 取下一个符号串
                if not token:  # 符号串处理完
                    self.SyntaxError('500')
                    return
                if token[1] != ',':
                    if token[1] != ')':
                        self.SyntaxError('503')
                        self.token_i -= 1
                    else:
                        tmp['para'].append(one)
                        self.semantic.define_func(tmp, self.func_field + 1)
                    break
                else:
                    tmp['para'].append(one)
                token = self.GetNextToken()  # 取下一个符号串
                if not token:  # 符号串处理完
                    self.SyntaxError('500')
                    return
        else:
            self.semantic.define_func(tmp, self.func_field + 1)
        token = self.GetNextToken()  # 取下一个符号串
        if not token:  # 符号串处理完
            self.SyntaxError('500')
            return
        if token[1] != '{':
            self.SyntaxError('504')
            self.token_i -= 1

    # 函数定义
    def analysis_func_define(self):
        # 比较定义的函数
        token = self.token[self.token_i + 1]
        f_type = self.token[self.token_i][1]
        f_name = self.token[self.token_i + 1][1]
        self.now_func = self.token[self.token_i + 1]
        self.semantic.temp_code.append(('fun', f_name, '', '', self.func_field))
        self.token_i += 2  # 直接指向括号
        self.push_stack()
        self.func_define_parameter(f_type, f_name, token)
        self.message += '\t' * self.func_field + f_name + '函数分析开始\n'
        self.func_field += 1
        self.analysis_complex()
        self.func_field -= 1
        self.pop_stack()
        if f_name != 'main':
            t = self.semantic.add_return(f_name)
            if not t:
                self.semantic.temp_code.append(('end', '', '', '', self.func_field))
        else:
            self.semantic.temp_code.append(('sys', '', '', '', self.func_field))
        self.message += '\t' * self.func_field + f_name + '函数分析结束\n'

    # 函数声明参数
    def func_declare_parameter(self, f_type, f_name, token):
        # 需要记录声明的形参
        tmp = {'name': f_name, 'type': f_type, 'para': [], 'token': token, 'declare': 1}
        token = self.GetNextToken()  # 取下一个符号串
        if not token:  # 符号串处理完
            self.SyntaxError('500')
            return
        if token[1] != ')':
            while 1:
                one = {}
                if token[1] not in self.value_type:
                    self.SyntaxError('514')
                    self.token_i -= 1
                # 添加一个参数
                else:
                    one['type'] = token[1]
                    tmp['para'].append(one)
                token = self.GetNextToken()  # 取下一个符号串
                if not token:  # 符号串处理完
                    self.SyntaxError('500')
                    return
                if token[1] != ',':
                    if token[1] != ')':
                        if token[1] in self.value_type:
                            self.SyntaxError('527')
                            continue
                        else:
                            self.SyntaxError('503')
                            self.token_i -= 1
                    else:
                        dit = tmp
                        self.semantic.declare_func(dit)
                    break
                token = self.GetNextToken()  # 取下一个符号串
                if not token:  # 符号串处理完
                    self.SyntaxError('500')
                    return
        else:
            dit = tmp
            self.semantic.declare_func(dit)
        token = self.GetNextToken()  # 取下一个符号串
        if not token:  # 符号串处理完
            self.SyntaxError('500')
            return
        if token[1] != ';':
            self.SyntaxError('506')
            self.token_i -= 1
            return

    # 函数声明
    def analysis_func_declare(self):
        # 记录声明的函数
        token = self.token[self.token_i + 1]
        f_type = self.token[self.token_i][1]
        f_name = self.token[self.token_i + 1][1]
        self.token_i += 2  # 直接指向括号
        self.func_declare_parameter(f_type, f_name, token)
        self.message += '\t' * self.func_field + '声明' + f_name + '函数\n'

    # 判断是函数定义还是声明
    def judge_func(self):
        token = self.GetNextToken()
        if not token:  # 符号串处理完
            self.SyntaxError('500')
            return
        if token[1] == ')':
            token = self.GetNextToken()
            if not token:  # 符号串处理完
                self.SyntaxError('500')
                return
            if token[1] == ';':
                self.token_i -= 4
                self.analysis_func_declare()
            elif token[1] == '{':
                self.token_i -= 4
                self.analysis_func_define()
            else:
                self.token_i -= 4
                self.analysis_func_define()
            return

        elif token[1] in self.value_type:
            token = self.GetNextToken()
            if not token:  # 符号串处理完
                self.SyntaxError('500')
                return
            if token[1] == ',':
                self.token_i -= 4
                self.analysis_func_declare()
            elif token[1] == ')':
                self.token_i -= 4
                self.analysis_func_declare()
            elif token[0] == '086':
                self.token_i -= 4
                self.analysis_func_define()
            else:
                if token[1] in self.value_type:
                    self.token_i -= 4
                    self.analysis_func_declare()
            return

    # 处理变量声明
    def analysis_change_value(self, where):
        """
        int x; int x,y; int x=1,y;
        int x,y=1; int x=1,y=1;
        """
        define_type = self.token[self.token_i][1]
        semantic_token = []
        if where == 'for':
            self.message += '变量定义: '
        else:
            self.message += '\t' * self.func_field + '变量定义: '
        while 1:
            token = self.GetNextToken()
            if not token:  # 符号串处理完
                self.SyntaxError('500')
                return
            if token[0] != '086':
                self.SyntaxError('509')
                self.token_i -= 1
            else:
                semantic_token = [token]
                self.message += '变量'
            token = self.GetNextToken()
            if not token:  # 符号串处理完
                self.SyntaxError('500')
                return
            if token[1] == ';':
                self.semantic.change_define(define_type, semantic_token, '', '', self.now_func, self.func_field)
                self.message += ';\n'
                break
            elif token[1] == ',':
                self.semantic.change_define(define_type, semantic_token, '', '', self.now_func, self.func_field)
                self.message += ', '
                continue
            elif token[1] == '=':
                self.message += ' = '
                self.token_i -= 2
                self.deal_expression(define_type)
            else:
                self.SyntaxError('506')
                return
            token = self.GetNextToken()
            if not token:  # 符号串处理完
                self.SyntaxError('500')
                return
            if token[1] == ',':
                self.message += ', '
                continue
            elif token[1] == ';':
                self.message += ';\n'
                break
            else:
                self.SyntaxError('506')
                self.token_i -= 1
                break

    # 判断是函数还是变量
    def judge_func_identity(self):
        t = self.token[self.token_i]
        if t[1] == 'void':
            token = self.GetNextToken()
            if not token:  # 符号串处理完
                self.SyntaxError('500')
                return
            if token[0] != '086':
                self.SyntaxError('509')
                self.token_i -= 1
            token = self.GetNextToken()
            if not token:  # 符号串处理完
                self.SyntaxError('500')
                return
            if token[1] == '(':
                self.judge_func()
            else:
                self.SyntaxError('526')
                self.token_i -= 2
                self.analysis_change_value('other')
            return
        token = self.GetNextToken()
        if not token:  # 符号串处理完
            self.SyntaxError('500')
            return
        if token[0] != '086':
            self.SyntaxError('509')
            self.token_i -= 1
        token = self.GetNextToken()
        if not token:  # 符号串处理完
            self.SyntaxError('500')
            return
        if token[1] == '(':
            self.judge_func()
        else:
            self.token_i -= 2
            self.analysis_change_value('others')

    # 分析表达式
    def analysis_expression(self, token, where):
        code = '524'
        num_exp[1] = ''
        line = str(token[0][2])
        lie = str(token[0][3])
        e = 'SyntaxError ' + code + '(line: ' + line + ', col: ' + lie + '): '
        error = self.code_error[code] + '\n'
        token = fix_num(token)
        ex = Op_first(token)
        if not token:
            self.error_num += 1
            self.error += e + error
            return
        if len(token[0]) == 3:
            line = str(token[0][1])
            lie = str(token[0][2])
            e = 'SyntaxError 525' + '(line: ' + line + ', col: ' + lie + '): \''
            error = token[0][0] + self.code_error['525'] + '\n'
            self.error_num += 1
            self.error += e + error
            return
            # 由于使用算符优先实现表达式的分析可能会出现输入的不支持的算符，需要捕捉异常报错
        try:
            t = ex.analysis()
            if not t:
                self.error_num += 1
                self.error += e + error
            else:
                tmp = []
                for j in range(len(token) - 1):
                    tmp.append(token[j])
                if len(tmp) == 1:
                    num_exp[1] = tmp[0][1]
                if where in self.value_type:  # 变量定义
                    self.message += '值'
                    values = tmp[2:]
                    value = ''
                    if self.func_field == 0:
                        if len(values) == 1:
                            if values[0][0] not in code_ju:
                                self.semantic.error_deal(tmp[0], 0, '623')
                                return
                        else:
                            self.semantic.error_deal(tmp[0], 0, '623')
                            return
                    for v in values:
                        value += v[1]
                    ty = self.semantic.analysis_expression(values, t, self.func_field)  # 分析表达式
                    if not ty:
                        self.semantic.change_define(where, tmp[:-1], '', '', self.now_func, self.func_field)
                    else:
                        self.semantic.temp_code.append(('=', ty[1], '', tmp[0][1], self.func_field))
                        self.semantic.change_define(where, tmp[:-1], value, ty[0], self.now_func, self.func_field)
                else:  # 其他情况
                    self.return_type = self.semantic.analysis_expression(tmp, t, self.func_field)  # 分析表达式
                    self.message += exp_code[t]
        except:
            self.error_num += 1
            self.error += e + error

    # 处理表达式token串
    def deal_expression(self, where):
        jt = 1
        tmp = []
        end = ('xxx', '#', 0, 0)
        if where in ['while', 'if', 'do']:
            s = '('
        else:
            s = ''
        line1 = self.token[self.token_i][2]
        if where == 'do':
            while 1:
                token1 = self.GetNextToken()
                if token1[1] in ['(', ')']:
                    s += token1[1]
                if not token1:  # 符号串处理完
                    self.SyntaxError('500')
                    return
                if line1 != token1[2]:
                    t = is_valid(s)
                    if t == 1:
                        self.SyntaxError('522')
                    elif t == 2:
                        self.SyntaxError('521')
                    else:
                        tmp[-1] = end
                        self.analysis_expression(tmp, where)
                        self.token_i -= 1
                    return
                if token1[1] == ';':
                    t = is_valid(s)
                    if t == 1:
                        self.SyntaxError('522')
                    elif t == 2:
                        self.SyntaxError('521')
                    else:
                        tmp[-1] = end
                        self.analysis_expression(tmp, where)
                        self.token_i -= 1
                    return
                tmp.append(token1)
        token1 = self.GetNextToken()
        if not token1:  # 符号串处理完
            self.SyntaxError('500')
            return
        if token1[1] in ['(', ')']:
            s += token1[1]
        line1 = token1[2]
        tmp.append(token1)
        stack = []
        while self.token_i < self.len_t:
            token2 = self.GetNextToken()
            if not token2:  # 符号串处理完
                self.SyntaxError('500')
                return
            if token1[0] == '086' and token2[1] == '(':
                jt = 0
            line2 = token2[2]
            if token2[1] in ['(', ')']:
                s += token2[1]
            if where == 'if' or where == 'while':  # 是if的表达式或while
                if line1 == line2:  # 在同一行
                    if token2[1] == '{' or (token1[1] == ')' and token2[0] == '086'):  # 有括号 或者为if(...) x=1;
                        t = is_valid(s)
                        if t == 1:
                            self.SyntaxError('522')
                        elif t == 2:
                            self.SyntaxError('521')
                        else:
                            tmp[-1] = end  # 结束标志
                            self.analysis_expression(tmp, where)  # 表达式分析
                            self.token_i -= 1
                        return
                    tmp.append(token2)
                else:
                    t = is_valid(s)
                    if t == 1:
                        self.SyntaxError('522')
                    elif t == 2:
                        self.SyntaxError('521')
                    else:
                        tmp[-1] = end
                        self.analysis_expression(tmp, where)  # 表达式分析
                        self.token_i -= 1
                    return
                token1 = token2
                continue
            else:
                if token2[1] == '(':
                    stack.append(')')
                if token2[1] == ')':
                    stack.pop()
                if not stack:
                    jt = 1
                if line1 == line2:
                    if token2[1] == ';' or (where in self.value_type and token2[1] == ',' and jt):
                        m = is_valid(s)
                        if m == 1:
                            self.SyntaxError('522')
                        elif m == 2:
                            self.SyntaxError('521')
                        else:
                            tmp.append(end)
                            self.analysis_expression(tmp, where)
                            self.token_i -= 1
                        return
                    p = token1[0] == '086' or token1[0] in self.value_type_code
                    t = token2[0] == '086' or token2[0] in self.value_type_code
                    if t and p:
                        m = is_valid(s)
                        if m == 1:
                            self.SyntaxError('522')
                        elif m == 2:
                            self.SyntaxError('521')
                        else:
                            tmp[-1] = end
                            self.analysis_expression(tmp, where)  # 表达式分析
                            self.token_i -= 1
                        return
                    if token1[1] == ')' and token2[1] == '(':
                        m = is_valid(s)
                        if m == 1:
                            self.SyntaxError('522')
                        elif m == 2:
                            self.SyntaxError('521')
                        else:
                            tmp[-1] = end
                            self.analysis_expression(tmp, where)  # 表达式分析
                            self.token_i -= 1
                        return
                    tmp.append(token2)
                else:
                    m = is_valid(s)
                    if m == 1:
                        self.SyntaxError('522')
                    elif m == 2:
                        self.SyntaxError('521')
                    else:
                        tmp.append(end)
                        self.analysis_expression(tmp, where)  # 表达式分析
                        self.token_i -= 1
                    return
                token1 = token2

    # 处理一条语句
    def judge_expression(self):
        self.token_i -= 1
        self.message += '\t' * self.func_field
        self.deal_expression('sentence')
        token = self.GetNextToken()
        if not token:  # 符号串处理完
            self.SyntaxError('500')
            return
        if token[1] != ';':
            self.SyntaxError('506')
            self.token_i -= 1
        else:
            self.message += ';\n'

    # 处理复合语句
    def analysis_complex(self):
        while 1:
            token = self.GetNextToken()
            if not token:  # 符号串处理完
                self.SyntaxError('500')
                return
            if token[1] == 'const':
                self.analysis_const()
                continue
            if token[1] in self.value_type:
                self.analysis_change_value('others')
                continue
            if token[0] == '086':
                self.judge_expression()
                continue
            if token[1] == 'for':
                self.analysis_for()
                continue
            if token[1] == 'if':
                self.analysis_if()
                continue
            if token[1] == 'while':
                self.analysis_while()
                continue
            if token[1] == 'do':
                self.analysis_do()
                continue
            if token[1] == '{':
                self.func_field += 1
                self.push_stack()
                self.content.append('complex')
                self.analysis_complex()
                self.content.pop()
                self.func_field -= 1
                self.pop_stack()
                continue
            if token[1] in ['break', 'continue', 'return']:
                self.analysis_other_control()
                continue
            if token[1] == '++':
                self.judge_expression()
                continue
            if token[1] == '}':
                return
            else:
                self.SyntaxError('507')
                continue

    # 主程序
    def analysis_main(self):
        self.message += '语法分析开始...\n'
        func_type = self.value_type + ['void']
        if self.len_t < 6:  # 小于6个错误
            self.SyntaxError('000')
            return
        token = self.GetNextToken()  # 取下一个符号串
        # 预处理全部在前
        while token[1] in ['#include', '#define']:
            self.analysis_pre()
            token = self.GetNextToken()  # 取下一个符号串
            if not token:  # 符号串处理完
                self.SyntaxError('501')
                return
        while self.token_i < self.len_t:
            if token[1] in func_type:
                self.judge_func_identity()
            elif token[1] == 'const':
                self.analysis_const()
            else:
                while token[1] not in func_type:
                    self.SyntaxError('507')
                    break
            token = self.GetNextToken()  # 取下一个符号串
        if self.error_500:
            code = '500'
            line = str(self.token[self.len_t - 1][2] + 1)
            lie = '1'
            t = 'SyntaxError ' + code + '(line: ' + line + ', col: ' + lie + '): ' + self.code_error[code]
            self.error += t
        self.message += '语法分析结束...\n'
        if self.semantic.func_message['main_have'] == 0:
            line = int(self.token[-1][2]) + 1
            t = 'SemanticError ' + '501' + '(line: ' + str(line) + ', col: ' + '1' + '): '
            self.semantic.error += t + "program misses 'main' function\n"
            self.semantic.error_num += 1
        self.semantic.judge_if_define()

