from prompt_toolkit import PromptSession, ANSI
from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit.lexers import Lexer
from prompt_toolkit.styles import Style
import re
import os
from prompt_toolkit import print_formatted_text as print
import antlr4

from .RFPLLexer import RFPLLexer
from .interpreter import Interpreter, Message, MessageType


def check_grammar(cmd, superc=True):
    if superc and re.match(r'^\s*(exit|finish|end|list|save\s+[\w/\-]+)\s*$', cmd):
        return True
    return intr.parsable(cmd)[0]


custom_style = Style.from_dict({
    'keyword': 'fg:magenta',
    'text': 'fg:white',
    'comment': 'fg:green',
    'error': 'fg:red',
    'number': 'fg:orange',
})


C_GREEN = '\033[32m'
C_ORANGE = '\033[33m'
C_RED = '\033[31m'
C_RESET = '\033[0m'


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
                elif tok.type == RFPLLexer.Comment:
                    formatted.append(('class:comment', tok.text))
                elif tok.type == RFPLLexer.Number or tok.text in ('!', '#', '@'):
                    formatted.append(('class:number', tok.text))
                elif tok.text in ('Cn', 'Pr', 'Mn', 'S', 'load'):
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


hist = ''
def save(filename: str):
    filename += '.rfpl'
    if os.path.exists(filename):
        print(ANSI(f'{C_RED}sorry, this file exists.{C_RESET}\n'))
    else:
        with open(filename, 'w') as f:
            f.write(hist)
            print(ANSI(f'   {C_GREEN}saved on {filename}{C_RESET}\n'))

def mainloop():
    global hist, intr
    while True:
        try:
            line = multiline_input()
        except (EOFError, KeyboardInterrupt):
            break
        if not line.strip():
            continue
        if re.match(r'^\s*(exit|finish|end)\s*$', line):
            break
        if re.match(r'^\s*list\s*$', line):
            out = []
            outstr = ''
            for fun in intr.symbol_table.table[::-1]:
                if fun.symbol != 'S' and fun.symbol not in out:
                    outstr = ' ' + fun.symbol + (f'[{fun.ftype.nbase}]' if fun.ftype.nbase else f'({fun.ftype.narg})') + outstr
                    out.append(fun.symbol)
            print(ANSI(f'{C_ORANGE}..{outstr}{C_RESET}\n'))
            continue
        mtch = re.match(r'^\s*save\s+(?P<FILE>[\w/\-]+)\s*$', line)
        if mtch:
            save(mtch.group('FILE'))
            continue
        hist += line.strip() + '\n\n'
        ok, messages = intr.report(line)
        for msg in messages:
            if msg.typ == MessageType.NATURAL:
                print(ANSI(f' {C_GREEN}= {msg.natural}{C_RESET}'))
            elif msg.typ == MessageType.INFO:
                print(ANSI(f' {C_ORANGE}. {msg.message}{C_RESET}'))
            elif msg.typ == MessageType.ERROR:
                print(ANSI(f' {C_RED}! ERROR: {msg.message}{C_RESET}'))
                if msg.context:
                    for ctx in msg.context:
                        print(ANSI(C_RED + ' '*7 + ctx + C_RESET))
            elif msg.typ == MessageType.EXCEPTION:
                print(ANSI(f' {C_RED}* EXCEPTION: {msg.message}{C_RESET}'))
        print()


def main():
    global intr
    intr = Interpreter()
    try:
        mainloop()
    except KeyboardInterrupt:
        print('KeyboardInterrupt')


if __name__ == '__main__':
    main()
