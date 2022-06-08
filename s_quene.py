class Queue(object):

    # 创建空列表
    def __init__(self):
        self.value = []

    # 判断是否为空
    def is_empty(self):
        return self.value == []

    # 队列长度
    def size(self):
        return len(self.value)

    # 入队
    def enqueue(self, data):
        # 类似尾部插入
        self.value.append(data)

    # 出队
    def dequeue(self):
        # 利用列表pop方法弹出第一个
        return self.value.pop(0)

    def head_tail(self, t):
        if t == 'h':
            return self.value[0]
        if t == 't':
            return self.value[len(self.value) - 1]
