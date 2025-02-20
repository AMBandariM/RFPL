grammar RFPL;

// Parser rules (start with lowercase)
singleline    : line? EOF ;
line          : define
              | examine
              | pragma ;
pragma        : load ;
load          : 'load' module ;
module        : Symbol ('.' Symbol)* ;
define        : Symbol '=' fexpr ;
examine       : nexpr ;
symbollist    : Symbol (',' Symbol)* ;
fexpr         : fexprleaf
              | builtinCn
              | builtinPr
              | builtinMn
              | builtinFix
              | identity
              | constant
              | bracket ;
fexprleaf     : Lazy? Symbol
              | Lazy? Symbol '[' fexprlist ']' ;
fexprlist     : fexpr (',' fexpr)* ;
builtinCn     : Lazy? 'Cn' '[' fexprlist identityRest ']' ;
identityRest  : ',' '!' Number '..' | ;
builtinPr     : Lazy? 'Pr' '[' fexpr ',' fexpr ']' ;
builtinMn     : Lazy? 'Mn' '[' fexpr ']' ;
builtinFix    : Lazy? 'Fix' '{' fexpr '}' ('[' fexprlist ']')? ;
identity      : '!' Number ;
constant      : '#' natural ;
bracket       : Lazy? '@' Number ;
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
Lazy          : '~' ;
Number        : [0-9]+ ;
Symbol        : [-a-zA-Z_][-a-zA-Z0-9_]* ;
Whitespace    : [ \t\r\n]+ -> channel(HIDDEN) ;  // Skip whitespace
Comment       : ';' ~[\n]* -> channel(HIDDEN) ;
Unknown       : . ;
