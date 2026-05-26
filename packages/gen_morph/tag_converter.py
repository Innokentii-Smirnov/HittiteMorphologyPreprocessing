from typing import Callable
import os
from os import path
import re
from re import Pattern
from library import get_file_name
from .exceptions import CannotParseGrammForm

class TagConverter:
    
    def __init__(self, file_name: str, func: Callable[[str, str], str]):
        cats = dict[str, dict[str, str]]()
        patterns = list[str]()
        with open(get_file_name(file_name), 'r', encoding='utf-8') as fin:
            cat = fin.readline().rstrip()
            while cat != '':
                if cat == 'Patterns':
                    while (line := fin.readline().rstrip()).startswith('\t'):
                        patterns.append(line.removeprefix('\t').replace('.', r'\.'))
                    else:
                        cat = line
                else:
                    cats[cat] = dict[str, str]()
                    while (line := fin.readline().rstrip()).startswith('\t'):
                        match line.removeprefix('\t').split():
                            case old, new:
                                cats[cat][old] = new.rstrip() if new != '_' else None
                            case old,:
                                cats[cat][old] = func(cat, old)
                    else:
                        cat = line

        self.cats = cats
        self.layered = set()
        for cat in self.cats:
            if len(self.cats[cat]) == 0:
                self.cats[cat] = self.cats[remove_clarif(cat)]
                self.layered.add(cat)
        
        self.patterns = list[Pattern]()
        for pattern in patterns:
            for cat in self.cats:
                grammemes = '|'.join(map(re.escape, cats[cat].keys()))
                pattern = re.sub(fr'{cat}:(?P<Grammemes>({grammemes})(\|({grammemes}))*)', fr'(?P<{cat}>\g<Grammemes>)', pattern)
                pattern = re.sub(fr'(?<!\<){cat}(?!_)', f'(?P<{cat}>{grammemes})', pattern)
            try:
                self.patterns.append(re.compile(pattern))
            except:
                print(pattern)
                raise

    def decompone(self, tag: str) -> dict[str, str]:
        for pattern in self.patterns:
            if m := pattern.fullmatch(tag):
                gf = m.groupdict()
                return gf
        raise CannotParseGrammForm(tag)
    
    def convert(self, old_gf:  dict[str, str]) ->  dict[str, str]:
        gf = {mod_cat(cat) if cat in self.layered else remove_clarif(cat):
              self.cats[cat][old] for cat, old in old_gf.items() if old is not None}
        return gf
    
    def __call__(self, tag: str) -> dict[str, str]:
        old_gf = self.decompone(tag)
        new_gf = self.convert(old_gf)
        return new_gf

def remove_clarif(cat: str) -> str:
    i = cat.find('_')
    if i == -1:
        i = cat.find('[')
        if i == -1:
            return cat
    return cat[:i]

def mod_cat(cat: str) -> str:
    if '_' in cat:
        return cat.replace('_', '[') + ']'
    return cat
