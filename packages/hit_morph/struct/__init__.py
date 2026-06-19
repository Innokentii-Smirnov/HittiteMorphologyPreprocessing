import re

def parse_lemma(lemma: str) -> tuple[str, str]:
    if m := re.match(r'(\D+)(\d+)', lemma):
        stem, index = m.groups()
    else:
        stem, index = lemma, '1'
    return stem, index
