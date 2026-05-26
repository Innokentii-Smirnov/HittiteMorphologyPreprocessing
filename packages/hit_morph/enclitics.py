import os
import library
from library.corrector import Corrector
from collections import OrderedDict
from library.read import read_dict_of_list
from . import dm


func = lambda x: tuple(x.split('='))

with dm:
    struct = read_dict_of_list('Enclitic chain structure.txt')
    encl_chain_corr = Corrector('Corrections/Enclitic chains.txt')
    encl_corr = Corrector('Corrections/Enclitics forms.txt')

def encl_chain_to_dict(encl_chain: str) -> OrderedDict[str, str]:
    encls = encl_corr.process_multiple(encl_chain_corr(encl_chain).split('='))
    positions = iter(struct)
    position = next(positions)
    token = OrderedDict[str, str]()
    for encl in encls:
        while encl not in struct[position]:
            position = next(positions)
        if position in token:
            raise ValueError(encls)
        token[position] = encl
    return token
