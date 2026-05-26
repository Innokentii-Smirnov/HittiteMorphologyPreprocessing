from gen_morph.gramm_forms.decomponer import Decomponer
from gen_morph.gramm_forms.linearizer1 import Linearizer
from .gramm_system import gs
from . import dm

with dm:
    dec = Decomponer.from_file('Decomponer.txt', gs.properties)
    lin = Linearizer.from_dec_file('Decomponer.txt')
