from library.tables.table_scheme import TableScheme
from .gramm_system import gs

schemata = dict[str, TableScheme]()
schemata['verb'] = gs['verb'].get_table_scheme('verbform mood tense num pers'.split(), 'voice asp'.split())
