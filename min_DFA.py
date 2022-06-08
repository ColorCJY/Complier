# 用分割法求最小化的DFA

class To_min:
    def __init__(self, dfa):
        self.dfa = dfa[0]  # 未简化的dfa图
        self.start = dfa[1]  # 开始结点
        self.end = dfa[2]  # 终态结点

    # 分割前的准备
    def pre_split(self):
        # 首先将状态分为非终态和终态
        tmp = []
        # 记录非终态结点
        for i in self.dfa:
            s = i['start']
            e = i['end']
            if s not in self.end and s not in tmp:
                tmp.append(s)
            if e not in self.end and e not in tmp:
                tmp.append(e)
        # 添加终态结点
        tmp = [tmp] + [self.end]

        # 记录边
        edges = set()
        for i in self.dfa:
            edges.add(i['edge'])

        # 求出各个状态的各个输入的变化
        a = {}
        for i in self.dfa:
            s = i['start']
            edge = i['edge']
            key = str(s) + str(edge)
            e = i['end']
            a[key] = e
        return tmp, a, edges

    # 进行等价分割
    def get_split(self):
        # 进行一些后面需要用到的值的准备
        tmp, a, edges = self.pre_split()
        t = 1  # 停止简化标志
        while t == 1:
            t = 0
            dit_state = {}  # 记录一种等价状态下含有的结点
            for i in range(len(tmp)):
                dit_state[i] = tmp[i]
            # 开始分割
            for _edge in edges:  # 考虑一个弧的转换
                split = []  # 一轮分割后的结果
                for _tmp in tmp:  # 等价状态一个一个的判断
                    if len(_tmp) == 1:
                        split.append(_tmp)
                        continue
                    res = {}  # 一种等价状态划分后的结果
                    for __tmp in _tmp:  # 该等价状态下的每个结点的转换
                        key = str(__tmp) + str(_edge)  # 转换
                        if key in a:  # 该节点有这种转换
                            value = a[key]  # 转换后的值
                            for x in dit_state:  # 获取转换后的等价状态
                                if value in dit_state[x]:  # 找到状态
                                    if x not in res:  # 未被记录
                                        res[x] = [__tmp]
                                    else:  # 记录
                                        res[x].append(__tmp)
                                    break  # 退出
                        else:
                            if -1 not in res:  # 未被记录
                                res[-1] = [__tmp]
                            else:  # 记录
                                res[-1].append(__tmp)
                    for j in res:
                        split.append(res[j])
                if len(split) != len(tmp):  # 有分割
                    tmp = split  # 重新开始分割
                    t = 1
                    break  # 已经区分开不用判断后面的边了
        return tmp

    def min_dfa(self):
        # 获得等价分割的结点
        tmp = self.get_split()
        dit = {}  # 重新分布结点
        new_g = []  # 重新分布图
        start = 0  # 开始结点
        end = []  # 终态结点

        # 等价结点的结点值重新赋值
        for i in range(len(tmp)):  # 以该等价组合所在数组下标代替
            for j in tmp[i]:  # 进行每一个结点的代替
                dit[j] = i

        # 重新构建图
        for i in self.dfa:
            # 顶点替换，边值不变
            s = i['start']
            eg = i['edge']
            e = i['end']
            new_e = {'start': dit[s], 'edge': eg, 'end': dit[e]}
            # 防止重复
            if new_e not in new_g:
                new_g.append(new_e)

        # 含有转换前的开始结点的等价组合仍为开始结点
        for i in range(len(tmp)):
            if self.start in tmp[i]:
                start = i  # 转换前只有一个开始结点
                break  # 并根据分割的过程可知转换也只有一个开始结点

        # 含有转换前的终态结点的等价组合仍为终态结点
        for i in range(len(tmp)):
            for j in tmp[i]:  # 可能会有多个终态结点
                if i not in end and j in self.end:
                    end.append(i)
        '''ヾ(●´∀｀●)由正则转换过来的DFA应该不会出现多余结点吧'''
        return new_g, start, end
