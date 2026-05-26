import re
from re import split
from .par_scheme import ParadigmScheme

class GrammaticalSystem:
    
    def __init__(self, properties: dict[str, list[str]],
                 categories: dict[str, list[str]],
                 pos_implic: dict[str, list[str]],
                 neg_implic: dict[str, list[str]],
                 implied: dict[str, set[str]]):
        self.properties = properties
        self.pos_implic = pos_implic
        self.neg_implic = neg_implic
        self.schemata = dict[str, ParadigmScheme]()
        for pos, value in categories.items():
            scheme = ParadigmScheme(properties, value, pos_implic, neg_implic, implied[pos])
            self.schemata[pos] = scheme

    def get_gramm_forms(self, pos: str):
        return self.schemata[pos].get_gramm_forms()

    def __iter__(self):
        return iter(self.schemata.keys())

    def __getitem__(self, key: str) -> ParadigmScheme:
        return self.schemata[key]

    @classmethod
    def from_file(cls, filename: str):
        properties = dict()
        categories = dict()
        pos_implic = dict()
        neg_implic = dict()
        implied = dict()
        with open(filename, 'r', encoding='utf-8') as fin:
            for line in fin:
                line = line.removesuffix('\n').removesuffix('\r')
                if '=' in line:
                    try:
                        category, allvalues = line.split(' = ')
                    except ValueError:
                        raise ValueError(line)
                    values = allvalues.split()
                    properties[category] = values
                elif ':' in line:
                    pos, allvalues = re.split(': ', line)
                    implied[pos] = set()
                    cats = allvalues.split()
                    for i in range(len(cats)):
                        if cats[i].startswith('~'):
                            cats[i] = cats[i].removeprefix('~')
                            implied[pos].add(cats[i])
                        if cats[i] not in properties:
                            raise ValueError("The grammatical category '{0}' in line '{1}' is not defined.".format(cat, line))
                    categories[pos] = cats
                elif '-/->' in line:
                    keys, values = re.split(' -/-> ', line)
                    for key in split(r' \| ', keys):
                        for value in split(r' \| ', values):
                            if key not in neg_implic:
                                neg_implic[key] = list()
                            neg_implic[key].append(value)
                elif '->' in line:
                    keys, values = re.split(' -> ', line)
                    for key in split(r' \| ', keys):
                        for value in split(r' \| ', values):
                            if key not in pos_implic:
                                pos_implic[key] = list()
                            pos_implic[key].append(value)
                else:
                    raise ValueError(line)
        return cls(properties, categories, pos_implic, neg_implic, implied)

