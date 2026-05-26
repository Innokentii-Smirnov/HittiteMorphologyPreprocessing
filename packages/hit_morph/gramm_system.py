from os import path
from gen_morph.gramm_systems.gramm_system import GrammaticalSystem
from . import dm

with dm:
    gs = GrammaticalSystem.from_file('Grammatical system.txt')
