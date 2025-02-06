# RFPL: Recursive Functional Programming Language

RFPL is a recursive functional programming language designed primarily for educational purposes. It introduces the concept of primitive recursion—which you can read about on [Wikipedia](https://en.wikipedia.org/wiki/Primitive_recursive_function)—and can also be used for non-educational purposes, such as for fun or challenges.

## Usage

### Installation

#### Easy Way

Clone the repository and use `make` to run RFPL:

```console
$ git clone https://github.com/AMBandariM/RFPL
$ cd RFPL
$ make          # Launch RFPL's interactive console
$ make journey  # Start "The RFPL Journey"
```

#### Easier Way

Alternatively, you can install RFPL using pip:

```console
$ pip install rfpl
```

Then run:

```console
$ python -m rfpl    # Launch RFPL's interactive console
$ python -m journey # Start "The RFPL Journey"
```

### VSCode Syntax Highlighter
To enable syntax highlighting for RFPL files in VSCode:

1. Open the Extensions panel.
2. Search for `RFPL`.
3. Install the **RFPL Syntax Highlighter** extension, which provides highlighting for `.rfpl` files.

## Development and Contribution
### Translating "The RFPL Journey"

You are welcome to translate the file `./journey/journey_en.json` into your native language. Submit your translation, if the translation meets our quality standards, we will include it in future releases with your name and contact information.

### Future Development

Although Version 1 of RFPL is complete and published, we have plans for future improvements:
- **Refactoring:** Extracting 'fundamental' functions from the interpreter.
- **User Experience:** Implementing a robust cache and function-gessing system.
- **Dependency Management:** Potentially removing ANTLR and other nonessential dependencies.

### Documentation
You have to experience the language and read the source code. There is no additional documentation at this time—sorry about that.

## Contact Information
- **Parsa Alizadeh** \[[parsa.alizadeh1@gmail.com](mailto:parsa.alizadeh1@gmail.com)\]

- **AmirMohammad Bandari Masoole** \[[ambandarim@gmail.com](mailto:ambandarim@gmail.com)\]

