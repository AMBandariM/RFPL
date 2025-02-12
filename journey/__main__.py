import sys
import shutil
import time
import random
import json
from typing import Union, List
from pathlib import Path
from rfpl.interpreter import Interpreter, DEBUG
from rfpl.RFPLLexer import RFPLLexer
from rfpl.RFPLParser import RFPLParser
from rfpl.interpreter import Interpreter, Message, MessageType
from rfpl.natural import Natural, NaturalList
from rfpl.symbol import SymbolEntry, FunctionType

from abc import ABC, abstractmethod
import re
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit.lexers import Lexer
from prompt_toolkit.styles import Style
import antlr4
from antlr4.ParserRuleContext import ParserRuleContext

intr, lastTree = None, None
def check_grammar(cmd, superc=True):
    if superc and re.match(r'^\s*(end|done|list|hint)\s*$', cmd):
        return True
    global lastTree
    res, lastTree = intr.parsable(cmd)
    return res


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
C_GREY = '\033[90m'
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

def line_breaker(lines, lim):
    res = []
    for line in lines:
        parts = line.split(' ')
        res.append(parts[0])
        cnt = len(parts[0])
        for part in parts[1:]:
            if cnt + len(part) < lim:
                res[-1] += ' ' + part
                cnt += 1 + len(part)
            else:
                res.append(part)
                cnt = len(part)
    return res

def typewriter(text, highlights=[], end='\n'):
    t = 0 if DEBUG else 1
    lines = text.split('\n')
    lines = line_breaker(lines, shutil.get_terminal_size()[0] - 3)
    fst = True
    print(C_BLUE, end='', flush=True)
    for line in lines:
        for highlight in highlights:
            line = line.replace(highlight, C_ORANGE + highlight + C_BLUE)
        print(f')) ' if fst else f')  ', end='', flush=True)
        fst = False
        for char in line:
            print(char, end='', flush=True)
            if char in '.!?':
                time.sleep(random.uniform(0.2 * t, 0.3 * t))
            elif char in ',;:':
                time.sleep(random.uniform(0.15 * t, 0.2 * t))
            elif char in ' ':
                time.sleep(random.uniform(0.04 * t, 0.1 * t))
            else:
                time.sleep(random.uniform(0.02 * t, 0.08 * t))
        print()
        time.sleep(random.uniform(0.06 * t, 0.12 * t))
    print(C_RESET, end=end, flush=True)


class SimpleCommandCompleter(Completer):
    def __init__(self, commands, ignore_case=True):
        self.commands = commands
        self.ignore_case = ignore_case

    def get_completions(self, document, complete_event):
        word = document.text_before_cursor
        if word[-1] == ' ':
            return
        word = [prt for prt in word.split(' ') if len(prt) > 0]
        if len(word) != 1:
            return
        word = word[0]

        if self.ignore_case:
            word = word.lower()

        for cmd in self.commands:
            if self.ignore_case:
                cmd_lower = cmd.lower()
                if cmd_lower.startswith(word):
                    yield Completion(cmd, start_position=-len(word))
            else:
                if cmd.startswith(word):
                    yield Completion(cmd, start_position=-len(word))


