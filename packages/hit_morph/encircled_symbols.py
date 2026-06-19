import re
from library.read import read_text
from . import dm

with dm:
    circ_symb = read_text('Signs.txt')


def remove_encircled_symbols(string: str) -> str:
    return re.sub(f'^({circ_symb}) ', '', string)
