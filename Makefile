ANTLRFILES=rfpl/RFPLParser.py rfpl/RFPLLexer.py

run: ${ANTLRFILES}
	python -m rfpl
.PHONY: run

journey: ${ANTLRFILES}
	python -m journey
.PHONY: journey

dist: ${ANTLRFILES}
	rm -rf build/ dist/
	python tests/test_general.py
	python -m build --wheel
.PHONY: dist

${ANTLRFILES}: RFPL.g4
	antlr4 -Dlanguage=Python3 -no-listener -no-visitor RFPL.g4 -o rfpl

clear:
	rm -rf ${ANTLRFILES} rfpl/*.interp  rfpl/*.tokens build/ dist/
.PHONY: clear
