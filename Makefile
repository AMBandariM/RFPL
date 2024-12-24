run: main.py rfplParser.py rfplLexer.py rfplListener.py
	python main.py
.PHONY: run

rfplParser.py rfplLexer.py rfplListener.py: rfpl.g4
	antlr4 -Dlanguage=Python3 rfpl.g4