class SideNotes:
    class Note:
        def __init__(self, title, content):
            self.title = title
            self.content = content
    
    def __init__(self):
        self.notes: List['SideNotes.Note'] = []
        self.session = PromptSession()

    def add_note(self, title, content):
        for note in self.notes:
            if note.title == title:
                note.content += '\n' + content
                return
        self.notes.append(self.Note(title, content))

    def print_note(self, index):
        print('#'*5 + ' ' + self.notes[index].title + ' ' + '#'*5)
        print(self.notes[index].content)
        print()

    def run(self):
        if len(self.notes) == 0:
            print(f'{C_GREY}There is no note!{C_RESET}\n')
            return
        while True:
            print(f'{C_GREY}// Choose a note by number or [end]')
            for i, note in enumerate(self.notes):
                print(f'{i:2d} {note.title}')
            print(f'{len(self.notes):2d} end{C_RESET}\n')
            cmd = self.session.prompt('?? ').strip()
            if cmd == 'end':
                print()
                return
            try:
                cmd = int(cmd)
                if cmd >= len(self.notes) or cmd < 0:
                    print()
                    return
                self.print_note(cmd)
            except ValueError:
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
        self.session = PromptSession()

    def run(self):
        for job in self.jobs:
            if job['type'] == 'typewriter':
                highlights = job['highlights'] if 'highlights' in job.keys() else []
                typewriter(job['content'], highlights=highlights)
            elif job['type'] == 'print':
                ncols, _ = shutil.get_terminal_size()
                lines = job['content'].split('\n')
                for line in lines:
                    print(' ' * ((ncols - len(line)) // 2) + line)
                print()
            elif job['type'] == 'getusername':
                self.journey.username = self.session.prompt('>> ')
                print()
            elif job['type'] == 'sidenote':
                self.journey.sidenotes.add_note(title=job['title'], content=job['content'])
        self.done = True


def __gcd(a: int, b: int)->int:
    if a == 0:
        return b
    if b == 0:
        return a
    return __gcd(min(a, b), max(a, b) % min(a, b))

def __fib(n: int)->int:
    if n < 2:
        return 1
    return __fib(n-1) + __fib(n-2)

challengeFunctions = {
    '': {
        'func': lambda args : args[0],
        'narg': 1
    },
    'z+3': {
        'func': lambda args : args[2] + Natural(3),
        'narg': 3
    },
    'x+y': {
        'func': lambda args : args[0] + args[1],
        'narg': 2
    },
    'y^x': {
        'func': lambda args : args[1] ** args[0],
        'narg': 2
    },
    'y-x': {
        'func': lambda args : args[1] - args[0],
        'narg': 2
    },
    'x/y': {
        'func': lambda args : Natural(int(args[0]) // int(args[1])),
        'narg': 2
    },
    'x%y': {
        'func': lambda args : args[0] % args[1],
        'narg': 2
    },
    '|x-y|': {
        'func': lambda args : Natural(max(int(args[0]) - int(args[1]), int(args[1]) - int(args[0]))),
        'narg': 2
    },
    'GCD': {
        'func': lambda args : Natural(__gcd(int(args[0]), int(args[1]))),
        'narg': 2
    },
    'fib': {
        'func': lambda args : Natural(__fib(int(args[0]))),
        'narg': 1
    }
}
assumedFunctions = {
    'Add': SymbolEntry(
        symbol='Add',
        call=lambda _blist, args : args[0] + args[1],
        builtin=True,
        ftype=FunctionType(narg=2),
    ),
    'Sub': SymbolEntry(
        symbol='Sub',
        call=lambda _blist, args : args[1] - args[0],
        builtin=True,
        ftype=FunctionType(narg=2),
    ),
    'Mul': SymbolEntry(
        symbol='Mul',
        call=lambda _blist, args : args[0] * args[1],
        builtin=True,
        ftype=FunctionType(narg=2),
    ),
    'Pow': SymbolEntry(
        symbol='Pow',
        call=lambda _blist, args : args[1] ** args[0],
        builtin=True,
        ftype=FunctionType(narg=2),
    ),
    'Mod': SymbolEntry(
        symbol='Mod',
        call=lambda _blist, args : args[0] % args[1],
        builtin=True,
        ftype=FunctionType(narg=2),
    )
}
class Challenge(Act):
    def __init__(self, journey, starter: str, prerequisites: List[Act], target: str,
                 tests: list, limits: List[str], have: List[str], hints: List[str], banner: str):
        super().__init__(journey, starter, prerequisites)
        self.target: str = target
        self.tests: list = tests
        self.limits: List[str] = limits
        self.hints: List[str] = hints
        self.have: List[str] = have
        self.hintcounter: int = 0
        self.banner = banner

    def collect_used_rules(self, tree, usedRules):
        if isinstance(tree, ParserRuleContext):
            rule_name = tree.parser.ruleNames[tree.getRuleIndex()]
            usedRules.add(rule_name)
        for i in range(tree.getChildCount()):
            child = tree.getChild(i)
            self.collect_used_rules(child, usedRules)

    def crosslimit(self):
        translate = {'define': '=', 'bracket': '@', 'naturallist': '< >', 'builtinCn': 'Cn', 'builtinPr': 'Pr', 'builtinMn': 'Mn'}
        usedRules = set()
        self.collect_used_rules(lastTree, usedRules)
        for element in usedRules:
            if element in self.limits:
                if element in translate.keys():
                    element = translate[element]
                typewriter(f'Using \'{element}\' is forbidden here.')
                return True
        return False

    def test(self):
        if len(self.target) == 0:
            typewriter('Good.')
            return True
        global intr
        syment = intr.symbol_table.table[-1]
        target = challengeFunctions[self.target]
        if syment.ftype.narg != target['narg']:
            typewriter(f'\'{self.target}\' gets {target["narg"]} arguments but \'{syment.symbol}\' gets {syment.ftype.narg} arguments!')
            return False
        if syment.ftype.nbase > 0:
            typewriter(f'\'{syment.symbol}\' is not a finished function.')
            return False
        for test in self.tests:
            args = []
            for numb in test:
                args.append(Natural(numb))
            args = NaturalList(args)
            expected = challengeFunctions[self.target]['func'](args)
            actual = syment.call([], args)
            if int(expected) != int(actual):
                typewriter(f'Oh, it\'s not working with input ({", ".join([str(n) for n in test])})')
                return False
        typewriter(f'Congraduations!')
        return True

    def run(self):
        typewriter(self.banner)
        global intr
        intr = Interpreter()
        for name in self.have:
            intr.symbol_table.add_entry(assumedFunctions[name])
        hist = ''
        while True:
            line = multiline_input()
            if not line.strip():
                continue
            if re.match(r'^\s*end\s*$', line):
                self.hintcounter = 0
                print()
                return
            if re.match(r'^\s*done\s*$', line):
                if self.test():
                    break
                continue
            if re.match(r'^\s*hint\s*$', line):
                if self.hintcounter >= len(self.hints):
                    typewriter('There is no more hint!' if self.hintcounter else 'There is no hint.')
                else:
                    typewriter(f'[Hint {self.hintcounter + 1}/{len(self.hints)}] {self.hints[self.hintcounter]}')
                    self.hintcounter += 1
                continue
            if re.match(r'^\s*list\s*$', line):
                out = []
                outstr = ''
                for fun in intr.symbol_table.table[::-1]:
                    if fun.symbol != 'S' and fun.symbol not in out:
                        outstr = ' ' + fun.symbol + (f'[{fun.ftype.nbase}]' if fun.ftype.nbase else f'({fun.ftype.narg})') + outstr
                        out.append(fun.symbol)
                print(f'{C_ORANGE}..{outstr}{C_RESET}\n')
                continue
            if self.crosslimit():
                continue
            ok, messages = intr.report(line)
            for msg in messages:
                if msg.typ == MessageType.NATURAL:
                    print(f' {C_GREEN}= {msg.natural}{C_RESET}')
                elif msg.typ == MessageType.INFO:
                    print(f' {C_ORANGE}. {msg.message}{C_RESET}')
                    hist += line.strip().replace(' ', '').replace('=', ' = ').replace(',', ', ') + '\n'
                elif msg.typ == MessageType.ERROR:
                    print(f' {C_RED}! ERROR: {msg.message}{C_RESET}')
                    if msg.context:
                        for ctx in msg.context:
                            print(C_RED + ' '*7 + ctx + C_RESET)
                elif msg.typ == MessageType.EXCEPTION:
                    print(f' {C_RED}* EXCEPTION: {msg.message}{C_RESET}')
            print()
        if self.target:
            self.journey.sidenotes.add_note(title=f'{self.starter}::solution ({self.target})', content=hist.strip())
        self.done = True


class Journey:
    def __init__(self, jsonfilepath: Path):
        self.username: str = ''
        self.sidenotes: SideNotes = SideNotes()
        self.acts: List[Act] = []
        self.writerContact = None
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
                        Challenge(self, act['starter'], prerequisites, act['target'], act['tests'], act['limits'], act['have'], act['hints'], act['banner'])
                    )
                elif act['type'] == 'writer-contact':
                    self.writerContact = {'fullname': act['fullname'], 'email': act['email']}
        self.session = PromptSession()

    def run(self):
        running = True
        while running:
            try:
                runnables_starters = []
                runnables = {}
                for act in self.acts:
                    if act.runnable():
                        runnables_starters.append(act.starter)
                        runnables[act.starter] = act
                commands = ['notes', 'contact', 'end'] + runnables_starters
                completer = SimpleCommandCompleter(commands, ignore_case=True)
                while True:
                    typewriter('Chose an option:', end='')
                    for starter in runnables_starters:
                        part1 = f' - {starter}' + ' '*20
                        part2 = runnables[starter].target if isinstance(runnables[starter], Challenge) else ''
                        print(part1[:20] + f'{C_GREY}{part2}{C_RESET}')
                    print(f' - notes            {C_GREY}to see notes{C_RESET}\n' +
                        f' - contact          {C_GREY}to see our contact information{C_RESET}\n'
                        f' - end              {C_GREY}to end this journey{C_RESET}\n')
                    cmd = self.session.prompt('$$ ', completer=completer).strip()
                    if cmd == 'notes':
                        self.sidenotes.run()
                    elif cmd == 'contact':
                        typewriter('RFPL core team:\n' +
                                '  Parsa Alizadeh [parsa.alizadeh1@gmail.com]\n' +  # just used the email address public in github
                                '  AmirMohammad Bandari Masoole [ambandarim@gmail.com]',
                                highlights=['parsa.alizadeh1@gmail.com', 'ambandarim@gmail.com'])
                        if self.writerContact and self.writerContact['email'] not in ['parsa.alizadeh1@gmail.com', 'ambandarim@gmail.com']:
                            typewriter('Language support:\n' +
                                    f'  {self.writerContact["fullname"]} [{self.writerContact["email"]}]',
                                    highlights=[self.writerContact['email']])
                    elif cmd == 'end':
                        running = False
                        break
                    elif cmd in runnables_starters:
                        break
                if cmd in runnables_starters:
                    runnables[cmd].run()
            except KeyboardInterrupt:
                pass
            except EOFError:
                running = False
                break

def main():
    jrny = Journey(Path(__file__).parent / 'journey_en.json')
    jrny.run()


if __name__ == '__main__':
    main()
