from bs4 import Tag
from bs4.element import PageElement, NavigableString
from collections.abc import Iterable
import re

def parse_element(element: PageElement) -> str:
    if isinstance(element, Tag):
        if element.name == 'd':
            return str(element)
        else:
            return element.text
    elif isinstance(element, NavigableString):
        return str(element)
    else:
        raise ValueError

repl = re.compile(r'<[^<>]+/>')

def parse_transliteration(transliteration: Iterable[PageElement]) -> str:
    trans = ''.join(parse_element(element) for element in transliteration)
    trans = repl.sub('', trans)
    return trans
