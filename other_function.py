import json


def load(file):  # 加载文件
    with open(file, 'r') as f:
        return json.load(f)


def save(file, content):  # 保存文件
    with open(file, 'w') as f:
        json.dump(content, f, indent=2)


def is_valid(s):  # 判断扩号是否匹配
    stack = []
    for c in s:
        if '(' == c:
            stack.append(')')
        elif len(stack) == 0 or stack.pop() != c:
            return 2  # 缺少(
    if len(stack) == 0:
        return 0
    else:
        return 1  # 缺少)


def get_grammar(file):
    """
    文法文件:A->C|D对应存储A:A|B，按行分割，有提示行，空行
    :param file: 文件名,读取UTF-8的文件
    :return: grammar: 文法集,vn: 非终结符, vt: 终结符
    """
    grammar = {}
    with open(file, encoding='UTF-8') as f:
        s = f.read()
        s = s.split('\n')
        t = []
        for i in range(len(s)):
            if s[i] and '@' not in s[i]:
                t.append(s[i].split(':'))
        for i in t:
            m = i[1].split('|')
            if i[0] in grammar:
                grammar[i[0]] += m
            else:
                grammar[i[0]] = m
        for i in grammar:
            for j in range(len(grammar[i])):
                grammar[i][j] = grammar[i][j].replace('\\', '|').split(' ')
    vn = set()  # 非终结符
    vt = set()  # 终结符
    for k in grammar:  # 添加非终结符
        vn.add(k)
    # 转为列表
    vn = list(vn)
    for k in grammar:
        for x in grammar[k]:
            for j in x:
                # 生成式右边除去非终结符剩下的是终结符
                if j not in vn and j != '$':
                    vt.add(j)
    # 转为列表
    vt = list(vt)
    return grammar, vn, vt


# 获取first集
def get_first(file):
    """
    1.若X->a..，则将终结符ａ加入FIRST(X)中;
    2.若X->$,则将终结符e加入FIRST(X)中($表示空集)；
    3.若X->BC..D,则将First（B）所有元素（除了空集）加入First（A），然后检测First（B），若First（B）中不存在空集, 即$,则停止，
    若存在则向B的后面查看，将First（C）中所有元素（除了空集）加入First（A），然后再检测First（C）中是否有$...直到最后，
    若D之前的所有非终结符的First集中都含有$,则检测到D时，将First（D）也加入First（A），若First（D）中含有$,则将 $加入First（A）
    """
    first_ = {}
    res, vn, vt = get_grammar(file)
    finish = 1
    for i in vn:
        first_[i] = set()
    while 1:
        for one in res:  # 依次读取非终结符
            t1 = len(first_[one])  # 扫描生成式之前的长度
            for alphas in res[one]:  # 读取one的各个生成式
                i = 0
                while i < len(alphas):  # 小于生成式的长度
                    v_t = alphas[i]  # 当前生成式中的第i个字符
                    if v_t in vn:  # 是非终结符P->ABC...
                        for ft in first_[v_t]:  # 先加入非空字符
                            if ft != '$':
                                first_[one].add(ft)
                        if '$' in first_[v_t]:  # 开始检测存在空，检查下一个
                            i += 1
                        else:  # 不存在，停止
                            break
                    else:
                        if i == 0:
                            first_[one].add(v_t)
                            break
                        if v_t in vt:  # 这个是终结符,前面含有$，加入，停止判断
                            first_[one].add(v_t)
                            break
                # 全部为非终结符，又都含有$,加入$
                if i == len(alphas):
                    first_[one].add('$')
            t2 = len(first_[one])  # 扫描后的长度
            if t1 != t2:  # 只要有一个非终结符的变化
                finish = 0  # 没有结束
        if finish:  # 不再增长
            break
        finish = 1
    return first_


''''# 获取follow集
def get_follow():
    follow = {}'''


