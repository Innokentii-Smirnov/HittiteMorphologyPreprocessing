import re
from re import Pattern
from udapi.core.feats import Feats
import os
from os import path
from ..enumerations import Lang, Pos
from .. import RESOURCES_DIRECTORY
from gen_morph.exceptions import CannotParseStemClass
import library
from library import padding
from library.read import read_list
from library.exceptions import InitializationError
from functools import partial

pad = partial(padding.pad, None, 5)

library.default_dir = None

direct = path.join(RESOURCES_DIRECTORY, 'Stem classes')
os.chdir(direct)

patterns = list[tuple[tuple[Lang, Pos, Feats], Pattern]]()

for folder in os.listdir(direct):

    match folder.split('-'):
        case str_lang, prefix:
            pass
        case str_lang,:
            prefix = None
        case _:
            raise InitializationError()
    
    lang = Lang[str_lang]

    for filename in os.listdir(folder):

        match filename.removesuffix('.txt').split('-'):
            case str_pos, str_feats:
                feats = Feats(str_feats.replace(';', '|'))
            case str_pos,:
                feats = Feats()
            case _:
                raise InitializationError()
        
        pos = Pos[str_pos]
        expression = '|'.join(map(lambda x: x.replace('.', r'\.'),
                                          read_list(path.join(folder, filename))))
        if prefix is not None:
            expression = r'{0}\.({1})'.format(prefix, expression)
        
        pattern = re.compile(expression)
        elem = ((lang, pos, feats), pattern)
        patterns.append(elem)


def parse_stem_class(stem_class) -> tuple[Lang, Pos, Feats]:

    for result, pattern in patterns:
        if pattern.match(stem_class):
            return result
    
    raise CannotParseStemClass(stem_class)


