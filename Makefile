ANTLRFILES=rfpl/RFPLParser.py rfpl/RFPLLexer.py

run: ${ANTLRFILES}
	python -m rfpl
.PHONY: run

build: ${ANTLRFILES}
.PHONY: build

${ANTLRFILES}: RFPL.g4
	antlr4 -Dlanguage=Python3 -no-listener -no-visitor RFPL.g4 -o rfpl

clear:
	rm -f ${ANTLRFILES} rfpl/*.interp  rfpl/*.tokens
.PHONY: clear
