# Disclaimer
SQL Parser written specifically for the autocomplete engine.   
The parser doesn't do semantic validation or error checking, its only purpose is to create a simple AST to be used for context detection during autocomplete.   
This is my first implementation of a language parser thus it's unoptimized and it certantly has its fair share of bugs. I strongly discourage using this for serious SQL parsing, there are better alternatives out there.

# Structure

- lexer.py
    - parse string into tokens
- parser.py
    - entry point of this package. uses the lexer to tokenize a string and then converts the tokens into a list of ASTs using parser classes defined in `parsers/`
- state.py
    - parser state
- tokens.py
    - collection of token types
- keywords.py
    - mapping of mysql keywords to token types
    - list of valid operators
- ast.py
    - collection of AST node types
- parsers/
    - parser classes
    - each type of statement has its own parser class
