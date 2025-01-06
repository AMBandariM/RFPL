from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.lexers import Lexer
from prompt_toolkit.styles import Style
import re
from .interpreter import Interpreter
from .natural import Natural
import os

import antlr4
from antlr4.error.ErrorListener import ErrorListener
from .RFPLLexer import RFPLLexer
from .RFPLParser import RFPLParser

class QuietErrorListener(ErrorListener):
    def __init__(self):
        super().__init__()
        self.has_errors = False

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        self.has_errors = True


def check_grammar(cmd, superc=True):
    if superc and re.match(r'^\s*(exit|finish|end|list|save\s+[\w/\-]+)\s*$',
                cmd):
        return True
    if re.match(r'^\s*load\s+[\w/\-]+\s*$', cmd):
        return True
    try:
        input_stream = antlr4.InputStream(cmd)
        lexer = RFPLLexer(input_stream)
        stream = antlr4.CommonTokenStream(lexer)
        parser = RFPLParser(stream)
        error_listener = QuietErrorListener()
        parser.removeErrorListeners()
        parser.addErrorListener(error_listener)
        parser.line()
    except Exception:
        return False

    return not error_listener.has_errors


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

session = PromptSession(lexer=CustomLexer(), style=custom_style)
def multiline_input():
    cmd = ''
    fst = True
    with patch_stdout():
        while True:
            line = session.prompt('>> ' if fst else '>  ').strip()
            fst = False
            if not line:
                break
            cmd += line + ' '
            if check_grammar(cmd):
                break
    return cmd

def load(intr: Interpreter, filename: str, loaded=[]):
    if filename in loaded:
        return
    if filename == 'basics':
        intr.load_basics()
        print('\033[32m', end='')
        for func in ['Add', 'Sub', 'Mul', 'Pow', 'Get', 'Set', 'Int', 'List', 'Mod']:
            print(f' . Function {func} added')
        print('\033[0m', end=''if loaded else '\n')
        return
    filename += '.rfpl'
    try:
        with open(filename, 'r') as f:
            lines = f.readlines()
            cmd = ''
            for line in lines:
                if line[0] == ';':
                    continue
                cmd += line.strip() + ' '
                if cmd == ' ':
                    cmd = ''
                    continue
                if not line.strip():
                    print(f'\033[31mSorry, I didn\'t understood this one:\n{cmd.strip()}\033[0m')
                    cmd = ''
                    continue
                if not check_grammar(cmd, superc=False):
                    continue
                mtch = re.match(r'^\s*load\s+(?P<FILE>[\w/\-]+)\s*$', cmd)
                if mtch:
                    load(intr, mtch.group('FILE'), loaded + [filename])
                else:
                    suc, res = intr.interpret(cmd)
                    if suc != 'Success':
                        print(f'\033[31m{suc}\033[0m')
                    elif isinstance(res, Natural):
                        print(f'\033[33m = {res}\033[0m')
                    else:
                        print(f'\033[33m . {res}\033[0m')
                cmd = ''
            print()
    except Exception as e:
        print(f'\033[31mcouldn\'nt open {filename}\033[0m\n')

hist = ''
def save(filename:str):
    filename += '.rfpl'
    if os.path.exists(filename):
        print('\033[31msorry, this file exists.\033[0m\n')
    else:
        with open(filename, 'w') as f:
            f.write(hist)
            print(f'   \033[33msaved on {filename}\033[0m\n')

if __name__ == '__main__':
    intr = Interpreter()
    while True:
        try:
            line = multiline_input()
        except (EOFError, KeyboardInterrupt):
            break
        if not line.strip():
            continue
        if re.match(r'^\s*(exit|finish|end)\s*$', line):
            break
        if re.match(r'list', line):
            print('\033[33m..', end='')
            out = []
            outstr = ''
            for fun in intr.symbol_table.table[::-1]:
                if fun.symbol != 'S' and fun.symbol not in out:
                    outstr = ' ' + fun.symbol + (f'[{fun.basesz}]' if fun.basesz else '') + outstr
                    out.append(fun.symbol)
            print(f'{outstr}\033[0m\n')
            continue
        mtch = re.match(r'^\s*load\s+(?P<FILE>[\w/\-]+)\s*$', line)
        if mtch:
            load(intr, mtch.group('FILE'))
            continue
        mtch = re.match(r'^\s*save\s+(?P<FILE>[\w/\-]+)\s*$', line)
        if mtch:
            save(mtch.group('FILE'))
            continue
        hist += line.strip() + '\n\n'
        suc, res = intr.interpret(line)
        if suc != 'Success':
            print(f'\033[31m{suc}\033[0m\n')
        elif isinstance(res, Natural):
            print(f'\033[33m = {res}\033[0m\n')
        else:
            print(f'\033[33m . {res}\033[0m\n')
