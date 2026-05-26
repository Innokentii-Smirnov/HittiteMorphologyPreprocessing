import re
from library.iterable import modify_values
from library.read import read_multidict

class Linearizer:
    
    def __init__(self, orders: dict[str, list[list[str]]]):
        self.orders = orders

    def __call__(self, pos: str, gramm_form: dict[str, str]):
        orders = self.orders[pos]
        matching_orders = list(filter(lambda order: all(key in order for key, value in gramm_form.items()
        if value is not None and not value.startswith('_')), orders))
        assert len(matching_orders) == 1, gramm_form
        order = matching_orders[0]
        features = list[str]()
        for category in order:
            if category in gramm_form:
                feature = gramm_form[category]
                if feature is not None and not feature.startswith('_'):
                    features.append(feature)
        linearized = '.'.join(features)
        linearized = re.sub(r'(?<=\d)\.(?=[A-z])', '', linearized)
        return linearized

    @classmethod
    def from_file(cls, filename: str):
        orders = read_multidict(filename)
        orders = modify_values(lambda seq: list(map(lambda x: x.split(' '), seq)), orders)
        return cls(orders)

    @classmethod
    def from_dec_file(cls, filename: str):
        global orders
        orders = read_multidict(filename)
        orders = modify_values(lambda seq: list(map(lambda x: [matched for matched in re.findall('<([^<>]+)>', x)], seq)), orders)
        return cls(orders)


