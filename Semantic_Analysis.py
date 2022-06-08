from Semantic_Identity import *


class Semantic:
    def __init__(self):
        self.const_table = [[]]  # 常量
        self.change_table = [[]]  # 变量
        self.ident_all = {}
        self.func_message = {'num': 3, 'main': 4, 'main_have': 0}  # 函数信息
        self.func_table = {1: {'name': 'read', 'type': 'input', 'para': []},
                           2: {'name': 'write', 'type': 'void', 'para': [{'type': 'output', 'name': 'out'}]}}  # 函数表
        self.temp_code = []  # 中间代码
        self.temp_T = 0  # 中间变量序号
        self.error_code = load('./Data/semantic_error.json')  # 错误代码
        self.error = ''  # 错误
        self.error_num = 0  # 错误数量
        self.have_called = {}  # 已经调用过的只声明了而没有定义

    def error_deal(self, token, i, code):
        if code in ['601', '602', '603', '604', '605', '606', '607', '608', '612', '613', '614', '619', '621', '622',
                    '623', '624']:
            t = 'SemanticError ' + code + '(line: ' + str(token[2]) + ', col: ' + str(token[3]) + '): '
            if code == '612':
                t += 'identifier '
            t += "'"
            self.error += t + token[1] + self.error_code[code]
        elif code == '609':
            line = '(line: ' + str(token[2]) + ', col: ' + str(token[3]) + '): '
            t = 'SemanticError ' + code + line + 'function \'' + token[1] + '\': parameter ' + str(i + 1)
        elif code != '618':
            line = '(line: ' + str(token[i][2]) + ', col: '
            t = 'SemanticError ' + code + line + str(token[i][3]) + '): '
        if code in ['600', '609']:
            self.error += t + self.error_code[code]
        elif code in ['610', '611']:
            self.error += t + self.error_code[code] + token[i][1] + "'\n"
        elif code == '618':
            t_error = 'SemanticError 618' + '(line: ' + str(token[2]) + ', col: ' + str(
                token[3]) + '): '
            message = "'" + i + "' not support factor's type is '" + token[0] + "'\n"
            self.error += t_error + message
        self.error_num += 1

    # =赋值后修改初始化状态
    def fix_init_state(self, name):
        i = len(self.change_table) - 1
        while i >= 0:
            if len(self.change_table) > i:
                for j in range(len(self.change_table[i])):
                    if self.change_table[i][j]['name'] == name:
                        self.change_table[i][j]['if_init'] = 1
                        return 'change'
            if len(self.const_table) > i:
                for j in range(len(self.const_table[i])):
                    if self.const_table[i][j]['name'] == name:
                        return 'const'
            i -= 1

    # 在作用域内查找
    def identity_can_use(self, name, func_field):
        while func_field >= 0:
            identities = self.change_table[func_field]
            for identity in identities:
                if identity['name'] == name:
                    return 1, identity['type'], identity['if_init']
            identities = self.const_table[func_field]
            for identity in identities:
                if identity['name'] == name:
                    return 1, identity['type'], 'const'
            func_field -= 1
        return 0, 'NULL', '0'

    # 定义时判断是否变量定义
    def identity_can_define(self, name, func_field):
        identities = self.change_table[func_field]
        for identity in identities:
            if identity['name'] == name:
                return 1
        identities = self.const_table[func_field]
        for identity in identities:
            if identity['name'] == name:
                return 1
        return 0

    # 加入变量
    def add_change(self, one, now_func, func_field, t):
        if func_field != 0:
            now_func = now_func[1]
        else:
            now_func = 'all'
        judge = self.identity_can_define(one[0][1], func_field)
        if not judge:
            self.change_table[func_field].append(t)
            name = one[0][1]
            x = {func_field: t['value'], 'type': t['type']}
            if now_func not in self.ident_all:
                self.ident_all[now_func] = [{name: [x]}]
            else:
                i = 0
                n = len(self.ident_all[now_func])
                while i < n:
                    if name in self.ident_all[now_func][i]:
                        self.ident_all[now_func][i][name].append(x)
                        break
                    i += 1
                if i >= n:
                    self.ident_all[now_func].append({name: [x]})
        else:
            self.error_deal(one, 0, '610')

    # 变量定义语义分析
    def change_define(self, define_type, token, value, value_type, now_func, func_field):
        if not value:
            t = {'name': token[0][1], 'type': define_type, 'value': '', 'if_init': 0}
            self.add_change(token, now_func, func_field, t)
        else:
            if value_type == 'input':
                value_type = define_type
            if define_type == value_type or (
                    define_type in ['double', 'float'] and value_type not in ['char', 'string', 'double']):
                if func_field != 0:
                    value = ''
                t = {'name': token[0][1], 'type': define_type, 'value': value, 'if_init': 1}
                self.add_change(token, now_func, func_field, t)
            else:
                t_error = 'SemanticError 617' + '(line: ' + str(token[0][2]) + ', col: ' + str(
                    token[0][3]) + '): '
                message = "not use '" + define_type + "' = '" + value_type + "'\n"
                self.error += t_error + message
                self.error_num += 1

    # 常量定义语义分析
    def const_define(self, token, func_field, now_func):
        """
        :param token: 符号串(int name value)
        :param func_field: 作用域
        :return:
        """
        if func_field != 0:
            now_func = now_func[1]
        else:
            now_func = 'all'
        len_t = len(token)  # token串长度
        define_type = token[0][1]  # 定义的类型
        for i in range(1, len_t - 1, 2):
            name = token[i][1]  # 定义的变量名
            value_type = token[i + 1][0]  # 定义值的类型
            value = token[i + 1][1]  # 定义的值
            if func_field != 0:
                value = ''
            t = {'name': name, 'type': code_value[value_type], 'value': value}  # 一个静态变量
            if name == 'main':  # 变量名不能用main
                self.error_deal(token, i, '600')
            # 赋值类型限制
            elif define_type == code_value[value_type] or (
                    define_type in ['double', 'float'] and code_value[value_type] not in ['char', 'string', 'double']):
                judge = self.identity_can_define(name, func_field)
                if not judge:
                    self.const_table[func_field].append(t)
                    x = {func_field: value, 'type': code_value[value_type]}
                    if now_func not in self.ident_all:
                        self.ident_all[now_func] = [{name: [x]}]
                    else:
                        i = 0
                        n = len(self.ident_all[now_func])
                        while i < n:
                            if name in self.ident_all[now_func][i]:
                                self.ident_all[now_func][i][name].append(x)
                                break
                            i += 1
                        if i >= n:
                            self.ident_all[now_func].append({name: [x]})
                else:
                    self.error_deal(token, i, '610')
            else:
                t_error = 'SemanticError 617' + '(line: ' + str(token[i][2]) + ', col: ' + str(
                    token[i][3]) + '): '
                message = "not use '" + define_type + "' = '" + code_value[value_type] + "'\n"
                self.error += t_error + message
                self.error_num += 1

    # 函数定义分析
    def define_func(self, dit, func_filed):
        if dit['name'] == 'main':  # main函数的定义
            if self.func_message['main_have'] == 0:  # 没被定义过
                # 记录main函数的次序用于检验是否定义或者调用是否有效
                self.func_message['main'] = self.func_message['num']
                t = self.func_message['num']
                self.func_table[t] = dit  # 记录main函数的定义信息
                del self.func_table[t]['token']  # 删除帮助记录错误的信息
                self.func_message['num'] += 1  # 序号+1
                self.func_message['main_have'] = 1  # main函数已经定义
            else:  # 重复定义报错
                self.error_deal(dit['token'], 0, '601')
        else:
            judge = 1
            for i in self.func_table:  # 依次全部访问完毕
                j_name = self.func_table[i]['name']
                if j_name == dit['name']:
                    if 'declare' not in self.func_table[i]:  # 不是函数声明
                        self.error_deal(dit['token'], 0, '601')  # 重复定义的错误
                        judge = 0  # 有错误不添加
                        break
                    else:  # 先前的声明
                        judge = 1
                        dit_func_t = dit['type']  # 函数类型
                        dit_func_p = dit['para']  # 函数的参数
                        func_type = self.func_table[i]['type']  # 声明的函数类型
                        func_p = self.func_table[i]['para']  # 声明的函数参数类型
                        if dit_func_t != func_type:  # 函数声明与定义的类型不同
                            self.error_deal(dit['token'], 0, '606')
                            judge = 0
                        if len(func_p) > len(dit_func_p):  # 定义参数给少
                            self.error_deal(dit['token'], 0, '607')
                            judge = 0
                        elif len(func_p) < len(dit_func_p):  # 定义参数给多
                            self.error_deal(dit['token'], 0, '608')
                            judge = 0
                        else:
                            j = 0
                            len_t = len(func_p)
                            while j < len_t:  # 定义的参数数量相同
                                if dit_func_p[j]['type'] != func_p[j]['type']:  # 类型不同
                                    self.error_deal(dit['token'], j, '609')
                                    judge = 0
                                j += 1
                        if judge:
                            now_func = dit['name']
                            self.ident_all[now_func] = []
                            for p in dit_func_p:
                                t = {'name': p['name'], 'type': p['type'], 'value': '', 'if_init': 1}
                                self.change_table[func_filed].append(t)
                                x = {1: '', 'type': p['type']}
                                if now_func not in self.ident_all:
                                    self.ident_all[now_func] = [{p['name']: [x]}]
                                else:
                                    self.ident_all[now_func].append({p['name']: [x]})
                            self.func_table[i] = dit  # 定义覆盖信息
                            del self.func_table[i]['token']  # 删除用于记录错误的串
                        return
            if judge:
                t = self.func_message['num']
                self.func_table[t] = dit
                dit_func_p = dit['para']
                for p in dit_func_p:
                    tx = {'name': p['name'], 'type': p['type'], 'value': '', 'if_init': 1}
                    self.change_table[func_filed].append(tx)
                del self.func_table[t]['token']
                self.func_message['num'] += 1
                if not self.func_message['main_have']:  # main函数已经定义不用再变化
                    self.func_message['main'] += 1

    # 函数声明分析
    def declare_func(self, dit):
        if dit['name'] == 'main':  # 主函数不用声明直接定义
            self.error_deal(dit['token'], 0, '604')
        else:
            if self.func_message['num'] < self.func_message['main']:  # 保证声明要在主函数前面
                num = self.func_message['num']  # 当前的函数序号
                self.func_table[num] = dit  # 当前序号记录
                self.func_message['num'] += 1  # 加1
                self.func_message['main'] += 1  # 加1
            else:
                self.error_deal(dit['token'], 0, '605')  # 主函数之后再申明报错

    # 函数调用分析及生成中间代码
    def func_call(self, token, where, func_field):
        code = []
        return_value = ''  # 返回值为空的四元式
        f_name = token[0][1]  # 函数名
        found = 0  # 找到标志
        m = 1
        for i in self.func_table:  # 在函数表中查找
            name = self.func_table[i]['name']
            if name == f_name:  # 有
                found = i  # 置找到的位置
                break
        if found:  # 函数从1开始的，没有找到为0
            func_type = self.func_table[found]['type']  # 函数类型
            if func_type == 'void':  # 为空
                if where != 'call_func':  # 不只是单独的函数调用
                    self.error_deal(token[0], 0, '602')
                    return []
                else:
                    t = (func_type, '', token[0][2], token[0][3])
            else:
                temp_num = self.get_tempT()  # 获得中间变量
                t = (func_type, temp_num, token[0][2], token[0][3])  # 返回四元组
                return_value = temp_num
        else:
            # 函数没有定义
            self.error_deal(token[0], 0, '603')
            return []
        # 开始记录参数
        func_p = self.func_table[found]['para']
        para = func_para(token)
        if len(para) < len(func_p):
            self.error_deal(token[0], 0, '613')
            m = 0
        if len(para) > len(func_p):
            self.error_deal(token[0], 0, '614')
            m = 0
        if len(func_p) == 0:
            self.temp_code.append(('call', f_name, '', return_value, func_field))
            if f_name in self.have_called:
                self.have_called[f_name].append(token[0])
            else:
                self.have_called[f_name] = [token[0]]
        else:
            i = 0
            while i < len(para):
                fpt = func_p[i]['type']
                if len(para[i]) == 1:
                    one = para[i][0]
                    if one[0] == '086':
                        re, ty, if_init = self.identity_can_use(one[1], func_field)
                        if re:  # 是定义了的
                            if if_init != 1 and if_init != 'const':
                                self.error_deal(one, 0, '612')  # 没有初始化
                                m = 0
                            if ty == fpt or (fpt in ['double', 'float'] and ty in ['int', 'float']) or fpt == 'output':
                                code.append(('para', one[1], '', '', func_field))
                            else:  # 参数类型不匹配
                                t_error = 'SemanticError 615' + '(line: ' + str(one[2]) + ', col: ' + str(
                                    one[3]) + '): '
                                message = 'parameter need \'' + fpt + "', not provide '" + ty + "'\n"
                                self.error += t_error + message
                                self.error_num += 1
                                m = 0
                        else:  # 参数没有定义
                            self.error_deal(para[i], 0, '611')
                            m = 0
                    else:
                        ty = code_value[one[0]]
                        if ty == fpt or (fpt in ['double', 'float'] and ty in ['int', 'float']) or fpt == 'output':
                            one = get_num(one)
                            code.append(('para', one[1], '', '', func_field))
                        else:  # 参数类型不匹配
                            t_error = 'SemanticError 615' + '(line: ' + str(one[2]) + ', col: ' + str(
                                one[3]) + '): '
                            message = 'parameter need \'' + fpt + "', not provide '" + ty + "'\n"
                            self.error += t_error + message
                            self.error_num += 1
                            m = 0
                else:
                    ty_p = self.analysis_expression(para[i], 'others', func_field)
                    if not ty_p:
                        m = 0
                        i += 1
                        continue
                    if ty_p[0] in value_t or ty_p[0] == 'input':
                        if ty_p[0] == fpt or (fpt in ['double', 'float'] and ty_p[0] in ['int', 'float']) or ty_p[
                            0] == 'input' or fpt == 'output':
                            code.append(('para', ty_p[1], '', '', func_field))
                        else:
                            t_error = 'SemanticError 615' + '(line: ' + str(ty_p[2]) + ', col: ' + str(
                                ty_p[3]) + '): '
                            message = 'parameter need \'' + fpt + "', not provide '" + ty_p[0] + "'\n"
                            self.error += t_error + message
                            self.error_num += 1
                            m = 0
                i += 1
            if not m:
                return []
            for i in code:
                self.temp_code.append(i)
            self.temp_code.append(('call', f_name, '', return_value, func_field))
            if f_name in self.have_called:
                self.have_called[f_name].append(token[0])
            else:
                self.have_called[f_name] = [token[0]]
        return t

    def get_tempT(self):
        while 1:
            temp_num = 'T' + str(self.temp_T)
            if temp_num not in have_d:
                self.temp_T += 1
                return temp_num
            else:
                self.temp_T += 1

    # 生成表达式的中间代码
    def trans_exp_code(self, token, func_field):
        stack = []
        zi_zeng = {}
        len_t = len(token)
        i = 0
        while i < len_t:
            t = token[i][1]
            if t in priority:
                if t == '++' or t == '--':
                    op = t[0]
                    op_num1 = stack[-1]
                    stack.pop()
                    if op_num1[0] not in ['string', 'char']:
                        if token[i][3] < op_num1[3]:  # ++在前先加后进行其他操作
                            temp_num = self.get_tempT()
                            self.temp_code.append((op, op_num1[1], 1, temp_num, func_field))
                            self.temp_code.append(('=', temp_num, '', op_num1[1], func_field))
                            stack.append(op_num1)
                        else:
                            stack.append(op_num1)
                            if op_num1[1] in zi_zeng:
                                if op == '-':
                                    zi_zeng[op_num1[1]] -= 1
                                else:
                                    zi_zeng[op_num1[1]] += 1
                            else:
                                if op == '-':
                                    zi_zeng[op_num1[1]] = -1
                                else:
                                    zi_zeng[op_num1[1]] = 1
                    else:  # 错误 字符不能自增
                        t_error = 'SemanticError 616' + '(line: ' + str(token[i][2]) + ', col: ' + str(
                            token[i][3]) + '): '
                        message = "'++' or '--' need num's identifier"
                        self.error += t_error + message
                        self.error_num += 1
                        return []
                elif t == '=':  # 赋值
                    op_num2 = stack[-1]  # 值
                    type1 = op_num2[0]
                    stack.pop()
                    op_num1 = stack[-1]  # 变量
                    type2 = op_num1[0]
                    if type1 == 'input':
                        type1 = type2
                    stack.pop()
                    judge = self.identity_can_use(op_num1[1], func_field)
                    if judge[2] == 'const':
                        self.error_deal(op_num1, 0, '624')
                        return []
                    self.fix_init_state(op_num1[1])
                    if type1 == type2 or (type1 == ['int', 'float'] and type2 in ['float', 'double']):  # 可以赋值
                        self.temp_code.append(('=', op_num2[1], '', op_num1[1], func_field))
                        stack.append(op_num1)
                    else:  # 不能赋值
                        t_error = 'SemanticError 617' + '(line: ' + str(op_num1[2]) + ', col: ' + str(
                            op_num1[3]) + '): '
                        message = "not use '" + type2 + "' = '" + type1 + "'\n"
                        self.error += t_error + message
                        self.error_num += 1
                        return []
                elif t in fu_zhi2:  # 两步 赋值
                    op1 = t[0:-1]
                    op2 = '='
                    op_num2 = stack[-1]  # 2
                    stack.pop()
                    push_type = op_num2[0]
                    op_num1 = stack[-1]  # 1
                    stack.pop()
                    if op1 in cal:
                        if op_num2[0] not in ['string', 'char']:
                            if op_num1[0] not in ['string', 'char']:
                                if push_type in ['float', 'double'] and op_num1[0] == 'int':  # not int to push_type
                                    t_error = 'SemanticError 617' + '(line: ' + str(op_num1[2]) + ', col: ' + str(
                                        op_num1[3]) + '): '
                                    message = "not use '" + op_num1[0] + t + push_type + "'\n"
                                    self.error += t_error + message
                                    self.error_num += 1
                                    return []
                                else:
                                    temp_num = self.get_tempT()
                                    self.temp_code.append((op1, op_num1[1], op_num2[1], temp_num, func_field))
                                    self.temp_code.append((op2, temp_num, '', op_num1[1], func_field))
                                    stack.append(op_num1)
                            else:  # 操作数类型不支持
                                self.error_deal(op_num1, op1, '618')
                                return []
                        else:  # 操作数类型不支持
                            self.error_deal(op_num2, op1, '618')
                            return []
                    else:
                        if op_num2[0] == 'int':
                            if op_num1[0] == 'int':
                                temp_num = self.get_tempT()
                                self.temp_code.append((op1, op_num1[1], op_num2[1], temp_num, func_field))
                                self.temp_code.append((op2, temp_num, '', op_num1[1], func_field))
                                stack.append(op_num1)
                            else:
                                self.error_deal(op_num1, op1, '618')
                                return []
                        else:  # 操作数类型不支持
                            self.error_deal(op_num2, op1, '618')
                            return []
                elif t in cal:
                    op_num2 = stack[-1]  # 2
                    stack.pop()
                    push_type = op_num2[0]
                    op_num1 = stack[-1]  # 1
                    stack.pop()
                    if op_num1[0] in ['double', 'float']:
                        push_type = op_num1[0]
                    if op_num2[0] not in ['string', 'char']:
                        if op_num1[0] not in ['string', 'char']:
                            temp_num = self.get_tempT()
                            self.temp_code.append((t, op_num1[1], op_num2[1], temp_num, func_field))
                            stack.append((push_type, temp_num, 0, 0))  # 得出的结果入栈
                        else:  # 操作数类型不支持
                            self.error_deal(op_num1, t, '618')
                            return []
                    else:  # 操作数类型不支持
                        self.error_deal(op_num2, t, '618')
                        return []
                elif t in wei_op:
                    op_num2 = stack[-1]  # 2
                    stack.pop()
                    op_num1 = stack[-1]  # 1
                    stack.pop()
                    if op_num2[0] == 'int':
                        if op_num1[0] == 'int':
                            temp_num = self.get_tempT()
                            self.temp_code.append((t, op_num1[1], op_num2[1], temp_num, func_field))
                            stack.append(('int', temp_num, 0, 0))  # 得出的结果入栈
                        else:  # 操作数类型不支持
                            self.error_deal(op_num1, t, '618')
                            return []
                    else:  # 操作数类型不支持
                        self.error_deal(op_num2, t, '618')
                        return []
                elif t == '!':
                    op_num1 = stack[-1]
                    stack.pop()
                    t_t = self.get_tempT()
                    self.temp_code.append(('!', op_num1[1], '', t_t, func_field))
                    stack.append(('int', t_t, 0, 0))
                else:  # 关系运算符和逻辑运算符
                    op_num2 = stack[-1]  # 2
                    stack.pop()
                    op_num1 = stack[-1]  # 1
                    stack.pop()
                    if t in ['>', '<', '>=', '<=', '==']:
                        if op_num1[0] == 'string':
                            self.error_deal(op_num1, t, '618')
                            return []  # 字符串比较错误
                        if op_num2[0] == 'string':
                            self.error_deal(op_num1, t, '618')
                            return []
                    temp_num = self.get_tempT()
                    self.temp_code.append((t, op_num1[1], op_num2[1], temp_num, func_field))
                    stack.append(('int', temp_num, 0, 0))  # 得出的结果入栈
            else:  # 操作数入栈
                stack.append(token[i])
            i += 1
        type_t = stack[0]
        for i in zi_zeng:
            temp_num = self.get_tempT()
            self.temp_code.append(('+', i, zi_zeng[i], temp_num, func_field))
            self.temp_code.append(('=', temp_num, '', i, func_field))
        return type_t

    # 表达式分析
    def analysis_expression(self, token, where, func_field):
        len_t = len(token)
        op_stack = []  # 操作符
        reserved = []  # 转换后的后缀表达式
        i = 0
        judge = 1  # 判断有无定义错误的标志
        while i < len_t:
            if i + 1 < len_t:
                if token[i][0] == '086' and token[i + 1][1] == '(':  # 记录函数调用项
                    stack = [')']
                    tmp = [token[i], token[i + 1]]
                    i += 2
                    while 1:
                        if token[i][1] == '(':
                            stack.append(')')
                        elif token[i][1] == ')':
                            stack.pop()
                        tmp.append(token[i])
                        i += 1
                        if len(stack) == 0:
                            t = self.func_call(tmp, where, func_field)  # 处理函数调用
                            if not t:
                                judge = 0
                            reserved.append(t)
                            break
                    continue
            if i >= len_t:
                break
            if token[i][0] == '086':  # 操作数
                re, ty, if_init = self.identity_can_use(token[i][1], func_field)
                if re:  # 是定义了的
                    if i + 1 < len_t:
                        if token[i + 1][1] != '=' and (if_init != 1 and if_init != 'const'):
                            self.error_deal(token[i], 0, '612')  # 没有初始化
                            judge = 0
                    else:
                        if if_init != 1 and if_init != 'const':
                            self.error_deal(token[i], 0, '612')  # 没有初始化
                            judge = 0
                    # 记录类型，在之后的运算中判断是否可以运算
                    token[i] = (ty, token[i][1], token[i][2], token[i][3])
                    have_d.append(token[i][1])
                    reserved.append(token[i])  # 操作数直接后缀
                else:
                    self.error_deal(token, i, '611')
                    judge = 0
            elif token[i][0] in code_value:
                num_type = code_value[token[i][0]]
                # 记录类型，在之后的运算中判断是否可以运算
                # token[i] = get_num(token[i])
                token[i] = (num_type, token[i][1], token[i][2], token[i][3])
                reserved.append(token[i])  # 操作数直接后缀
            else:
                if not op_stack:  # 操作符栈为空，操作符入栈
                    op_stack.append(token[i])
                elif token[i][1] == '(':  # （直接入栈
                    op_stack.append(token[i])
                elif token[i][1] == ')':
                    while 1:  # )弹出至(包括(
                        if op_stack[-1][1] == '(':
                            op_stack.pop()
                            break
                        else:
                            reserved.append(op_stack[-1])
                            op_stack.pop()
                else:  # 弹出比输入字符优先级大或者等于的符号至小于输入符号或栈空为止
                    b = token[i][1]
                    while 1:
                        a = op_stack[-1][1]
                        if a in fu_zhi and b in fu_zhi:
                            break
                        if priority[a] <= priority[b]:
                            reserved.append(op_stack[-1])
                        if priority[a] > priority[b]:
                            break
                        op_stack.pop()
                        if not op_stack:
                            break
                    op_stack.append(token[i])  # 并加入当前输入符号
            i += 1
        if not judge:
            return []
        while op_stack:  # 在表达式读取完后弹出所有未弹出的符号
            reserved.append(op_stack[-1])
            op_stack.pop()
        exp_type = self.trans_exp_code(reserved, func_field)
        return exp_type

    def analysis_return(self, token, return_type):
        name = token
        for i in self.func_table:
            if self.func_table[i]['name'] == name:
                if return_type:
                    if self.func_table[i]['type'] == 'void':
                        self.error_deal(token, 0, '619')
                        return
                    if self.func_table[i]['type'] != return_type[0]:
                        t = 'SemanticError ' + '620' + '(line: ' + str(token[2]) + ', col: ' + str(token[3]) + '): '
                        self.error += t + "'" + name + self.error_code['620'] + self.func_table[i]['type'] + "'\n"
                        self.error_num += 1
                        return
                else:
                    if self.func_table[i]['type'] != 'void':
                        t = 'SemanticError ' + '620' + '(line: ' + str(token[2]) + ', col: ' + str(token[3]) + '): '
                        self.error += t + "'" + name + self.error_code['620'] + self.func_table[i]['type'] + "'\n"
                        self.error_num += 1
                        return

    def add_return(self, name):
        for i in self.func_table:
            if self.func_table[i]['name'] == name:
                ty = self.func_table[i]['type']
                if ty != 'void':
                    if self.temp_code[-1][0] != 'ret':
                        a = 0
                        if ty == 'int':
                            a = 0
                        if ty == 'double' or ty == 'float':
                            a = 0.0
                        if ty == 'char':
                            a = '"0"'
                        if ty == 'string':
                            a = '"hello"'
                        self.temp_code.append(('ret', add_end[ty], '', '', a))
                    return 1
        return 0

    def analysis_break_continue(self, token, content):
        if len(content) == 0:
            self.error_deal(token, 0, '621')
            return 0
        elif len(content) == 1:
            if content[0] == 'if' or content[0] == 'complex':
                self.error_deal(token, 0, '621')
                return 0
        else:
            a = content[-1]
            b = content[-2]
            if a == 'complex':
                self.error_deal(token, 0, '621')
                return 0
            if a == 'if' and b == 'if':
                self.error_deal(token, 0, '621')
                return 0
        return 1

    def judge_if_define(self):
        for i in self.have_called:
            for num in self.func_table:
                if i == self.func_table[num]['name']:
                    if 'declare' in self.func_table[num]:
                        for j in self.have_called[i]:
                            self.error_deal(j, 0, '622')

    def get_func_place(self, code):
        place = {}
        t = 0
        for i in self.func_table:
            if self.func_table[i]['name'] == 'write':
                t = self.func_table[i]['para']
                x = {'place': 0, 'para': t}
                place['write'] = x
            if self.func_table[i]['name'] == 'read':
                t = self.func_table[i]['para']
                x = {'place': 1, 'para': t}
                place['read'] = x
        for i in range(len(code)):
            name = code[i][1]
            if code[i][0] == 'fun':
                for j in self.func_table:
                    if self.func_table[j]['name'] == name:
                        t = self.func_table[j]['para']
                        break
                x = {'place': i, 'para': t}
                place[name] = x
            elif code[i][0] == 'sys':
                place['sys'] = i
        return place

# if __name__ == '__main__':
#     with open('./Debug/temp.txt', 'r', encoding='utf-8') as f:
#         toke = f.readlines()
#     for t_k in range(len(toke)):
#         toke[t_k] = toke[t_k].strip().split(' ')
#         toke[t_k] = tuple(toke[t_k])
#     toke.append(('000', '#', 0, 0))
#     op = Op_first(toke)
#     try:
#         if op.analysis():
#             del toke[-1]
#             test = Semantic()
#             test.analysis_expression(toke, 'others', 0)
#             for c in test.temp_code:
#                 print(c)
#         else:
#             print('error expression')
#     except:
#         print('error expression')
