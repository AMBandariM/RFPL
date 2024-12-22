# Generated from rfpl.g4 by ANTLR 4.13.2
# encoding: utf-8
from antlr4 import *
from io import StringIO
import sys
if sys.version_info[1] > 5:
	from typing import TextIO
else:
	from typing.io import TextIO

def serializedATN():
    return [
        4,1,15,142,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,2,5,7,5,2,6,7,
        6,2,7,7,7,2,8,7,8,2,9,7,9,2,10,7,10,2,11,7,11,2,12,7,12,2,13,7,13,
        1,0,1,0,3,0,31,8,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
        1,3,1,45,8,1,1,2,1,2,1,3,1,3,1,3,1,3,1,3,3,3,54,8,3,1,4,1,4,1,4,
        1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,
        1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,3,4,84,8,4,1,5,1,5,1,5,1,5,1,
        5,3,5,91,8,5,1,6,1,6,1,6,1,6,1,6,1,6,3,6,99,8,6,1,7,1,7,1,7,1,7,
        3,7,105,8,7,1,8,1,8,1,8,1,8,1,8,3,8,112,8,8,1,9,1,9,1,9,1,9,1,9,
        3,9,119,8,9,1,10,1,10,1,10,1,10,3,10,125,8,10,1,11,1,11,1,11,1,11,
        1,11,3,11,132,8,11,1,12,5,12,135,8,12,10,12,12,12,138,9,12,1,13,
        1,13,1,13,0,0,14,0,2,4,6,8,10,12,14,16,18,20,22,24,26,0,0,145,0,
        30,1,0,0,0,2,44,1,0,0,0,4,46,1,0,0,0,6,53,1,0,0,0,8,83,1,0,0,0,10,
        90,1,0,0,0,12,98,1,0,0,0,14,104,1,0,0,0,16,111,1,0,0,0,18,118,1,
        0,0,0,20,124,1,0,0,0,22,131,1,0,0,0,24,136,1,0,0,0,26,139,1,0,0,
        0,28,31,3,2,1,0,29,31,3,4,2,0,30,28,1,0,0,0,30,29,1,0,0,0,31,1,1,
        0,0,0,32,33,3,26,13,0,33,34,5,1,0,0,34,35,3,8,4,0,35,45,1,0,0,0,
        36,37,3,26,13,0,37,38,5,2,0,0,38,39,3,26,13,0,39,40,3,6,3,0,40,41,
        5,3,0,0,41,42,5,1,0,0,42,43,3,8,4,0,43,45,1,0,0,0,44,32,1,0,0,0,
        44,36,1,0,0,0,45,3,1,0,0,0,46,47,3,12,6,0,47,5,1,0,0,0,48,54,1,0,
        0,0,49,50,5,4,0,0,50,51,3,26,13,0,51,52,3,6,3,0,52,54,1,0,0,0,53,
        48,1,0,0,0,53,49,1,0,0,0,54,7,1,0,0,0,55,84,3,26,13,0,56,57,3,26,
        13,0,57,58,5,2,0,0,58,59,3,8,4,0,59,60,3,10,5,0,60,61,5,3,0,0,61,
        84,1,0,0,0,62,84,5,11,0,0,63,84,5,12,0,0,64,65,5,5,0,0,65,66,5,2,
        0,0,66,67,3,8,4,0,67,68,3,10,5,0,68,69,5,3,0,0,69,84,1,0,0,0,70,
        71,5,6,0,0,71,72,5,2,0,0,72,73,3,8,4,0,73,74,5,4,0,0,74,75,3,8,4,
        0,75,76,5,3,0,0,76,84,1,0,0,0,77,78,5,7,0,0,78,79,5,2,0,0,79,80,
        3,8,4,0,80,81,5,3,0,0,81,84,1,0,0,0,82,84,5,8,0,0,83,55,1,0,0,0,
        83,56,1,0,0,0,83,62,1,0,0,0,83,63,1,0,0,0,83,64,1,0,0,0,83,70,1,
        0,0,0,83,77,1,0,0,0,83,82,1,0,0,0,84,9,1,0,0,0,85,91,1,0,0,0,86,
        87,5,4,0,0,87,88,3,8,4,0,88,89,3,10,5,0,89,91,1,0,0,0,90,85,1,0,
        0,0,90,86,1,0,0,0,91,11,1,0,0,0,92,93,3,8,4,0,93,94,5,9,0,0,94,95,
        3,14,7,0,95,96,5,10,0,0,96,99,1,0,0,0,97,99,3,18,9,0,98,92,1,0,0,
        0,98,97,1,0,0,0,99,13,1,0,0,0,100,105,1,0,0,0,101,102,3,12,6,0,102,
        103,3,16,8,0,103,105,1,0,0,0,104,100,1,0,0,0,104,101,1,0,0,0,105,
        15,1,0,0,0,106,112,1,0,0,0,107,108,5,4,0,0,108,109,3,12,6,0,109,
        110,3,16,8,0,110,112,1,0,0,0,111,106,1,0,0,0,111,107,1,0,0,0,112,
        17,1,0,0,0,113,119,3,24,12,0,114,115,5,2,0,0,115,116,3,20,10,0,116,
        117,5,3,0,0,117,119,1,0,0,0,118,113,1,0,0,0,118,114,1,0,0,0,119,
        19,1,0,0,0,120,125,1,0,0,0,121,122,3,18,9,0,122,123,3,22,11,0,123,
        125,1,0,0,0,124,120,1,0,0,0,124,121,1,0,0,0,125,21,1,0,0,0,126,132,
        1,0,0,0,127,128,5,4,0,0,128,129,3,18,9,0,129,130,3,22,11,0,130,132,
        1,0,0,0,131,126,1,0,0,0,131,127,1,0,0,0,132,23,1,0,0,0,133,135,5,
        14,0,0,134,133,1,0,0,0,135,138,1,0,0,0,136,134,1,0,0,0,136,137,1,
        0,0,0,137,25,1,0,0,0,138,136,1,0,0,0,139,140,5,13,0,0,140,27,1,0,
        0,0,12,30,44,53,83,90,98,104,111,118,124,131,136
    ]

