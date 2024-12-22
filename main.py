import re
from antlr4 import *
from rfplLexer import rfplLexer
from rfplParser import rfplParser

func_table = {
    'S': lambda b, x: x+1,
}

def call(fun:str, b, x):
    mtch = re.fullmatch(r'Id(\d+)', fun)
    if mtch:
        num = int(mtch.group(1))
        return x[num] if num < len(x) else 0
    mtch = re.fullmatch(r'C(\d+)', fun)
    if mtch:
        return int(mtch.group(1))
    if fun in func_table.keys():
        return func_table[fun](b, x)
    return -1

def interpret(tree, base, rbase, args):
    if len(base) != len(rbase):
        print('ERR :: mismatch between base and runtime base!')
        return -1
    tree = tree.children[0]
    ruleName = parser.ruleNames[tree.getRuleIndex()]
    if ruleName == 'fexprleaf':
        symb = tree.children[0].getText()
        b = []
        if len(tree.children) == 5:
            i = base.find(tree.children[2].getText())
            if i != -1:
                b.append(rbase[i])
            else:
                b.append(tree.children[2])
            fexprlist = tree.children[3]
            while len(fexprlist.children) > 1:
                i = base.find(fexprlist.children[1].getText())
                if i != -1:
                    b.append(rbase[i])
                else:
                    b.append(fexprlist.children[1])
                fexprlist = fexprlist.children[2]
        call(symb, b, args)
    elif ruleName == 'builtinCn':
        pass
    elif ruleName == 'builtinPr':
        pass
    elif ruleName == 'builtinMn':
        pass


while True:
    input_stream = InputStream(input(">> "))
    lexer = rfplLexer(input_stream)
    token_stream = CommonTokenStream(lexer)
    parser = rfplParser(token_stream)
    tree = parser.line()  # Start from the 'line' rule
    print("Parse Tree:")
    print(tree.toStringTree(recog=parser))  # Display the parse tree

    tree = tree.children[0]
    ruleName = parser.ruleNames[tree.getRuleIndex()]
    if ruleName == 'define':
        symb = tree.children[0].getText()
        if symb in func_table.keys():
            print(f'ERR :: {symb} is already defined!')
            continue
        base = []
        if len(tree.children) == 7:
            base.append(tree.children[2].getText())
            symblist = tree.children[3]
            while len(symblist.children) > 1:
                base.append(symblist.children[1].getText())
                symblist = symblist.children[2]
        func_table[symb] = lambda b, x: interpret(tree.children[-1], base, b, x)
    elif ruleName == 'examine':
        pass
