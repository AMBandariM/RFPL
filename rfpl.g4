grammar rfpl;

// Parser rules (start with lowercase)
line          : define
              | examine ;
define        : symbol '=' fexpr 
              | symbol '[' symbol symbollist ']' '=' fexpr ;
examine       : nexpr ;
symbollist    : /* epsilon */ 
              | ',' symbol symbollist ;
fexpr         : fexprleaf
              | builtinCn
              | builtinPr
              | builtinMn ;
fexprleaf     : symbol 
              | symbol '[' fexpr fexprlist ']' ;
builtinCn     : 'Cn' '[' fexpr fexprlist ']' ;
builtinPr     : 'Pr' '[' fexpr ',' fexpr ']' ;
builtinMn     : 'Mn' '[' fexpr ']' ;
fexprlist     : /* epsilon */ 
              | ',' fexpr fexprlist ;
nexpr         : fexpr '(' nexprlist ')' 
              | natural ;
nexprlist     : /* epsilon */ 
              | nexpr nexprlist2 ;
nexprlist2    : /* epsilon */ 
              | ',' nexpr nexprlist2 ;
natural       : number 
              | '[' naturallist ']' ;
naturallist   : /* epsilon */ 
              | natural naturallist2 ;
naturallist2  : /* epsilon */ 
              | ',' natural naturallist2 ;

// Lexer rules (start with uppercase)
number        : DIGIT* ;
symbol        : Symbol ;
Symbol        : [a-zA-Z_][a-zA-Z0-9_]* ;
DIGIT         : [0-9] ;
WS            : [ \t\r\n]+ -> skip ;  // Skip whitespace
