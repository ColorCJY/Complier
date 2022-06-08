import os
import sys


class result:
    def __init__(self):
        self.dire = os.path.dirname(sys.argv[0])
        self.dire += '/Debug'
        if os.path.exists(self.dire + '/token.txt'):
            os.remove(self.dire + '/token.txt')
        if not os.path.exists(self.dire):
            os.mkdir(self.dire)

    def result_word(self, error, token, now_file):
        f = open(self.dire + '/token.txt', 'w', encoding='UTF-8')
        for i in token:
            f.write(i[0] + ' ' + i[1] + ' ' + str(i[2]) + ' ' + str(i[3]) + '\n')
        f.close()
        with open(self.dire + '/token.txt', 'r', encoding='UTF-8') as f:
            token_s = f.readlines()
        for i in range(len(token_s)):
            token_s[i] = '(' + token_s[i].strip() + ')\n'
            t = token_s[i].split(' ')
            token_s[i] = ', '.join(t)
        token_s = ''.join(token_s)
        error_s = ''
        if error:
            error_s += str(len(error)) + ' error(s):\n'
            for i in error:
                error_s += now_file + i + '\n'
        else:
            error_s = '0 error(s)'
        return error_s, token_s
