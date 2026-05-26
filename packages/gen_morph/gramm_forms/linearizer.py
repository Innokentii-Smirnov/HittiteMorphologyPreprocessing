import re
from functools import partial
from library.iterable import modify_values
from library.read import read_multidict
from itertools import chain
from languages.brackets import generate_language

def condition(gramm_form, order):
    i = 0
    while i < len(order):
        if order[i] == '<':
            start = i
            while order[i] != '>':
                i += 1
                if i == len(order):
                    raise ValueError(order)
            cat = order[start+1:i]
            if cat not in gramm_form:
                return False
        i += 1
    second = all('<{0}>'.format(key) in order for key, value in gramm_form.items() 
    if value is not None and not value.startswith('_'))
    return second
            

class Linearizer:
    
    def __init__(self, orders: dict[str, list[str]]):
        self.orders = orders

    def __call__(self, pos: str, gramm_form: dict[str, str]):
        orders = self.orders[pos]
        matching_orders = list(filter(partial(condition, gramm_form), orders))
        assert len(matching_orders) == 1, gramm_form
        line = matching_orders[0]
        for category, value in gramm_form.items():
            if value is not None:
                line = line.replace('<{0}>'.format(category), value)
            else:
                line = line.replace('<{0}>'.format(category), '')
        line = line.strip('.')
        line = line.strip(':')
        line = re.sub('\.+', '.', line)
        line = re.sub('\:+', ':', line)
        return line

    @classmethod
    def from_file(cls, filename: str):
        general_orders = read_multidict(filename)
        cats_to_orders = {
            cat: set(chain.from_iterable(map(generate_language, orders)))
            for cat, orders in general_orders.items()
        }
        return cls(cats_to_orders)
    