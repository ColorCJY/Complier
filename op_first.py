from other_function import *


class Op_first:
    def __init__(self, token):
        self.grammar, self.VN, self.VT = get_grammar('Data/Grammar/expression.txt')  # 文法
        self.table = load('./Data/Op_Table.json')  # 算符优先表
        self.token = token  # 符号串
        self.len_t = len(self.token)
        self.token_i = 0

    def getNext(self):
        if self.token_i >= self.len_t:
            return []
        token = self.token[self.token_i]
        self.token_i += 1
        return token

    def analysis(self):
        s = ['', '#']
        top = 1
        while 1:
            token = self.getNext()
            if not token:
                a = '#'
            elif token[0] == '086':
                a = 'identity'
            elif token[0] in ['081', '082', '083', '084', '085', '087', '088']:
                a = 'const_value'
            else:
                a = token[1]
            if s[top] in self.VT:
                j = top
            else:
                j = top - 1
            if self.table[s[j]][a] == -1 or self.table[s[j]][a] == 0:
                top += 1
                if top >= len(s):
                    s.append(a)
                else:
                    s[top] = a
            elif self.table[s[j]][a] == 1:
                while 1:
                    q = s[j]
                    if s[j-1] in self.VT:
                        j -= 1
                    else:
                        j -= 2
                    if self.table[s[j]][q] < 0:
                        break
                tmp = []
                for i in range(j + 1, top + 1):
                    tmp.append(s[i])
                end = 0
                error = 1
                for lt in self.grammar:
                    for r in self.grammar[lt]:
                        if len(r) == len(tmp):
                            i = 0
                            while i < len(r):
                                if r[i] in self.VN:
                                    if tmp[i] not in self.VN:
                                        break
                                elif r[i] in self.VT:
                                    if tmp[i] != r[i]:
                                        break
                                else:
                                    return 0
                                i += 1
                            if i >= len(r):
                                top = j + 1
                                s[top] = lt
                                end = 1
                                break
                    if end:
                        self.token_i -= 1
                        error = 0
                        break
                if error:  # 不是文法定义的运算
                    return 0
            else:
                return 0
            if len(s) >= 4:  # 最后规约为一个终结符后形成#E由于#=#会形成#E##...#把这样作为结束的标志
                if s[1] == '#' and s[2] in self.VN and s[3] == '#':
                    while 1:
                        t = 0
                        for lt in self.grammar:
                            for r in self.grammar[lt]:
                                if len(r) == 1:
                                    if r[0] == s[2]:
                                        if lt == 'expression':
                                            return s[2]
                                        s[2] = lt
                                        t = 1
                                        break
                            if t:
                                break
