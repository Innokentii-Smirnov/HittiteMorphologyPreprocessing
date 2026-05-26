from .gramm_system import gs
from .gramm_forms import lin
from functools import partial

par_schemata = dict[str, dict[str, str]]()
for pos in gs:
    par_schemata[pos] = list(map(partial(lin, pos), gs.get_gramm_forms(pos)))
