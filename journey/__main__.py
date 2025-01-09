import sys
import time
import random
import json
from typing import Union, List
from rfpl.interpreter import Interpreter
from rfpl.RFPLLexer import RFPLLexer
from rfpl.RFPLParser import RFPLParser
from rfpl.interpreter import Interpreter, Message, MessageType
from rfpl.natural import Natural, NaturalList

from abc import ABC, abstractmethod
import re
from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit.lexers import Lexer
from prompt_toolkit.styles import Style
import antlr4

intr = None
def check_grammar(cmd, superc=True):
    if superc and re.match(r'^\s*(end|done|list|hint)\s*$', cmd):
        return True
    return intr.parsable(cmd)


custom_style = Style.from_dict({
    'keyword': 'fg:magenta',
    'text': 'fg:white',
    'comment': 'fg:green',
    'error': 'fg:red',
    'number': 'fg:orange',
})


C_GREEN = '\033[32m'
C_BLUE = '\033[34m'
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

def typewriter(text):
    lines = text.split('\n')
    fst = True
    for line in lines:
        print(f'{C_BLUE})) ' if fst else f'{C_BLUE})  ', end='', flush=True)
        fst = False
        for char in line:
            print(char, end='', flush=True)

            if char in '.!?':
                time.sleep(random.uniform(0.2, 0.3))
            elif char in ',;:':
                time.sleep(random.uniform(0.15, 0.2))
            elif char in ' ':
                time.sleep(random.uniform(0.04, 0.1))
            else:
                time.sleep(random.uniform(0.02, 0.08))
        print()
        time.sleep(random.uniform(0.06, 0.12))
    print(C_RESET, end='', flush=True)



class SideNotes:
    class Note:
        def __init__(self, title, content):
            self.title = title
            self.content = content
    
    def __init__(self):
        self.notes: List['Note'] = []

    def addNote(self, title, content):
        self.notes.append(Note(title, content))

    def run(self):
        pass


class Act(ABC):
    @abstractmethod
    def __init__(self, journey, starter: str, prerequisites: List['Act']):
        self.journey: Journey = journey
        self.starter: str = starter
        self.prerequisites: List['Act'] = prerequisites
        self.done: bool = False

    @abstractmethod
    def run(self):
        pass

    def runnable(self):
        if self.done:
            return False
        for act in self.prerequisites:
            if not act.done:
                return False
        return True


class UserGuide(Act):
    def __init__(self, journey, prerequisites: List[Act], jobs: list):
        super().__init__(journey, 'talk', prerequisites)
        self.jobs = jobs

    def run(self):
        for job in self.jobs:
            if job['type'] == 'typewriter':
                typewriter(job['content'])
            if job['type'] == 'print':
                print(job['content'])
            elif job['type'] == 'getusername':
                self.journey.username = input('>> ')
        self.done = True


