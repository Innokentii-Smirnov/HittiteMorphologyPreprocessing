class ParsingError(ValueError):

    arg_type = 'argument'
    
    def __init__(self, argument: str):
        self.argument = argument

    def __str__(self) -> str:
        return f"Cannot parse {self.arg_type}: '{self.argument}'"

class CannotParseStemClass(ParsingError):
    
    arg_type = 'stem class'


class CannotParseGrammForm(ParsingError):

    arg_type = 'grammatical form'


class CannotParseMorpholex(ParsingError):

    arg_type = 'morpholexemic representation'


class CannotParseFormSet(ParsingError):

    arg_type = 'grammatical form set'

class CannotParseWordform(ParsingError):

    arg_type = 'wordform'

class CannotParseSelection(ParsingError):

    arg_type = 'selection'

class CannotParseEnclChain(ParsingError):

    arg_type = 'enclitic chain'

class SecondaryParsingError(Exception):

    description = 'The following error occured while parsing:\n'

    def __init__(self, parsing_error: ParsingError):
        self.parsing_error = parsing_error

    def __str__(self) -> str:
        return self.description + str(self.parsing_error)

