from itertools import chain
from typing import Optional, Sequence
from bs4 import Tag
from warnings import warn
from gen_morph.exceptions import CannotParseWordform
from ..parsing.transliterations import parse_transliteration
from . import inflecting
from library.serializable import Serializable, StringList
from .clitic_complex import CliticComplex, CliticComplexDict
from .morpholex import Morpholex
from .encl_chain import EnclChain
from .selection import Selection, SelectionList
from gen_morph.exceptions import CannotParseSelection

missing = set()

def get_lang(trans: Tag) -> str:
    if (l := trans.sGr) is not None and l.text != '':
        return 'sux'
    elif (l := trans.aGr) is not None and l.text != '':
        return 'akk'
    else:
        return 'hit'
        
def get_options(wordform: Tag, prefix: str) -> CliticComplexDict:
    options = CliticComplexDict()
    for key, value in wordform.attrs.items():
        if key.startswith(prefix) and key != prefix + '0sel':
            lemma_idx = int(key.removeprefix(prefix))
            clitic_complex = CliticComplex.from_analysis(value)
            gramm_forms = inflecting.parse_form(clitic_complex.morpholex.gramm_form)
            if clitic_complex.encl_chain is not None:
                encl_chain_labels = inflecting.parse_form(clitic_complex.encl_chain.tags)
                for gramm_form_idx, gramm_form in gramm_forms.items():
                    morpholex = Morpholex.copy(clitic_complex.morpholex, gramm_form)
                    for encl_chain_label_idx, encl_chain_label in encl_chain_labels.items():
                        encl_chain = EnclChain.copy(clitic_complex.encl_chain, encl_chain_label)
                        selection = Selection(lemma_idx, gramm_form_idx, encl_chain_label_idx)
                        options[str(selection)] = CliticComplex(morpholex, encl_chain)
            else:
                for gramm_form_idx, gramm_form in gramm_forms.items():
                    morpholex = Morpholex.copy(clitic_complex.morpholex, gramm_form)
                    selection = Selection(lemma_idx, gramm_form_idx, None)
                    options[str(selection)] = CliticComplex(morpholex, None)
    return options

def get_selections(wordform: Tag, prefix: str) -> StringList:
    selections = StringList()
    key = prefix +'0sel'
    if key in wordform.attrs and (str_selections := wordform[key].strip()) != '':
        for selected in str_selections.split():
            try:
                selection = Selection.parse_string(selected)
                selections.append(selected)
            except CannotParseSelection:
                pass
    return selections

def add_index(index: int):
    return lambda x: (index, x)
add_one = add_index(1)
add_two = add_index(2)

from typing import TypeVar
from itertools import chain
TKey = TypeVar('TKey')
TValue = TypeVar('TValue')
class DoubleDictionary:
    def __init__(self, d1: dict[TKey, TValue], d2: dict[TKey, TValue]):
        self.d1 = d1
        self.d2 = d2
       
    def __getitem__(self, long_key: tuple[int, TKey]) -> TValue:
        index, key = long_key
        if index == 1:
            return self.d1[key]
        elif index == 2:
            return self.d2[key]
        else:
            raise ValueError(index)
    
    def __setitem__(self, long_key: tuple[int, TKey], value: TValue):
        index, key = long_key
        if index == 1:
            self.d1[key] = value
        elif index == 2:
            self.d2[key] = value
        else:
            raise ValueError(index)
    
    def __iter__(self):
        return chain(map(add_one, self.d1.keys()), map(add_two, self.d2.keys()))
    
    def items(self):
        return chain(
            map(lambda x: (add_one(x[0]), x[1]), self.d1.items()),
            map(lambda x: (add_two(x[0]), x[1]), self.d2.items()),
        )