challengeFunctions = {
    'x+y': {
        'func': lambda args : args[0] + args[1],
        'nargs': 2
    },
}
class Challenge(Act):
    def __init__(self, journey, starter: str, prerequisites: List[Act], target: str,
                 tests: list, limits: List[str], hints: List[str]):
        super().__init__(journey, starter, prerequisites)
        self.target: str = target
        self.tests: list = tests
        self.limits: List[str] = limits
        self.hints: List[str] = hints
        self.hintcounter: int = 0

    def crosslimit(self, line):
        return False

    def test(self):
        global intr
        syment = intr.symbol_table.table[-1]
        target = challengeFunctions[self.target]
        if syment.nargs != target['nargs']:
            typewriter(f'\'{self.target}\' gets {target['nargs']} arguments but \'{syment.symbol}\' gets {syment.nargs} arguments!')
            return False
        if syment.basesz > 0:
            typewriter(f'\'{syment.symbol}\' is not a finished function.')
            return False
        for test in self.tests:
            args = []
            for numb in test:
                args.append(Natural(numb))
            args = NaturalList(args)
            expected = challengeFunctions[self.target]['func'](args)
            actual = syment.call([], args)
            if expected.weirdHash() != actual.weirdHash():
                typewriter(f'Oh, it\'s not working with input ({', '.join([str(n) for n in test])})')
                return False
        typewriter(f'Congraduations!')
        return True

    def run(self):
        typewriter(f'{len(self.hints)} [hint]s, type [done] when you are. type [list] to see all functions you\'ve made.')
        global intr
        intr = Interpreter()
        hist = ''
        while True:
            line = multiline_input()
            if not line.strip():
                continue
            if re.match(r'^\s*end\s*$', line):
                self.hintcounter = 0
                return
            if re.match(r'^\s*done\s*$', line):
                if self.test():
                    break
                continue
            if re.match(r'^\s*hint\s*$', line):
                if self.hintcounter >= len(self.hints):
                    typewriter('There is no more hint!')
                else:
                    typewriter(f'[Hint {self.hintcounter + 1}/{len(self.hints)}] {self.hints[self.hintcounter]}')
                    self.hintcounter += 1
                continue
            if re.match(r'^\s*list\s*$', line):
                out = []
                outstr = ''
                for fun in intr.symbol_table.table[::-1]:
                    if fun.symbol != 'S' and fun.symbol not in out:
                        outstr = ' ' + fun.symbol + (f'[{fun.basesz}]' if fun.basesz else f'({fun.nargs})') + outstr
                        out.append(fun.symbol)
                print(f'{C_ORANGE}..{outstr}{C_RESET}\n')
                continue
            if self.crosslimit(line):
                continue
            hist += line.strip().replace(' ', '').replace('=', ' = ') + '\n'
            ok, messages = intr.report(line)
            for msg in messages:
                if msg.typ == MessageType.NATURAL:
                    print(f' {C_GREEN}= {msg.natural}{C_RESET}')
                elif msg.typ == MessageType.INFO:
                    print(f' {C_ORANGE}. {msg.message}{C_RESET}')
                elif msg.typ == MessageType.ERROR:
                    print(f' {C_RED}! ERROR: {msg.message}{C_RESET}')
                    if msg.context:
                        for ctx in msg.context:
                            print(C_RED + ' '*7 + ctx + C_RESET)
                elif msg.typ == MessageType.EXCEPTION:
                    print(f' {C_RED}* EXCEPTION: {msg.message}{C_RESET}')
            print()

        self.done = True


class Journey:
    def __init__(self, jsonfilepath: str):
        self.username: str = ''
        self.sidenotes: SideNotes = SideNotes()
        self.acts: List[Act] = []
        with open(jsonfilepath) as file:
            data = json.load(file)
            for act in data:
                if act['type'] == 'userguide':
                    prerequisites = []
                    for req in act['prerequisites']:
                        prerequisites.append(self.acts[req])
                    self.acts.append(UserGuide(self, prerequisites, act['jobs']))
                elif act['type'] == 'challenge':
                    prerequisites = []
                    for req in act['prerequisites']:
                        prerequisites.append(self.acts[req])
                    self.acts.append(
                        Challenge(self, act['starter'], prerequisites, act['target'], act['tests'], act['limits'], act['hints'])
                    )

    def run(self):
        running = True
        while running:
            runnables_starters = []
            runnables = {}
            for act in self.acts:
                if act.runnable():
                    runnables_starters.append(act.starter)
                    runnables[act.starter] = act
            while True:
                typewriter('Chose an option:')
                for starter in runnables_starters:
                    print(f'- {starter}')
                print('- end')
                cmd = input('>> ')
                if cmd == 'end':
                    running = False
                    break
                if cmd in runnables_starters:
                    break
            if cmd in runnables_starters:
                runnables[cmd].run()


jrny = Journey('./journey/journey_en.json')
jrny.run()

