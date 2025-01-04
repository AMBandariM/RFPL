ANTLRFILES=rfpl/RFPLParser.py rfpl/RFPLLexer.py
PYFILES=$(wildcard rfpl/*.py)

run: ${PYFILES} ${ANTLRFILES}
	python -m rfpl
.PHONY: run

${ANTLRFILES}: RFPL.g4
	antlr4 -Dlanguage=Python3 -no-listener -no-visitor RFPL.g4 -o rfpl

clear:
	rm -f ${ANTLRFILES} rfpl/*.interp  rfpl/*.tokens
.PHONY: clear