class Segment(Serializable):
    sep = ';\n'

    def get_elements(self) -> tuple[str, str, str, Optional[str], Optional[str], CliticComplexDict, int, SelectionList,
    Optional[str], Optional[str], Selection]:
        return (self.exponent, self.translit, self.lang, self.predet, self.postdet,
        self.old_selections, self.old_options, self.idx,
        self.new_trans, self.new_selections, self.new_options,
        self.pred_lemma, self.pred_label, self.pred_selections,
        self.final_lemma, self.final_label, self.final_selections,
        self.pred_lemmata)
    
    def __tuple__(self):
        return (self.exponent, self.translit, self.lang, self.predet, self.postdet,
        self.old_selections, self.old_options,
        self.new_trans, self.new_selections, self.new_options,
        self.pred_lemma, self.pred_label, self.pred_selections,
        self.final_lemma, self.final_label, self.final_selections)
    
    @classmethod
    def from_strings(cls,
                     transcription: str,
                     transliteration: str,
                     lang: str,
                     predet: Optional[str],
                     postdet: Optional[str],
                     old_selections: str,
                     old_options: str,
                     idx: str,
                     new_trans: str,
                     new_selections: str,
                     new_options: str,
                     pred_lemma: Optional[str],
                     pred_label: Optional[str],
                     pred_selections: str,
                     final_lemma: Optional[str],
                     final_label: Optional[str],
                     final_selections: str,
                     pred_lemmata: Optional[str] = None):
        return cls(transcription, transliteration, lang, predet, postdet,
                   StringList.from_string(old_selections), CliticComplexDict.from_string(old_options),
                   int(idx), new_trans,
                   StringList.from_string(new_selections), CliticComplexDict.from_string(new_options),
                   pred_lemma, pred_label, StringList.from_string(pred_selections),
                   final_lemma, final_label, StringList.from_string(final_selections),
                   StringList() if pred_lemmata is None else StringList.from_string(pred_lemmata))

    def __init__(self,
                 transcription: str,
                 transliteration: str,
                 lang: str,
                 predet: Optional[str],
                 postdet: Optional[str],
                 old_selections: StringList,
                 old_options: CliticComplexDict,
                 idx: int,
                 new_trans: str,
                 new_selections: StringList,
                 new_options: CliticComplexDict,
                 pred_lemma: Optional[str],
                 pred_label: Optional[str],
                 pred_selections: StringList,
                 final_lemma: Optional[str],
                 final_label: Optional[str],
                 final_selections: StringList,
                 pred_lemmata: Optional[StringList] = None):
        self.exponent = transcription
        self.translit = transliteration
        self.lang = lang
        self.predet = predet
        self.postdet = postdet
        self.old_selections = old_selections
        self.old_options = old_options
        self.idx  = idx
        self.new_trans = new_trans
        self.new_options = new_options
        self.new_selections = new_selections
        self.pred_lemma = pred_lemma
        self.pred_label = pred_label
        self.pred_selections = pred_selections
        self.final_lemma = final_lemma
        self.final_label = final_label
        self.final_selections = final_selections
        self.pred_lemmata = pred_lemmata or StringList()
        self.mark_morphs()
        self.options = DoubleDictionary(old_options, new_options)

    @property
    def analyses(self) -> list[CliticComplex]:
        return list(chain(self.old_options.values(), self.new_options.values()))

    def mark_morphs(self):
        for analysis in self.analyses:
            analysis.segment = self
            analysis.morpholex.segment = self
            if analysis.encl_chain is not None:
                analysis.encl_chain.segment = self
            analysis.assign_attributes()

    @classmethod
    def from_tag(cls, wordform: Tag):

        # Exponent
        transcription = wordform.attrs.get('trans', '_')
        transliteration = parse_transliteration(wordform.children)
        lang = get_lang(wordform)
        idx = int(wordform.attrs['idx'])
        new_trans = wordform.attrs.get('trans', '_')

        # Morphological representations
        old_options = get_options(wordform, 'opt')
        new_options = get_options(wordform, 'mrp')

        #Selections
        old_selections = get_selections(wordform, 'opt')
        new_selections = get_selections(wordform, 'mrp')

                
        return cls(transcription, transliteration, lang, None, None,
        old_selections, old_options,
        idx, new_trans, new_selections, new_options,
        None, None, StringList(),
        None, None, StringList(),
        StringList())
    
    def actual_selections(self, verbose=True):
        for selected in self.old_selections:
            if selected in self.old_options:
                yield selected
            else:
                selection = Selection.parse_string(selected)
                if selection.gramm_form == 'all':
                    for key, analysis in self.old_options.items():
                        curr_selection = Selection.parse_string(key)
                        if (curr_selection.lexeme == selection.lexeme and 
                            curr_selection.encl_chain == selection.encl_chain):
                            yield key
                elif selection.gramm_form == 'sg':
                    for key, analysis in self.old_options.items():
                        curr_selection = Selection.parse_string(key)
                        if (curr_selection.lexeme == selection.lexeme and 
                            curr_selection.encl_chain == selection.encl_chain and
                            analysis.morpholex.gramm_form and
                            'SG' in analysis.morpholex.gramm_form):
                            yield key
                elif selection.gramm_form == 'pl':
                    for key, analysis in self.old_options.items():
                        curr_selection = Selection.parse_string(key)
                        if (curr_selection.lexeme == selection.lexeme and 
                            curr_selection.encl_chain == selection.encl_chain and
                            analysis.morpholex.gramm_form and
                            'PL' in analysis.morpholex.gramm_form):
                            yield key
                else:
                    if verbose:
                        warn('Missing selection: {0} for {1}\n'.format(self.old_selections, self.old_options))
                    #raise ValueError(self)
    
    @property
    def first(self) -> CliticComplex:
        try:
            try:
                selected = next(self.actual_selections(False))
            except StopIteration:
                selected = next(iter(self.old_options))
                warn("Taking randomly '{0}' instead of '{1}' for {2} in {3}\n{4}\n".format(
                    selected, self.old_selections, self.exponent, self.sentence.metadata, self.old_options
                ))
                global missing
                missing.add((self, self.sentence.metadata))
            return self.old_options[selected]
        except StopIteration:
            raise ValueError('No options for {0} in {1}'.format(self.exponent, self.sentence.metadata))
    
    @property
    def correct(self) -> list[CliticComplex]:
        return [self.old_options[selection] for selection in self.actual_selections()]
    
    @property
    def label(self) -> str:
        return self.first.label
    
    @property
    def lemma(self) -> str:
        return self.first.morpholex.lemma
    
    @property
    def labels(self) -> set[str]:
        return set(analysis.label for analysis in self.correct)
    
    @property
    def lemmata(self) -> set[str]:
        return set(analysis.morpholex.lemma for analysis in self.correct)
    
    @property
    def text(self) -> str:
        text = self.exponent
        if self.predet is not None:
            text = self.predet + ' ' + text
        if self.postdet is not None:
            text +=  ' ' + self.postdet
        return text
    
    @property
    def next(self):
        idx = self.position + 1
        if idx < len(self.sentence):
            return self.sentence[idx]
        else:
            return None
    
    @property
    def prev(self):
        idx = self.position - 1
        if idx > 0:
            return self.sentence[idx]
        else:
            return None

    @property
    def possible_lemmata(self) -> set[str]:
        return set(analysis.morpholex.lemma for analysis in self.new_options.values())
