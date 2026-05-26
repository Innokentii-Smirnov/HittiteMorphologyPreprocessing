from enum import Enum, auto

class Result(Enum):
    NOTE = auto()
    DELIN = auto()
    DELFIN = auto()
    SPACE = auto()
    SIGN = auto()
    DET = auto()
    OTHER = auto()
    DEL = auto()
    NOSEL = auto()
    EMPTYSEL = auto()
    NOTRANS = auto()

import re
from bs4 import Tag
#pat = re.compile(r'mrp\d')

def check_wordform(wordform: Tag, trans: str, mrp: str) -> Result | None:
    #count = sum(1 for key in wordform.attrs if pat.fullmatch(key))
    if trans not in wordform.attrs:
        if mrp not in wordform.attrs:
            contents = wordform.contents
            elems = tuple(elem.name if isinstance(elem, Tag) else None for elem in contents)
            match elems:
                case ('del_in',) | ('del_in', 'note'):
                    return Result.DELIN
                case ('del_fin',) | ('del_fin', 'note'):
                    return Result.DELFIN
                case 'note',:
                    return Result.NOTE
                case 'space',:
                    return Result.SPACE
                case 'c',:
                    assert wordform.c is not None
                    match wordform.c['type']:
                        case 'sign':
                            return Result.SIGN
                case 'd',:
                    return Result.DET
                case _:
                    return Result.OTHER
        else:
            if wordform[mrp] == 'DEL':
                return Result.DEL
            else:
                return Result.NOTRANS
    else:
        if mrp not in wordform.attrs:
            return Result.NOSEL
        elif wordform[mrp] == '':
            return Result.EMPTYSEL
        elif wordform[mrp] == 'DEL':
            return Result.DEL
    return None