def get_FirstVT(file):
    """
    :grammar: 文法，F->AB|BC存储格式：{F:[[A,B],[B,C]]}
    :first_vt: FirstVT集存储格式：{F:{a:1,b:0},B:{...}}
    """
    grammar, vn, vt = get_grammar(file)
    first_vt = {}
    # one一个非终结符
    for one in vn:  # 初始化F[P,a] = 0
        temp = {}  # 中间存储
        for two in vt:  # two:一个终结符
            temp[two] = 0  # {a:0}
        first_vt[one] = temp  # {F:{a:0},...}
    # 规则1 P->a... P->Qa, a->FirstVT(P)
    for lt in grammar:  # lt 生成式左边非终结符
        for r in grammar[lt]:  # r非终结符lt的生成式右边的一条语句
            if len(r) == 1:  # F->a
                t = r[0]
                if t in vt:  # F[a] = 1
                    first_vt[lt][t] = 1
            elif len(r) >= 2:  # P->Qa... | P->aQ...
                s = r[0]  # Q
                t = r[1]  # a
                if s in vt:  # P->aQ...
                    first_vt[lt][s] = 1
                elif s in vn and t in vt:  # P->Qa...
                    first_vt[lt][t] = 1
    # 规则2 P->Q... a->FirstVT(Q), a->FirstVT(P)
    while 1:
        judge = 1  # 判断结束标志
        for lt in grammar:  # lt 生成式左边非终结符
            for r in grammar[lt]:  # r非终结符lt的生成式右边的一条语句P->a...
                t = r[0]
                if t in vn:  # P->Q...
                    for n in first_vt[t]:  # 在FirstVT(Q)里寻找
                        if first_vt[t][n] == 1:  # n属于FirstVT(Q)
                            if first_vt[lt][n] == 0:  # 有新增的
                                judge = 0  # 不能结束
                                first_vt[lt][n] = 1  # n也属于FirstVT(P)
        if judge:  # 全部遍历完没有新增结束
            break
    return first_vt


def get_LastVT(file):
    """
    :grammar: 文法，F->AB|BC存储格式：{F:[[A,B],[B,C]]}
    :last_vt: FirstVT集存储格式：{F:{a:1,b:0},B:{...}}
    """
    grammar, vn, vt = get_grammar(file)
    last_vt = {}
    # one一个非终结符
    for one in vn:  # 初始化F[P,a] = 0
        temp = {}  # 中间存储
        for two in vt:  # two:一个终结符
            temp[two] = 0  # {a:0}
        last_vt[one] = temp  # {F:{a:0},...}
    # 规则1 P->...a P->...aQ, a->LastVT(P)
    for lt in grammar:  # lt 生成式左边非终结符
        for r in grammar[lt]:  # r非终结符lt的生成式右边的一条语句
            if len(r) == 1:  # F->a
                t = r[0]
                if t in vt:  # F[a] = 1
                    last_vt[lt][t] = 1
            elif len(r) >= 2:  # P->...a | P->...aQ
                s = r[-1]  # Q
                t = r[-2]  # a
                if s in vt:  # P->...Qa
                    last_vt[lt][s] = 1
                elif s in vn and t in vt:  # P->..aQ
                    last_vt[lt][t] = 1
    # 规则2 P->...Q a->LastVT(Q), a->LastVT(P)
    while 1:
        judge = 1  # 判断结束标志
        for lt in grammar:  # lt 生成式左边非终结符
            for r in grammar[lt]:  # r非终结符lt的生成式右边的一条语句P->a...
                t = r[-1]
                if t in vn:  # P->...Q
                    for n in last_vt[t]:  # 在LastVT(Q)里寻找
                        if last_vt[t][n] == 1:  # n属于LastVT(Q)
                            if last_vt[lt][n] == 0:  # 有新增的
                                judge = 0  # 不能结束
                                last_vt[lt][n] = 1  # n也属于LastVT(P)
        if judge:  # 全部遍历完没有新增结束
            break
    return last_vt


