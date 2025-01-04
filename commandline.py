from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.lexers import Lexer
from prompt_toolkit.styles import Style
import re
from interpreter import Interpreter, Natural
import os

custom_style = Style.from_dict({
    'super': 'fg:magenta',
    '': 'fg:white',
})

class CustomLexer(Lexer):
    def lex_document(self, document):
        def get_line(lineno):
            line = document.lines[lineno]
            tokens = []
            parts = re.findall(r'\w+|[^\w\s]|\s', line)
            for part in parts:
                if part in ['Pr', 'Mn', 'Cn', 'S', '!', '#', '@']:
                    tokens.append(('class:super', part))
                else:
                    tokens.append(('class:', part))
            return tokens
        return get_line


def multiline_input():
    session = PromptSession(lexer=CustomLexer(), style=custom_style)
    lines = []

    fst = True
    with patch_stdout():
        while True:
            line = session.prompt('>> ' if fst else '   ')
            fst = False
            if not line.strip():
                break
            lines.append(line)
    return ' '.join(lines)

def load(intr, filename:str):
    if filename == 'basics':
        intr.func_table['add'] = Interpreter.FuncType(call=lambda _stack, x : Natural(x[0].toInt() + x[1].toInt))
        intr.func_table['mul'] = Interpreter.FuncType(call=lambda _stack, x : Natural(x[0].toInt() * x[1].toInt))
        intr.func_table['pow'] = Interpreter.FuncType(call=lambda _stack, x : Natural(x[1].toInt ** x[0].toInt()))
        print('\033[32mbaseic functions added: add, mul, pow\033[0m\n')
    else:
        filename += '.rfpl'
        try:
            with open(filename, 'r') as f:
                lines = f.read().split('\n')
                cmd = ''
                for line in lines:
                    if line == '':
                        cmd = cmd.strip()
                        if cmd:
                            suc, res = intr.interpret(cmd)
                            if suc != 'Success':
                                print(f'\033[31m{suc}\033[0m')
                            elif isinstance(res, Natural):
                                print(f'\033[33m = {res}\033[0m')
                            else:
                                print(f'\033[33m . {res}\033[0m')
                        cmd = ''
                    else:
                        cmd += line + ' '
                print()
        except Exception as e:
            print(f'\033[31mcoulden\'nt open {filename}\033[0m\n')

hist = ''
def save(filename:str):
    filename += '.rfpl'
    if os.path.exists(filename):
        print('\033[31msorry, this file exists.\033[0m\n')
    else:
        with open(filename, 'w') as f:
            f.write(hist)
            print(f'   \033[33msaved on {filename}\033[0m\n')

def test(fun1, fun2):
    pass

if __name__ == '__main__':
    intr = Interpreter()
    while True:
        line = multiline_input()
        if re.match(r'exit|finish|end', line):
            break
        if re.match(r'list', line):
            print('\033[33m.. ', end='')
            for fun in intr.func_table.keys():
                if fun != 'S':
                    print(fun, end=' ')
            print('\033[0m\n')
            continue
        mtch = re.match(r'load (?P<FILE>\w+)', line)
        if mtch:
            load(intr, mtch.group('FILE'))
            continue
        mtch = re.match(r'save (?P<FILE>\w+)', line)
        if mtch:
            save(mtch.group('FILE'))
            continue
        mtch = re.match(r'test (?P<FUN1>\w+) (?P<FUN2>\w+)', line)
        if mtch:
            test(mtch.group('FUN1'), mtch.group('FUN2'))
            continue
        hist += line.strip() + '\n\n'
        suc, res = intr.interpret(line)
        if suc != 'Success':
            print(f'\033[31m{suc}\033[0m\n')
        elif isinstance(res, Natural):
            print(f'\033[33m = {res}\033[0m\n')
        else:
            print(f'\033[33m . {res}\033[0m\n')
