# Generated from rfpl.g4 by ANTLR 4.13.2
from antlr4 import *
if "." in __name__:
    from .rfplParser import rfplParser
else:
    from rfplParser import rfplParser

# This class defines a complete listener for a parse tree produced by rfplParser.
class rfplListener(ParseTreeListener):

    # Enter a parse tree produced by rfplParser#line.
    def enterLine(self, ctx:rfplParser.LineContext):
        pass

    # Exit a parse tree produced by rfplParser#line.
    def exitLine(self, ctx:rfplParser.LineContext):
        pass


    # Enter a parse tree produced by rfplParser#define.
    def enterDefine(self, ctx:rfplParser.DefineContext):
        pass

    # Exit a parse tree produced by rfplParser#define.
    def exitDefine(self, ctx:rfplParser.DefineContext):
        pass


    # Enter a parse tree produced by rfplParser#examine.
    def enterExamine(self, ctx:rfplParser.ExamineContext):
        pass

    # Exit a parse tree produced by rfplParser#examine.
    def exitExamine(self, ctx:rfplParser.ExamineContext):
        pass


    # Enter a parse tree produced by rfplParser#symbollist.
    def enterSymbollist(self, ctx:rfplParser.SymbollistContext):
        pass

    # Exit a parse tree produced by rfplParser#symbollist.
    def exitSymbollist(self, ctx:rfplParser.SymbollistContext):
        pass


    # Enter a parse tree produced by rfplParser#fexpr.
    def enterFexpr(self, ctx:rfplParser.FexprContext):
        pass

    # Exit a parse tree produced by rfplParser#fexpr.
    def exitFexpr(self, ctx:rfplParser.FexprContext):
        pass


    # Enter a parse tree produced by rfplParser#fexprlist.
    def enterFexprlist(self, ctx:rfplParser.FexprlistContext):
        pass

    # Exit a parse tree produced by rfplParser#fexprlist.
    def exitFexprlist(self, ctx:rfplParser.FexprlistContext):
        pass


    # Enter a parse tree produced by rfplParser#nexpr.
    def enterNexpr(self, ctx:rfplParser.NexprContext):
        pass

    # Exit a parse tree produced by rfplParser#nexpr.
    def exitNexpr(self, ctx:rfplParser.NexprContext):
        pass


    # Enter a parse tree produced by rfplParser#nexprlist.
    def enterNexprlist(self, ctx:rfplParser.NexprlistContext):
        pass

    # Exit a parse tree produced by rfplParser#nexprlist.
    def exitNexprlist(self, ctx:rfplParser.NexprlistContext):
        pass


    # Enter a parse tree produced by rfplParser#nexprlist2.
    def enterNexprlist2(self, ctx:rfplParser.Nexprlist2Context):
        pass

    # Exit a parse tree produced by rfplParser#nexprlist2.
    def exitNexprlist2(self, ctx:rfplParser.Nexprlist2Context):
        pass


    # Enter a parse tree produced by rfplParser#natural.
    def enterNatural(self, ctx:rfplParser.NaturalContext):
        pass

    # Exit a parse tree produced by rfplParser#natural.
    def exitNatural(self, ctx:rfplParser.NaturalContext):
        pass


    # Enter a parse tree produced by rfplParser#naturallist.
    def enterNaturallist(self, ctx:rfplParser.NaturallistContext):
        pass

    # Exit a parse tree produced by rfplParser#naturallist.
    def exitNaturallist(self, ctx:rfplParser.NaturallistContext):
        pass


    # Enter a parse tree produced by rfplParser#naturallist2.
    def enterNaturallist2(self, ctx:rfplParser.Naturallist2Context):
        pass

    # Exit a parse tree produced by rfplParser#naturallist2.
    def exitNaturallist2(self, ctx:rfplParser.Naturallist2Context):
        pass


    # Enter a parse tree produced by rfplParser#number.
    def enterNumber(self, ctx:rfplParser.NumberContext):
        pass

    # Exit a parse tree produced by rfplParser#number.
    def exitNumber(self, ctx:rfplParser.NumberContext):
        pass


    # Enter a parse tree produced by rfplParser#symbol.
    def enterSymbol(self, ctx:rfplParser.SymbolContext):
        pass

    # Exit a parse tree produced by rfplParser#symbol.
    def exitSymbol(self, ctx:rfplParser.SymbolContext):
        pass



del rfplParser