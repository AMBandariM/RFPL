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


def check_grammar(cmd, superc=True):
    if superc and re.match(r'^\s*(exit|finish|end|list|save\s+[\w/\-]+)\s*$', cmd):
        return True
    if re.match(r'^\s*load\s+[\w/\-]+\s*$', cmd):
        return True
    return intr.parsable(cmd)


custom_style = Style.from_dict({
    'keyword': 'fg:magenta',
    'text': 'fg:white',
    'comment': 'fg:green',
    'error': 'fg:red',
    'number': 'fg:orange',
})

class CustomLexer(Lexer):
    def lex_document(self, document):
        def get_line(lineno):
            line = document.lines[lineno]
            input_stream = antlr4.InputStream(line)
            lexer = RFPLLexer(input_stream)
            lexer.removeErrorListeners()
            formatted = []
            while True:
                tok = lexer.nextToken()
                if tok.type == antlr4.Token.EOF:
                    break
                if tok.type == RFPLLexer.Unknown:
                    formatted.append(('class:error', tok.text))
                elif tok.type == RFPLLexer.Comment or tok.type == RFPLLexer.String:
                    formatted.append(('class:comment', tok.text))
                elif tok.type == RFPLLexer.Number or tok.text in ('!', '#', '@'):
                    formatted.append(('class:number', tok.text))
                elif tok.text in ('Cn', 'Pr', 'Mn', 'S', '#load'):
                    formatted.append(('class:keyword', tok.text))
                else:
                    formatted.append(('class:text', tok.text))
            return formatted
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
        names = intr.loadBasics()
        print('\033[32m', end='')
        for func in names:
            print(f' . Function {func} added')
        print('\033[0m', end=''if loaded else '\n')
        return
    filename += '.rfpl'
    try:
        with open(filename, 'r') as f:
            lines = f.readlines()
            cmd = ''
            for line in lines:
                cmd += line.strip()
                if not cmd:
                    continue
                cmd += ' '
                if not check_grammar(cmd, superc=False):
                    continue
                mtch = re.match(r'^\s*load\s+(?P<FILE>[\w/\-]+)\s*$', cmd)
                if mtch:
                    load(intr, mtch.group('FILE'), loaded + [filename])
                else:
                    ok, result = intr.interpret(cmd)
                    if not ok:
                        print(f'\033[31m{result}\033[0m')
                    elif isinstance(result, Natural):
                        print(f'\033[33m = {result}\033[0m')
                    elif result is not None:
                        print(f'\033[33m . {result}\033[0m')
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
        ok, result = intr.interpret(line)
        if not ok:
            print(f'\033[31m{result}\033[0m')
        elif isinstance(result, Natural):
            print(f'\033[33m = {result}\033[0m\n')
        elif result is not None:
            print(f'\033[33m . {result}\033[0m\n')
