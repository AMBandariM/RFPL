# RFPL: Recursive Functional Programming Language

RFPL is a recursive functional programming language designed primarily for
educational purposes. It introduces the concept of primitive recursion—which you
can read about on
[Wikipedia](https://en.wikipedia.org/wiki/Primitive_recursive_function)—and can
also be used for non-educational purposes, such as for fun or challenges.

## Usage

### Installation

#### Latest from Github

Install ANTLR4. Clone the repository and use `make` to run RFPL:

```console
$ git clone https://github.com/AMBandariM/RFPL
$ cd RFPL
$ make          # Launch RFPL's interactive console
$ make journey  # Start "The RFPL Journey"
```

#### Stable from pip

Alternatively, you can install RFPL using pip:

```console
$ pip install rfpl
```

Then run:

```console
$ rfpl      # Launch RFPL's interactive console
$ journey   # Start "The RFPL Journey"
$ # or run with `python -m rfpl` and `python -m journey` if there was PATH errors.
```

### VSCode Syntax Highlighter
To enable syntax highlighting for RFPL files in VSCode:

1. Open the Extensions panel.
2. Search for `RFPL`.
3. Install the **RFPL Syntax Highlighter** extension, which provides
   highlighting for `.rfpl` files.

## Showcase

`journey` provides an introduction to recursive functions and the the syntax of
RFPL. Apart from the definitions of μ-recursive functions, the features of RFPL
described here make it distinct from similar implementations, potentially making
it an interesting esolang in its own.

<details>
<summary><h3>Every Value Is a Natural Number</h3></summary>

Assuming $0\in\mathbb{N}$, every value is of type $\mathbb{N}$.

``` clojure
>> 3
 = 3
>> _  ; undefined number representing a never-halting computation.
 = Undefined
```
</details>
<details>
<summary><h3>Native Gödel's Encoding</h3></summary>

Positive numbers can be represented as list of numbers based on their
prime factorization. RFPL supports lists as another representation for values.

``` clojure
>> <3, 1, 2>  ; equivalent to 2^3 * 3^1 * 5^2.
 = <3, 1, 2>
>> load basics
>> Int(<3, 1, 2>)  ; identity function. only changes the representation.
 = 600
```

Some of the basic operations are defined directly using the list encoding (like `Get` and
`Set` from basics library, or `Mul` and `Pow` for vector operations over lists).

This representation is very flexible, as numbers in a list can also be lists.
Thus, lists can be used similar to LISP (and the fact that 0 has no
factorization makes it a good candidate for `nil`). Many data structures can be
constructed and processed in this way (see [stack.rfpl](rfpl/lib/stack.rfpl)).

``` clojure
>> ;    3
   ;   / \
   ;  2   4
   ;     / \
   ;    5   7
>> <3, <2>, <4, <5>, <7>>>  ; one way to represent a tree
```
</details>
<details>
<summary><h3>Bases</h3></summary>

Second-order functions can be defined using a feature we call "base"; they take functions
as input and result in a function as an output.

``` clojure
>> map[Cn[S, S]](<3, 1, 2, 3>)  ; map a function over elements of a stack
 = <3, 3, 4, 5>
```

The syntax of the base allows to mimic the basic operators of RFPL (`Cn`, `Pr`,
and `Mn`).
</details>
<details>
<summary><h3>Function Type Check</h3></summary>

With the introduction of bases, RFPL implements a basic type check to avoid
errors before the evaluation.

``` clojure
>> foo = Cn[@0, #0]
>> bar = foo[!2]
 ! ERROR: Base @0 of function foo needs 3 arguments, but is limited to at most 1 argument by function foo
       bar = foo[!2]
             ^~~~~~~
```
</details>
<details>
<summary><h3>Lazy Evaluation</h3></summary>

RFPL is strict, although it allows some expressions to be evaluated lazily;
perhaps to improve performance or avoid unnecessary computation.

``` clojure
>> add = Pr[!0, Cn[S, !0]]
>> mul = Pr[#0, Cn[add, !2, !0]]
>> mul(0, mul(1000, 1000))  ; takes ~2 seconds
 = 0
>> mul(0, ~mul(1000, 1000))  ; instant
 = 0
```
</details>

## Development and Contribution
### Translating "The RFPL Journey"

You are welcome to translate the file `./journey/journey_en.json` into your native language. Submit your translation, if the translation meets our quality standards, we will include it in future releases with your name and contact information.

### Future Development

Although Version 1 of RFPL is complete and published, we have plans for future improvements:
- **Refactoring:** Extracting 'fundamental' functions from the interpreter.
- **User Experience:** Implementing a robust cache and function-guessing system.
- **Dependency Management:** Potentially removing ANTLR and other nonessential dependencies.

### Documentation
You have to experience the language and read the source code. There is no additional documentation at this time—sorry about that.

## Contact Information
- **Parsa Alizadeh** \[[parsa.alizadeh1@gmail.com](mailto:parsa.alizadeh1@gmail.com)\]

- **AmirMohammad Bandari Masoole** \[[ambandarim@gmail.com](mailto:ambandarim@gmail.com)\]

