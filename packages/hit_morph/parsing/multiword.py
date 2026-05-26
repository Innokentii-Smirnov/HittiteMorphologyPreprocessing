import regex as re
from typing import Union
from itertools import zip_longest
from udapi.core.root import Root
from udapi.core.node import Node
from udapi.core.mwt import MWT
from udapi.core.dualdict import DualDict
from hit_morph.struct.morpholex import Morpholex
from hit_morph.struct.encl_chain import EnclChain
from gen_morph.exceptions import CannotParseGrammForm

def get_mwt(root: Root, exponent: str, morpholex: Morpholex, encl_chain: EnclChain) -> MWT:
    
    complex_gramm_form = morpholex.gramm_form
    nodes = list[Node]()
    mwt_misc = DualDict()

    if '+' in complex_gramm_form:
        
        for form, lemma, gloss_gramm_form in zip_longest(exponent.split('˽'),
                                             morpholex.lemma.split('˽'),
                                             complex_gramm_form.split('+')):
            gloss, gramm_form = gloss_gramm_form.split(':')
            node = root.create_child()
            node.form = form
            node.lemma = lemma
            node.xpos = gramm_form
            node.gloss = gloss
            nodes.append(node)
        
        nodes[0].parent = nodes[1]
        nodes[0].deprel = "nmod"

        mwt_misc['Gloss'] = morpholex.gloss
        mwt_misc['Class'] = morpholex.stem_class
        mwt_misc['Det'] = morpholex.det

    elif '_' in complex_gramm_form:
        gramm_forms = complex_gramm_form.split('_')
        with_preposition = any(
            gramm_forms[1].endswith(tag) for tag in {'ADV', 'PREP', 'POSP'}
        )
        with_posessive = any(
            gramm_forms[1].lstrip().startswith(tag) for tag in ['DEM', 'PPRO']
        )
        with_other_following_dependent = gramm_forms[1] in {'QUOT'}

        if with_preposition:
            gramm_forms.reverse()
            exponents = exponent.split(' ')
        else:
            exponents = list[str]()

        for form, gloss_gramm_form in zip_longest(exponents,
                                                  gramm_forms):
            spl = gloss_gramm_form.split(':')
            if len(spl) == 2:
                gloss, gramm_form = spl
            else:
                gramm_form = spl[0]
                gloss = None
            node = root.create_child()
            node.form = form
            node.xpos = gramm_form
            node.gloss = gloss
            nodes.append(node)

        if with_preposition:
            nodes[0].parent = nodes[1]
            nodes[0].deprel = 'case'
            if nodes[0].xpos == 'POSP':
                nodes[0].xpos = 'PREP'
            main = nodes[1] if nodes[1].form is not None else nodes[0]

        elif with_posessive:
            nodes[1].parent = nodes[0]
            nodes[1].deprel = 'nmod'
            main = nodes[0]

        elif with_other_following_dependent:
            nodes[1].parent = nodes[0]
            main = nodes[0]

        else:
            raise CannotParseGrammForm(gramm_forms[1])

        main.lemma = morpholex.lemma
        main.gloss = morpholex.gloss
        main.misc['Class'] = morpholex.stem_class
        main.misc['Det'] = morpholex.det

    elif '=' in complex_gramm_form:

        lemmas = re.split(r'=(?!$|\w*\-)', morpholex.lemma)
        gramm_forms = complex_gramm_form.split('=')
        if len(lemmas) == 1:
            main_lemma = lemmas[0]
            forms = [None] * len(gramm_forms)
        else:
            main_lemma = None
            forms = lemmas
        
        for form, gloss_gramm_form in zip(forms,
                                           gramm_forms,
                                           strict=True):
            spl = gloss_gramm_form.split(':')
            if len(spl) == 2:
                gloss, gramm_form = spl
            else:
                gramm_form = spl[0]
                gloss = None
            node = root.create_child()
            node.form = form
            node.xpos = gramm_form
            node.gloss = gloss
            nodes.append(node)
        
        main = nodes[0]
        main.lemma = main_lemma
        if morpholex.gloss != '':
            if main.gloss == '':
                main.gloss = morpholex.gloss
            else:
                assert main.gloss == morpholex.gloss, "'{0}' != '{1}'".format(morpholex.gloss, main.gloss)
        main.misc['Class'] = morpholex.stem_class
        main.misc['Det'] = morpholex.det
    
    if encl_chain is not None:
        for encl, gramm_form in zip(encl_chain.exponents.split('='),
                                    encl_chain.gramm_form.split('='),
                                    strict=True):
            node = root.create_child()
            node.form = encl
            node.xpos = gramm_form
            nodes.append(node)
    
    mwt = root.create_multiword_token(nodes, exponent, mwt_misc)
    return mwt
