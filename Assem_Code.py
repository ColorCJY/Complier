def trans_code(code, index):
    assem_code = ''
    op_num1, op_num2, result = code[1], code[2], code[3]
    if code[0] == 'call':
        assem_code = '  CALL {};\n'.format(code[1])
    elif code[0] == 'call':
        assem_code = '  CALL {};\n'.format(code[1])
    elif code[0] == '+':  # 加法
        assem_code = '  MOV AX,{}\n  ADD AX,{}\n  MOV {},AX;\n'.format(op_num1, op_num2, result)
    elif code[0] == '-':
        assem_code = '  MOV AX,{}\n  SUB AX,{}\n  MOV {},AX;\n'.format(op_num1, op_num2, result)
    elif code[0] == '*':
        assem_code = '  MOV AX,{}\n  MOV BX,{}\n  MUL BX\n  MOV {},AX\n'.format(op_num1, op_num2, result)
    elif code[0] == '/':
        assem_code = '  MOV AX,{}\n  MOV DX,0\n  MOV BX,{}\n  DIV BX\n  MOV {},AX\n'.format(op_num1, op_num2, result)
    elif code[0] == '%':
        assem_code = '  MOV AX,{}\n  MOV DX,0\n  MOV BX,{}\n  DIV BX\n  MOV {},DX\n'.format(op_num1, op_num2, result)
    elif code[0] == '<':
        assem_code = '  MOV DX,1\n  MOV AX,{}\n  CMP AX,{}\n  JB _LT\n  MOV DX,0\n  _LT: MOV {}, DX\n'.format(
            op_num1, op_num2, result)
    elif code[0] == '>=':
        assem_code = '  MOV DX,1\n  MOV AX,{}\n  CMP AX,{}\n  JNB _GE\n  MOV DX,0\n  _GE: MOV {}, DX\n'.format(
            op_num1, op_num2, result)
    elif code[0] == '>':
        assem_code = '  MOV DX,1\n  MOV AX,{}\n  CMP AX,{}\n  JA _GT\n  MOV DX,0\n  _GT: MOV {}, DX\n'.format(
            op_num1, op_num2, result)
    elif code[0] == '<=':
        assem_code = '  MOV DX,1\n  MOV AX,{}\n  CMP AX,{}\n  JNA _LE\n  MOV DX,0\n  _LE: MOV {}, DX\n'.format(
            op_num1, op_num2, result)
    elif code[0] == '==':
        assem_code = '  MOV DX,1\n  MOV AX,{}\n  CMP AX,{}\n  JE _EQ\n  MOV DX,0\n  _EQ: MOV {}, DX\n'.format(
            op_num1, op_num2, result)
    elif code[0] == '!=':
        assem_code = '  MOV DX,1\n  MOV AX,{}\n  CMP AX,{}\n  JNE _NE\n  MOV DX,0\n  _NE: MOV {}, DX\n'.format(
            op_num1, op_num2, result)
    elif code[0] == '&&':
        t1 = '  MOV DX,0\n  MOV AX,{}\n  CMP AX,0\n  JE _AND\n'.format(op_num1)
        t2 = '  MOV AX,{}\n  CMP AX,0\n  JE _AND\n  MOV DX,1\n  AND: MOV {},DX\n'.format(op_num2, result)
        assem_code = t1 + t2
    elif code[0] == '||':
        t1 = '  MOV DX,1\n  MOV AX,{}\n  CMP AX,0\n  JNE _OR\n'.format(op_num1)
        t2 = '  MOV AX,{}\n  CMP AX,0\n  JNE _OR\n  MOV DX,0\n  _OR: MOV {},DX\n'.format(op_num2, result)
        assem_code = t1 + t2
    elif code[0] == '!':
        assem_code = '  MOV DX,1\n  MOV AX,{}\n  CMP AX,0\n  JE _NOT\n  MOV DX,0\n  _NOT: MOV {},DX\n'.format(op_num1,
                                                                                                             result)
    elif code[0] == 'j':
        assem_code = '  JMP far ptr _{}\n'.format(result)
    elif code[0] == 'jnz':
        assem_code = '  MOV AX,{}\n  CMP AX,0\n  JE _EZ\n  JMP far ptr _{}\n  _EZ: NOP\n'.format(op_num1, result)
    elif code[0] == 'para':
        assem_code = '  MOV AX,{}\n  PUSH AX\n'.format(op_num1)
    elif code[0] == 'ret' and code[1]:
        assem_code = '  MOV AX,{}\n  MOV SP,BP\n  POP BP\n  RET\n'.format(op_num1)
    elif code[0] == 'ret' and not code[1]:
        assem_code = ' MOV SP,BP\n  POP BP\n  RET\n'.format(op_num1)
    elif code[0] == '=':
        if op_num1 == 'return_value':
            assem_code = '  MOV {}, AX\n'.format(result)
        else:
            assem_code = '  MOV AX,{}\n  MOV {}, AX\n'.format(op_num1, result)
    elif code[0] == 'sys':
        assem_code = '  QUIT: MOV AH, 4CH\n  int 21h'
    if assem_code:
        assem_code = '_' + str(index) + ':\n' + assem_code
    else:
        if code[0] == 'fun':
            assem_code = '_{}:\n  PUSH BP\n  MOV BP,SP\n  SUB SP\n'.format(code[1])
    return assem_code


class Assem_Code:
    def __init__(self, codes):
        self.codes = codes

    def first_step(self):
        assem_codes = ''
        n = len(self.codes)
        for index in range(n):
            assem_codes += trans_code(self.codes[index], index)
        with open('./Debug/assem_code.txt', 'w', encoding='utf-8') as f:
            f.write(assem_codes)
        return assem_codes
