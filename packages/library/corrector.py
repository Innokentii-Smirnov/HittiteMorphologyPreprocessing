from typing import TypeVar
from .read import read_dict
from .write import write_list
from .iterable import modify_keys, modify_values

T = TypeVar('T', str, str | None)

class Corrector:
    
    def __init__(self, file_name: str):
        self.corrections = read_dict(file_name)
    
    def process_single(self, item: T) -> T:
        if item in self.corrections:
            return self.corrections[item]
        else:
            return item

    def process_multiple(self, items: list[T]) -> list[T]:
        return list(map(self.process_single, items))

    def __call__(self, item: T) -> T:
        return self.process_single(item)

def update_corr(to_update: str, erroneous: list[str], remove=True, other=False):
    source = 'Corrections for ' + to_update
    target = source
    if other:
        target += ' 2'
    corr = read_dict(source)
    for item in erroneous:
        if item not in corr:
            print('Adding ', item)
            corr[item] = item
    if remove:
        remove_condition = lambda item: corr[item] == item and item not in erroneous
        to_remove = set(filter(remove_condition, corr))
        for item in to_remove:
            print('Removing ', item)
            del corr[item]
    li = ['{0}\t{1}'.format(key, value) for key, value in sorted(corr.items())]
    write_list(li, target)
