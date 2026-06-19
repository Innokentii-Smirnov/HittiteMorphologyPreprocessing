from __future__ import annotations
from typing import Sequence, TYPE_CHECKING
from numpy import ndarray
from library.serializable import Serializable, SerializableDict
from .morpholex import Morpholex
from .encl_chain import EnclChain
from ..parsing.analysis import parse_analysis
from .selection import Selection
if TYPE_CHECKING:
  from .segment import Segment

class CliticComplex(Serializable):
    sep = '\t'
    segment: 'Segment'

    def get_elements(self) -> tuple[Morpholex, EnclChain | None]:
        return self.morpholex, self.encl_chain

    @classmethod
    def from_strings(cls, morpholex: str, encl_chain: str) -> CliticComplex:
        return cls(
            Morpholex.from_string(morpholex),
            EnclChain.from_string(encl_chain) if encl_chain is not None else None
        )
    
    def __init__(self, morpholex: Morpholex, encl_chain: EnclChain | None):
        self.morpholex = morpholex
        self.encl_chain = encl_chain
        self.morpholex.clitic_complex = self
        if self.encl_chain is not None:
            self.encl_chain.clitic_complex = self
        self.assign_attributes()
    
    def assign_attributes(self) -> None:
        self.attrs = {
            'lemma': self.morpholex.lemma,
            'upos': self.morpholex.upos,
            'gloss': self.morpholex.gloss,
            'encl_chain': self.encl_chain.tags if self.encl_chain is not None else None,
            'gramm_form': self.morpholex.gramm_form,
            'det': self.morpholex.det,
            'simple_label': self.morpholex.simple_label
        }
    
    def score(self, log_probs_dict: dict[str, ndarray], vocabs: dict[str, dict[str, int]]) -> float:
        score = 0.0
        for attr in log_probs_dict:
            value = self.attrs[attr]
            vocab = vocabs[attr]
            log_probs = log_probs_dict[attr]
            if value in vocab:
                code = vocab[value]
                score += log_probs[code]
            else:
                score += log_probs.mean()
        return score

    @classmethod
    def from_analysis(cls, analysis: str) -> CliticComplex:
        morpholex, encl_chain = parse_analysis(analysis)
        return cls(morpholex, encl_chain)

    # def select_gramm_form(self, selection: str | None):
    #     self.morpholex.select_gramm_form(selection)
    #
    # def select_encl_chain(self, selection: str | None):
    #     if self.encl_chain is None:
    #         assert selection is None, 'This wordform has no enclitic chain.'
    #     else:
    #         self.encl_chain.select_tags(selection)
    
    @property
    def label(self) -> str:
        label = self.morpholex.label
        if self.encl_chain is not None and self.encl_chain.tags is not None:
            label = '='.join([label, self.encl_chain.tags])
        return label
    
    @property
    def elements(self) -> tuple[Morpholex, EnclChain | None]:
        return self.morpholex, self.encl_chain

    @property
    def complete_encl_chain(self) -> str | None:
        tags = []
        if self.morpholex.attached_enclitics_tag is not None:
            tags.append(self.morpholex.attached_enclitics_tag)
        if self.morpholex.relators is not None:
            tags.append(self.morpholex.relators.replace('.RLT', '=RLT'))
        if self.encl_chain is not None and self.encl_chain.tags is not None:
            tags.append(self.encl_chain.tags)
        if len(tags) > 0:
            return '='.join(tags)
        else:
            return None

class CliticComplexDict(SerializableDict[str, CliticComplex]):
    sep = '\n'
    get_key = lambda string: string
    get_value = CliticComplex.from_string



    
