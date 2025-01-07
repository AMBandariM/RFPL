grammar RFPL;

// Parser rules (start with lowercase)
line          : define EOF
              | examine EOF
              | EOF ;
define        : Symbol '=' fexpr ;
examine       : nexpr ;
symbollist    : Symbol (',' Symbol)* ;
fexpr         : fexprleaf
              | builtinCn
              | builtinPr
              | builtinMn
              | identity
              | constant
              | bracket ;
fexprleaf     : Symbol
              | Symbol '[' fexprlist ']' ;
fexprlist     : fexpr (',' fexpr)* ;
builtinCn     : 'Cn' '[' fexprlist ']' ;
builtinPr     : 'Pr' '[' fexpr ',' fexpr ']' ;
builtinMn     : 'Mn' '[' fexpr ']' ;
identity      : '!' Number ;
constant      : '#' natural ;
bracket       : '@' Number ;
nexpr         : fexpr '(' nexprlist ')' 
              | natural ;
nexprlist     : /* epsilon */ 
              | nexpr (',' nexpr)* ;
natural       : Number 
              | '<' naturallist '>'
              | '_' ;   /* similar to bottom symbol */
naturallist   : /* epsilon */ 
              | natural (',' natural)* ;

// Lexer rules (start with uppercase)
Number        : [0-9]+ ;
Symbol        : [-a-zA-Z_][-a-zA-Z0-9_]* ;
Whitespace    : [ \t\r\n]+ -> skip ;  // Skip whitespace
Comment       : '/*' .*? '*/' -> skip ;
