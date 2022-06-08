# 子集法进行NFA到DFA的转换
from s_quene import *


class To_DFA:
    def __init__(self, nfa):
        self.nfa = nfa[0]  # nfa图
        self.start = nfa[1]  # nfa开始结点
        self.end = nfa[2]  # nfa结束结点
        self.new_g = []  # 存储转换后的dfa图
        self.tmp = [self.start]  # 当前生成的状态

    def get_node(self, start):  # 获得ε-Closure
        for i in self.nfa:  # 依次比对
            t = i['start']  # 开始
            e = i['end']  # 结束
            # 是空弧转换且没被统计
            if t == start and i['edge'] == '$':
                if e not in self.tmp:
                    self.tmp.append(e)  # 添加
                    self.get_node(e)  # 该节点往下寻找

    def to_dfa(self):
        edges = set()  # 集合去重
        # 统计有哪些转换
        for i in self.nfa:
            if i['edge'] != '$':
                edges.add(i['edge'])
        state = Queue()  # 状态队列
        self.get_node(self.start)  # 获得开始结点
        state.enqueue(self.tmp)  # 开始结点入队
        self.tmp.sort()  # 排序便于比较是否是新的状态
        had = [self.tmp]  # 已经有过的状态
        while not state.is_empty():  # 没有更多新的状态退出
            t = state.dequeue()  # 出队
            for edge in edges:  # 依次比对转换
                self.tmp = []  # 当前生成的状态清空
                for i in t:  # 每个结点求转换
                    for j in self.nfa:  # 查找转换
                        s = j['start']
                        b = j['edge']
                        e = j['end']
                        if i == s and b == edge:  # 符合转换
                            self.tmp.append(e)  # 添加转换后的结点
                if self.tmp:
                    for i in self.tmp:
                        self.get_node(i)  # 获得ε-Closure
                    self.tmp.sort()  # 排序便于比较
                    if self.tmp not in had:  # 产生的是新状态
                        had.append(self.tmp)  # 记录已经产生过
                        state.enqueue(self.tmp)  # 入队
                    self.new_g.append({'start': had.index(t), 'edge': edge, 'end': had.index(self.tmp)})  # 添加图的边
        end = []  # 终态结点
        for j in range(len(had)):  # 含有转换前的终态结点的为终态结点
            if self.end[0] in had[j]:
                end.append(j)
        return self.new_g, self.start, end
