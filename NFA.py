# 先求后缀式，再进行正归式到NFA的转换
from graphviz import Digraph
from DFA import To_DFA
from min_DFA import To_min
from stack import *


# 返回运算符的优先级，优先级定义：闭包（*）> 连接(.) >或运算（|）>括号
def priority_level(a):  # 优先级
    if a == '(':
        return 1
    elif a == '|':
        return 2
    elif a == '.':
        return 3
    elif a == '*':
        return 4
    else:
        return 0


# 判断是否是运算符
def is_Operator(a):
    if a == '*' or a == '|' or a == '.':
        return True
    else:
        return False


def draw_graph(graphs, name):
    g = graphs[0]
    end = graphs[2]
    # 默认pdf，更改类型加上format='文件类型(png,pdf等)'
    gs = Digraph('G', filename='./Debug/' + name + '.gv')
    gs.attr(rankdir='LR')
    for i in g:
        gs.edge(str(i['start']), str(i['end']), label=str(i['edge']))
    for i in end:
        gs.node(str(i), shape='doublecircle')
    # True会以系统默认打开这种文件的方式打开文件
    gs.render(view=True)


class To_NFA(object):
    def __init__(self, s1):
        self.s = s1  # 输入正则字符串

    # 一些不会抛异常的错
    def judge_s(self):
        if '.' in self.s:
            return 'E'
        f = self.s.count('(')
        h = self.s.count(')')
        if f != h:
            return 'E'
        for i in range(len(self.s)):
            # 非英文符号
            if ord(self.s[i]) < 0 or ord(self.s[i]) > 127:
                return 'E'
            if i == 0:
                pass
            else:
                if self.s[i - 1] == '*' and self.s[i] == '*':
                    return 'E'

    def add_lian(self):  # 增添连接符.
        t = list(self.s)
        i = 0
        while i < len(t) - 1:
            judge = ['(', ')', '*', '|']
            a, b = t[i], t[i + 1]
            # A·() or a·b or A*·() or A*·b or ()·() or ()·A
            if (a not in judge and b == '(') or (a not in judge and b not in judge) or \
                    (a == '*' and (b not in judge or b == '(')) or (a == ')' and b == '(') or \
                    (a == ')' and b not in judge):
                t.insert(i + 1, '.')
                i += 1
            i += 1
        tmp = ''.join(t)
        self.s = tmp

    def tran_s(self):  # 中缀转后缀
        # 记录转换后的字符串
        temp = []
        # 压栈操作符
        op = Stack()
        for i in range(len(self.s)):
            c = self.s[i]
            if is_Operator(c):  # 是运算符
                if op.is_empty():  # 空栈压栈
                    op.push(c)
                else:  # 优先级更大的运算符全部出栈
                    while not op.is_empty():
                        t = op.top()
                        if priority_level(c) <= priority_level(t):
                            op.pop()
                            temp.append(t)
                        else:
                            break
                    op.push(c)
            else:
                if c == '(':  # 左括号直接入栈
                    op.push(c)
                elif c == ')':  # 遇到右括号，一直出栈，直到遇到左括号
                    while op.top() != '(':
                        temp.append(op.top())
                        op.pop()
                    op.pop()
                else:
                    temp.append(c)  # 操作数直接放入表达式中
        while not op.is_empty():
            temp.append(op.top())
            op.pop()
        return ''.join(temp)

    def to_nfa(self):
        judge = self.judge_s()
        if judge == 'E':
            return []
        self.add_lian()
        ts = self.tran_s()
        symbols = Stack()  # 符号栈
        starts = Stack()  # 起点栈
        nfa_g = Stack()  # nfa图栈
        ends = Stack()  # 终点栈
        symbols.push('#')  # '#'入符号栈
        state = 0
        for c in ts:
            if not is_Operator(c):
                dit = [{'start': state, 'edge': c, 'end': state + 1}]
                starts.push(state)
                ends.push(state + 1)
                state += 2
                nfa_g.push(dit)
                continue

            if c == '.':
                ts = starts.pop()  # 起点2出栈
                ss = starts.pop()  # 起点1出栈
                te = ends.pop()  # 终点2出栈
                se = ends.pop()  # 终点1出栈
                t = nfa_g.pop()  # 连接后
                s1 = nfa_g.pop()  # 连接前
                for j in range(len(t)):
                    if t[j]['start'] == ts:
                        t[j]['start'] = se
                starts.push(ss)
                ends.push(te)
                nfa_g.push(s1 + t)

            elif c == '|':
                ts = starts.pop()  # 起点2出栈
                ss = starts.pop()  # 起点1出栈
                te = ends.pop()  # 终点2出栈
                se = ends.pop()  # 终点1出栈
                t = nfa_g.pop()  # 或后
                s1 = nfa_g.pop()  # 或前
                x1 = [{'start': state, 'edge': '$', 'end': ss}]  # x->1
                x2 = [{'start': state, 'edge': '$', 'end': ts}]  # x->2
                starts.push(state)  # 新起点入栈
                state += 1
                y1 = [{'start': se, 'edge': '$', 'end': state}]  # 1e->y
                y2 = [{'start': te, 'edge': '$', 'end': state}]  # 2e->y
                ends.push(state)  # 新终点入栈
                state += 1
                new_g = x1 + x2 + s1 + t + y1 + y2  # 新的图
                nfa_g.push(new_g)
                continue

            elif c == '*':
                ss = starts.pop()
                se = ends.pop()
                s1 = nfa_g.pop()
                new_s = state
                new_e = state + 1
                x1 = [{'start': new_s, 'edge': '$', 'end': ss}]  # x->s
                x2 = [{'start': se, 'edge': '$', 'end': ss}]  # e->s
                x3 = [{'start': se, 'edge': '$', 'end': new_e}]  # e->y
                x4 = [{'start': new_s, 'edge': '$', 'end': new_e}]  # x->y
                starts.push(new_s)
                ends.push(new_e)
                state += 2
                nfa_g.push(x1 + x4 + s1 + x2 + x3)

            else:
                return []

        return nfa_g.pop(), starts.pop(), [ends.pop()]


if __name__ == '__main__':
    s1 = input('输入正规式：')
    s1 = s1.replace('\n', '')
    try:
        if s1:
            nfa = To_NFA(s1)
            graph = nfa.to_nfa()
            if not graph:
                print('Error Input:' + s1 + '!')
            else:
                draw_graph(graph, 'NFA')
                dfa = To_DFA(graph)
                graph = dfa.to_dfa()
                draw_graph(graph, 'DFA')
                min_dfa = To_min(graph)
                graph = min_dfa.min_dfa()
                draw_graph(graph, 'MFA')
    except Exception as e:
        print('Error Input:' + s1 + '!')
