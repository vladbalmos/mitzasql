# Naive autocomplete engine

Uses the parser to create a list of ASTs from an SQL string. The engine uses the last created AST node and its parents to determine the context in a statement and based on that, suggest schema object names and keywords.   
The engine has support for most of the Data Manipulation Statements and can provide a context for schema object name suggestions, for unsupported statements the engine falls back to dumb keyword suggestions.