# 构造算符优先表
def get_op_table(file):
    """
    :param file: 文法文件
    first_vt: FirstVT集
    last_vt: Last_VT集
    :return: op_table 文法grammar的算符优先表
    """
    # 优先级关系: -1: 小于 0: 等于 1: 大于 2: 没有关系
    grammar, vn, vt = get_grammar(file)
    first_vt = get_FirstVT(file)
    last_vt = get_LastVT(file)
    op_table = {}
    # 初始化
    for i in vt:
        temp = {}
        for j in vt:
            temp[j] = 2
        op_table[i] = temp
    # 每个产生式i->n-1检查四种情况
    for lt in grammar:  # lt 生成式左边非终结符
        for r in grammar[lt]:  # r非终结符lt的生成式右边的一条语句
            n = len(r)
            for index in range(n - 1):
                x = r[index]
                y = r[index + 1]
                # P->ab
                if x in vt and y in vt:
                    op_table[x][y] = 0

                # P->aQb
                if index < n - 2:
                    z = r[index + 2]
                    if x in vt and y in vn and z in vt:
                        op_table[x][z] = 0

                # P->xY... a属于FirstVT(Y) x < a
                if x in vt and y in vn:
                    for a in first_vt[y]:
                        if first_vt[y][a] == 1:
                            op_table[x][a] = -1

                # P->Xy... a属于LastVT(X) a > y
                if x in vn and y in vt:
                    for a in last_vt[x]:
                        if last_vt[x][a] == 1:
                            op_table[a][y] = 1
    return op_table


# 修改负数
def fix_num(token):
    value_type_code = ['081', '082', '083', '084', '085', '087', '088']
    t = []  # 为空为错误的字符串
    if len(token) <= 2:  # 只有一个运算符和结束'#'
        # 1 # 或者 x #
        if token[0][0] == '086' or token[0][0] in value_type_code:
            t = token
    elif len(token) == 3:  # ++i  #或者-- i #
        if token[0][1] in ['++', '--'] and token[1][0] == '086':
            t = token
        elif token[0][0] == '086' and token[1][1] in ['++', '--']:  # i ++ #或者i -- #
            t = token
        elif token[0][1] == '-' and token[1][1] in value_type_code:  # - 1 # 或者 - x #
            s = '-' + token[1][1]  # 合并
            t = [(token[1][0], s, token[0][2], token[0][3])] + token[-1]
        elif token[0][1] == '+' and token[1][1] in value_type_code:
            t = [(token[1][0], token[1][1], token[0][2], token[0][3])] + token[-1]
    else:
        index = 1
        if token[0][1] == '-':
            if token[1][0] in value_type_code or token[1][0] == '086':
                s = '-' + token[1][1]
                t = [(token[1][0], s, token[0][2], token[0][3])]
                index += 1
        else:
            t.append(token[0])
        while index < len(token) - 1:
            x = token[index - 1]
            y = token[index]
            z = token[index + 1]
            if (x[0] != '086' and x[0] not in value_type_code) and y[1] == '-':
                if z[0] in value_type_code or z[0] == '086':
                    s = '-' + z[1]
                    t.append((z[0], s, y[2], y[3]))
                    index += 1
                elif z[1] != '(':
                    return []
                else:
                    t.append(y)
            else:
                t.append(token[index])
            index += 1
        t.append(token[-1])
    return t


# 转换数值
def get_num(num):
    ty = ['int', 'float', 'double', '081', '084', '085', '087', '088']
    num = list(num)
    if num[0] == 'int':
        if len(num[1]) >= 2:
            if num[1][0] == '0' and (num[1][1] != 'x' or num[1][1] != 'X'):
                num[1] = '0o' + num[1][1:]
    if num[0] in ty:
        num[1] = eval(num[1])
    return tuple(num)


# 分割函数的参数
def func_para(token):
    i = 2  # 下标
    rp = []  # 记录的参数
    tmp = []
    len_t = len(token)
    if len(token) == 3:
        return []
    stack = []
    while i < len_t - 1:
        if token[i][1] == '(':
            stack.append(')')
            tmp.append(token[i])
        elif token[i][1] == ')':
            stack.pop()
            tmp.append(token[i])
        elif token[i][1] != ',':
            tmp.append(token[i])
        else:
            if len(stack) == 0:
                rp.append(tmp)
                tmp = []
                stack = []
            else:
                tmp.append(token[i])
        i += 1
    rp.append(tmp)
    return rp


if __name__ == '__main__':
    first_agg = get_first('./Data/Grammar/test3.txt')
    FirstVT = get_FirstVT('./Data/Grammar/expression.txt')
    LastVT = get_LastVT('./Data/Grammar/expression.txt')
    Op_Table = get_op_table('./Data/Grammar/expression.txt')
    print(len(Op_Table['+']))
    # save('./Data/Op_Table.json', Op_Table)
