run: main.py rfplParser.py rfplLexer.py rfplVisitor.py
	python main.py
.PHONY: run

rfplParser.py rfplLexer.py rfplVisitor.py: rfpl.g4
	antlr4 -Dlanguage=Python3 rfpl.g4 -no-listener -visitor

clear:
	rm -f rfplParser.py rfplLexer.py *.inerp *.tokens
.PHONY: clear
