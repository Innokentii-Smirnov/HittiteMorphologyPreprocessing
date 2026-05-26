import os
from . import dm
from library.corrector import Corrector
from library.dm import DM

with dm, DM('Corrections'):
    print('Loading corrections from: ', os.getcwd())
    morpholex_corr = Corrector('Morpholexemic representations.txt')
    form_set_corr = Corrector('Grammatical form sets.txt')
    gramm_form_corr = Corrector('Grammatical forms.txt')
    wordform_corr = Corrector('Wordforms.txt')
    stem_class_corr = Corrector('Stem classes.txt')