class rfplParser ( Parser ):

    grammarFileName = "rfpl.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "'='", "'['", "']'", "','", "'Cn'", "'Pr'", 
                     "'Mn'", "'S'", "'('", "')'" ]

    symbolicNames = [ "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "Idnumber", 
                      "Cnumber", "Symbol", "DIGIT", "WS" ]

    RULE_line = 0
    RULE_define = 1
    RULE_examine = 2
    RULE_symbollist = 3
    RULE_fexpr = 4
    RULE_fexprlist = 5
    RULE_nexpr = 6
    RULE_nexprlist = 7
    RULE_nexprlist2 = 8
    RULE_natural = 9
    RULE_naturallist = 10
    RULE_naturallist2 = 11
    RULE_number = 12
    RULE_symbol = 13

    ruleNames =  [ "line", "define", "examine", "symbollist", "fexpr", "fexprlist", 
                   "nexpr", "nexprlist", "nexprlist2", "natural", "naturallist", 
                   "naturallist2", "number", "symbol" ]

    EOF = Token.EOF
    T__0=1
    T__1=2
    T__2=3
    T__3=4
    T__4=5
    T__5=6
    T__6=7
    T__7=8
    T__8=9
    T__9=10
    Idnumber=11
    Cnumber=12
    Symbol=13
    DIGIT=14
    WS=15

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.13.2")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class LineContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def define(self):
            return self.getTypedRuleContext(rfplParser.DefineContext,0)


        def examine(self):
            return self.getTypedRuleContext(rfplParser.ExamineContext,0)


        def getRuleIndex(self):
            return rfplParser.RULE_line

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterLine" ):
                listener.enterLine(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitLine" ):
                listener.exitLine(self)




    def line(self):

        localctx = rfplParser.LineContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_line)
        try:
            self.state = 30
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,0,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 28
                self.define()
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 29
                self.examine()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class DefineContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def symbol(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(rfplParser.SymbolContext)
            else:
                return self.getTypedRuleContext(rfplParser.SymbolContext,i)


        def fexpr(self):
            return self.getTypedRuleContext(rfplParser.FexprContext,0)


        def symbollist(self):
            return self.getTypedRuleContext(rfplParser.SymbollistContext,0)


        def getRuleIndex(self):
            return rfplParser.RULE_define

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterDefine" ):
                listener.enterDefine(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitDefine" ):
                listener.exitDefine(self)




    def define(self):

        localctx = rfplParser.DefineContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_define)
        try:
            self.state = 44
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,1,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 32
                self.symbol()
                self.state = 33
                self.match(rfplParser.T__0)
                self.state = 34
                self.fexpr()
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 36
                self.symbol()
                self.state = 37
                self.match(rfplParser.T__1)
                self.state = 38
                self.symbol()
                self.state = 39
                self.symbollist()
                self.state = 40
                self.match(rfplParser.T__2)
                self.state = 41
                self.match(rfplParser.T__0)
                self.state = 42
                self.fexpr()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ExamineContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def nexpr(self):
            return self.getTypedRuleContext(rfplParser.NexprContext,0)


        def getRuleIndex(self):
            return rfplParser.RULE_examine

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterExamine" ):
                listener.enterExamine(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitExamine" ):
                listener.exitExamine(self)




    def examine(self):

        localctx = rfplParser.ExamineContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_examine)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 46
            self.nexpr()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class SymbollistContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def symbol(self):
            return self.getTypedRuleContext(rfplParser.SymbolContext,0)


        def symbollist(self):
            return self.getTypedRuleContext(rfplParser.SymbollistContext,0)


        def getRuleIndex(self):
            return rfplParser.RULE_symbollist

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterSymbollist" ):
                listener.enterSymbollist(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitSymbollist" ):
                listener.exitSymbollist(self)




    def symbollist(self):

        localctx = rfplParser.SymbollistContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_symbollist)
        try:
            self.state = 53
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [3]:
                self.enterOuterAlt(localctx, 1)

                pass
            elif token in [4]:
                self.enterOuterAlt(localctx, 2)
                self.state = 49
                self.match(rfplParser.T__3)
                self.state = 50
                self.symbol()
                self.state = 51
                self.symbollist()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class FexprContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def symbol(self):
            return self.getTypedRuleContext(rfplParser.SymbolContext,0)


        def fexpr(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(rfplParser.FexprContext)
            else:
                return self.getTypedRuleContext(rfplParser.FexprContext,i)


        def fexprlist(self):
            return self.getTypedRuleContext(rfplParser.FexprlistContext,0)


        def Idnumber(self):
            return self.getToken(rfplParser.Idnumber, 0)

        def Cnumber(self):
            return self.getToken(rfplParser.Cnumber, 0)

        def getRuleIndex(self):
            return rfplParser.RULE_fexpr

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterFexpr" ):
                listener.enterFexpr(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitFexpr" ):
                listener.exitFexpr(self)




    def fexpr(self):

        localctx = rfplParser.FexprContext(self, self._ctx, self.state)
        self.enterRule(localctx, 8, self.RULE_fexpr)
        try:
            self.state = 83
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,3,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 55
                self.symbol()
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 56
                self.symbol()
                self.state = 57
                self.match(rfplParser.T__1)
                self.state = 58
                self.fexpr()
                self.state = 59
                self.fexprlist()
                self.state = 60
                self.match(rfplParser.T__2)
                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 62
                self.match(rfplParser.Idnumber)
                pass

            elif la_ == 4:
                self.enterOuterAlt(localctx, 4)
                self.state = 63
                self.match(rfplParser.Cnumber)
                pass

            elif la_ == 5:
                self.enterOuterAlt(localctx, 5)
                self.state = 64
                self.match(rfplParser.T__4)
                self.state = 65
                self.match(rfplParser.T__1)
                self.state = 66
                self.fexpr()
                self.state = 67
                self.fexprlist()
                self.state = 68
                self.match(rfplParser.T__2)
                pass

            elif la_ == 6:
                self.enterOuterAlt(localctx, 6)
                self.state = 70
                self.match(rfplParser.T__5)
                self.state = 71
                self.match(rfplParser.T__1)
                self.state = 72
                self.fexpr()
                self.state = 73
                self.match(rfplParser.T__3)
                self.state = 74
                self.fexpr()
                self.state = 75
                self.match(rfplParser.T__2)
                pass

            elif la_ == 7:
                self.enterOuterAlt(localctx, 7)
                self.state = 77
                self.match(rfplParser.T__6)
                self.state = 78
                self.match(rfplParser.T__1)
                self.state = 79
                self.fexpr()
                self.state = 80
                self.match(rfplParser.T__2)
                pass

            elif la_ == 8:
                self.enterOuterAlt(localctx, 8)
                self.state = 82
                self.match(rfplParser.T__7)
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class FexprlistContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def fexpr(self):
            return self.getTypedRuleContext(rfplParser.FexprContext,0)


        def fexprlist(self):
            return self.getTypedRuleContext(rfplParser.FexprlistContext,0)


        def getRuleIndex(self):
            return rfplParser.RULE_fexprlist

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterFexprlist" ):
                listener.enterFexprlist(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitFexprlist" ):
                listener.exitFexprlist(self)




    def fexprlist(self):

        localctx = rfplParser.FexprlistContext(self, self._ctx, self.state)
        self.enterRule(localctx, 10, self.RULE_fexprlist)
        try:
            self.state = 90
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [3]:
                self.enterOuterAlt(localctx, 1)

                pass
            elif token in [4]:
                self.enterOuterAlt(localctx, 2)
                self.state = 86
                self.match(rfplParser.T__3)
                self.state = 87
                self.fexpr()
                self.state = 88
                self.fexprlist()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class NexprContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def fexpr(self):
            return self.getTypedRuleContext(rfplParser.FexprContext,0)


        def nexprlist(self):
            return self.getTypedRuleContext(rfplParser.NexprlistContext,0)


        def natural(self):
            return self.getTypedRuleContext(rfplParser.NaturalContext,0)


        def getRuleIndex(self):
            return rfplParser.RULE_nexpr

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterNexpr" ):
                listener.enterNexpr(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitNexpr" ):
                listener.exitNexpr(self)




    def nexpr(self):

        localctx = rfplParser.NexprContext(self, self._ctx, self.state)
        self.enterRule(localctx, 12, self.RULE_nexpr)
        try:
            self.state = 98
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [5, 6, 7, 8, 11, 12, 13]:
                self.enterOuterAlt(localctx, 1)
                self.state = 92
                self.fexpr()
                self.state = 93
                self.match(rfplParser.T__8)
                self.state = 94
                self.nexprlist()
                self.state = 95
                self.match(rfplParser.T__9)
                pass
            elif token in [-1, 2, 4, 10, 14]:
                self.enterOuterAlt(localctx, 2)
                self.state = 97
                self.natural()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class NexprlistContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def nexpr(self):
            return self.getTypedRuleContext(rfplParser.NexprContext,0)


        def nexprlist2(self):
            return self.getTypedRuleContext(rfplParser.Nexprlist2Context,0)


        def getRuleIndex(self):
            return rfplParser.RULE_nexprlist

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterNexprlist" ):
                listener.enterNexprlist(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitNexprlist" ):
                listener.exitNexprlist(self)




    def nexprlist(self):

        localctx = rfplParser.NexprlistContext(self, self._ctx, self.state)
        self.enterRule(localctx, 14, self.RULE_nexprlist)
        try:
            self.state = 104
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,6,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)

                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 101
                self.nexpr()
                self.state = 102
                self.nexprlist2()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Nexprlist2Context(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def nexpr(self):
            return self.getTypedRuleContext(rfplParser.NexprContext,0)


        def nexprlist2(self):
            return self.getTypedRuleContext(rfplParser.Nexprlist2Context,0)


        def getRuleIndex(self):
            return rfplParser.RULE_nexprlist2

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterNexprlist2" ):
                listener.enterNexprlist2(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitNexprlist2" ):
                listener.exitNexprlist2(self)




    def nexprlist2(self):

        localctx = rfplParser.Nexprlist2Context(self, self._ctx, self.state)
        self.enterRule(localctx, 16, self.RULE_nexprlist2)
        try:
            self.state = 111
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [10]:
                self.enterOuterAlt(localctx, 1)

                pass
            elif token in [4]:
                self.enterOuterAlt(localctx, 2)
                self.state = 107
                self.match(rfplParser.T__3)
                self.state = 108
                self.nexpr()
                self.state = 109
                self.nexprlist2()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class NaturalContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def number(self):
            return self.getTypedRuleContext(rfplParser.NumberContext,0)


        def naturallist(self):
            return self.getTypedRuleContext(rfplParser.NaturallistContext,0)


        def getRuleIndex(self):
            return rfplParser.RULE_natural

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterNatural" ):
                listener.enterNatural(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitNatural" ):
                listener.exitNatural(self)




    def natural(self):

        localctx = rfplParser.NaturalContext(self, self._ctx, self.state)
        self.enterRule(localctx, 18, self.RULE_natural)
        try:
            self.state = 118
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [-1, 3, 4, 10, 14]:
                self.enterOuterAlt(localctx, 1)
                self.state = 113
                self.number()
                pass
            elif token in [2]:
                self.enterOuterAlt(localctx, 2)
                self.state = 114
                self.match(rfplParser.T__1)
                self.state = 115
                self.naturallist()
                self.state = 116
                self.match(rfplParser.T__2)
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class NaturallistContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def natural(self):
            return self.getTypedRuleContext(rfplParser.NaturalContext,0)


        def naturallist2(self):
            return self.getTypedRuleContext(rfplParser.Naturallist2Context,0)


        def getRuleIndex(self):
            return rfplParser.RULE_naturallist

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterNaturallist" ):
                listener.enterNaturallist(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitNaturallist" ):
                listener.exitNaturallist(self)




    def naturallist(self):

        localctx = rfplParser.NaturallistContext(self, self._ctx, self.state)
        self.enterRule(localctx, 20, self.RULE_naturallist)
        try:
            self.state = 124
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,9,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)

                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 121
                self.natural()
                self.state = 122
                self.naturallist2()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Naturallist2Context(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def natural(self):
            return self.getTypedRuleContext(rfplParser.NaturalContext,0)


        def naturallist2(self):
            return self.getTypedRuleContext(rfplParser.Naturallist2Context,0)


        def getRuleIndex(self):
            return rfplParser.RULE_naturallist2

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterNaturallist2" ):
                listener.enterNaturallist2(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitNaturallist2" ):
                listener.exitNaturallist2(self)




    def naturallist2(self):

        localctx = rfplParser.Naturallist2Context(self, self._ctx, self.state)
        self.enterRule(localctx, 22, self.RULE_naturallist2)
        try:
            self.state = 131
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [3]:
                self.enterOuterAlt(localctx, 1)

                pass
            elif token in [4]:
                self.enterOuterAlt(localctx, 2)
                self.state = 127
                self.match(rfplParser.T__3)
                self.state = 128
                self.natural()
                self.state = 129
                self.naturallist2()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class NumberContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def DIGIT(self, i:int=None):
            if i is None:
                return self.getTokens(rfplParser.DIGIT)
            else:
                return self.getToken(rfplParser.DIGIT, i)

        def getRuleIndex(self):
            return rfplParser.RULE_number

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterNumber" ):
                listener.enterNumber(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitNumber" ):
                listener.exitNumber(self)




    def number(self):

        localctx = rfplParser.NumberContext(self, self._ctx, self.state)
        self.enterRule(localctx, 24, self.RULE_number)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 136
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==14:
                self.state = 133
                self.match(rfplParser.DIGIT)
                self.state = 138
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class SymbolContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Symbol(self):
            return self.getToken(rfplParser.Symbol, 0)

        def getRuleIndex(self):
            return rfplParser.RULE_symbol

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterSymbol" ):
                listener.enterSymbol(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitSymbol" ):
                listener.exitSymbol(self)




    def symbol(self):

        localctx = rfplParser.SymbolContext(self, self._ctx, self.state)
        self.enterRule(localctx, 26, self.RULE_symbol)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 139
            self.match(rfplParser.Symbol)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx





