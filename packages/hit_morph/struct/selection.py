import re
from gen_morph.exceptions import CannotParseSelection
from library.serializable import Serializable, SerializableList
String = str | None

class Selection(Serializable):
    selection_pattern = re.compile(r'(\d+)([a-z]+)?([A-Z]+)?')
    sep = '.'

    def get_elements(self) -> tuple[int, String, String]:
        return self.lexeme, self.gramm_form, self.encl_chain

    @classmethod
    def from_strings(cls, lexeme: str, gramm_form: str, encl_chain: str):
        return cls(int(lexeme), gramm_form, encl_chain)

    def __init__(self, lexeme: int, gramm_form: String, encl_chain: String):
        self.lexeme = lexeme
        self.gramm_form = gramm_form
        self.encl_chain = encl_chain

    @classmethod
    def parse_string(cls, selection: str):
        matched = cls.selection_pattern.fullmatch(selection)
        if matched is not None:
            lexeme, gramm_form, encl_chain = matched.groups()
            return cls.from_strings(lexeme, gramm_form, encl_chain)
        else:
            raise CannotParseSelection(selection)
    
    def __str__(self):
        string = str(self.lexeme)
        if self.gramm_form is not None:
            string += self.gramm_form
        if self.encl_chain is not None:
            string += self.encl_chain
        return string
    

class SelectionList(SerializableList):
    sep = ' '
    get_element = Selection.from_string
