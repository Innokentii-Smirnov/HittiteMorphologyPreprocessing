import re
from gen_morph.exceptions import CannotParseMorpholex
from library.brackets import find_with_brack_balance
from hit_morph import corrections as corrs
from ..struct.morpholex import Morpholex
from ..struct.encl_chain import EnclChain
from ..encircled_symbols import circ_symb
import hit_morph

preprocess = lambda y: y.strip()

def parse_analysis(analysis: str) -> tuple[Morpholex, EnclChain|None]:
    analysis = re.sub(f'^({circ_symb}) ', '', analysis)
    analysis = corrs.morpholex_corr(analysis)

    pattern = tuple(map(lambda x: tuple(map(preprocess, x.split('@'))), re.split(r'\+=', analysis)))
    match pattern:
        case morph, encl:
            match pattern:
                case (lemma, gloss, gramm_forms, stem_class, det), (exponents, tags, _):
                    # 5,3
                    other_tags = ''
                case (lemma, gloss, gramm_forms, stem_class), (exponents, tags, other_tags, det):
                    # 4,4
                    pass
                case (lemma, gloss, gramm_forms, stem_class), (exponents, tags, det):
                    # 4,3
                    other_tags = ''
                case (lemma, gloss, gramm_forms, stem_class, ''), (exponents, tags, '', det):
                    # 5,4
                    other_tags = ''
                case (lemma, gloss, gramm_forms, stem_class, det), (exponents, tags):
                    # 5,2
                    other_tags = ''
                case (lemma, gloss, gramm_forms), (exponents, tags, '', det):
                    # 3,4
                    other_tags = ''
                    stem_class = ''
                case _:
                    raise CannotParseMorpholex(analysis)

            morpholex = Morpholex(lemma, gloss, gramm_forms, stem_class, det, None)
            encl_chain = EnclChain(exponents, tags, other_tags)
            return morpholex, encl_chain

        case morph,:
            match morph:
                case lemma, gloss, gramm_forms, stem_class, det:
                    # 5
                    pass
                case lemma, gloss, gramm_forms, stem_class, '', det:
                    # 6
                    pass
                case lemma, gloss_gramm_forms, '' if len(
                    find_with_brack_balance(gloss_gramm_forms, ':', '{', '}')) > 0:
                    # 3
                    try:
                        gloss, gramm_forms = gloss_gramm_forms.split(' || ')[0].split(':')
                    except ValueError:
                        raise CannotParseMorpholex(analysis)
                    stem_class = None
                    det = None
                case lemma, gramm_forms, '' if len(
                    find_with_brack_balance(gramm_forms, ':', '{', '}')) == 0:
                    # 3
                    gloss = ''
                    stem_class = ''
                    det = ''
                case lemma, gloss, gramm_forms if (gramm_forms != ''):
                    # 3
                    stem_class = ''
                    det = ''
                case lemma, gloss_gramm_forms if (':' in gloss_gramm_forms):
                    # 2
                    gloss, gramm_forms = gloss_gramm_forms.split(':')
                    stem_class = ''
                    det = ''
                case  lemma, gloss, gramm_forms, stem_class:
                    det = ''
                case  lemma, gloss:
                    gramm_forms = ''
                    stem_class = ''
                    det = ''
                case _:
                    raise CannotParseMorpholex(analysis)

            return Morpholex(lemma, gloss, gramm_forms, stem_class, det, None), None

        case _:
            raise CannotParseMorpholex(analysis)

