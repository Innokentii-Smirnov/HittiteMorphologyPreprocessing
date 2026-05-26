import re
from collections.abc import Iterable

def parse_lemma(lemma):
    if m := re.match(r'(\D+)(\d+)', lemma):
        stem, index = m.groups()
    else:
        stem, index = lemma, '1'
    return stem, index
