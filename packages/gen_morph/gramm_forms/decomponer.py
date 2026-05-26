import re
from library.read import read_list
from gen_morph.exceptions import CannotParseGrammForm

class Decomponer:
    
    def __init__(self, order_sets: dict[str, list[tuple[str, str | None]]], properties: dict[str, list[str]]):
        self.patterns = dict[str, list[tuple[re.Pattern, str | None]]]()
        for pos, orders in order_sets.items():
            for order, struct in orders:
                order = order.replace('.', r'\.')
                for _category, _features in properties.items():
                    for matched in re.finditer(r'<({0})(?:\:([\w/|\\?]+))?(?:\[(\w+)\])?>'.format(_category), order):
                        text = matched.group(0)
                        category, allowed_values, scope = matched.groups()
                        if scope is not None:
                            newcategory = '{0}_{1}'.format(category, scope)
                        else:
                            newcategory = category
                        features = '|'.join(_features) if allowed_values is None else allowed_values
                        order = order.replace(text, '(?P<{0}>{1})'.format(newcategory, features))
                if pos not in self.patterns:
                    self.patterns[pos] = list[tuple[re.Pattern, str | None]]()
                self.patterns[pos].append((re.compile(order), struct))

    def __call__(self, pos: str, tag: str) -> tuple[dict[str, str], str | None]:
        matched = None
        corr_struct = None
        for pattern, struct in self.patterns[pos]:
            new_matched = pattern.fullmatch(tag)
            if new_matched is not None:
                if matched is not None:
                    raise CannotParseGrammForm('Ambiguity for ' + tag)
                matched = new_matched
                corr_struct = struct
        if matched is None:
            raise CannotParseGrammForm('Incorrect tag: ' + tag)
        groups = matched.groupdict()
        decomponed = dict[str, str]()
        for key, value in groups.items():
            if value is not None:
                match key.split('_'):
                    case category, scope:
                        newkey = '{0}[{1}]'.format(category, scope)
                    case category,:
                        newkey = category
                    case _:
                        raise ValueError(key)
                decomponed[newkey] = value
        return decomponed, corr_struct

    @classmethod
    def from_file(cls, filename: str, properties: dict[str, list[str]]):
        order_sets = dict[str, list[tuple[str, str | None]]]()
        for line in read_list(filename):
            match line.split('\t'):
                case pos, order, struct:
                    pass
                case pos, order:
                    struct = None
                case _:
                    raise ValueError(line)
            if pos not in order_sets:
                order_sets[pos] = list[tuple[str, str | None]]()
            order_sets[pos].append((order, struct))
        return cls(order_sets, properties)
