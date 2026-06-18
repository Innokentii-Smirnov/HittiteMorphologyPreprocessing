from .segment import Segment
from .clitic_complex import CliticComplex
from .morpholex import Morpholex
from .encl_chain import EnclChain
from .sentence import Sentence
from itertools import groupby
from collections import Counter
from library.serializable import SerializableList
from itertools import chain
from numpy import inf
from tqdm.auto import tqdm
from more_itertools import one
from udapi.core.document import Document as UDDocument
from udapi.core.node import Node
from library.iterable import group_by

class Document(SerializableList):
    sep = '\n\n***\n'
    get_element = Sentence.from_string

    @property
    def segments(self) -> list[Segment]:
        return list(chain.from_iterable(sentence.segments for sentence in self))
    
    @property
    def clitic_complexes(self) -> list[CliticComplex]:
        return list(chain.from_iterable(segment.analyses for segment in self.segments))
    
    @property
    def wordforms(self) -> list[Morpholex]:
        return list(analysis.morpholex for analysis in self.clitic_complexes)
    
    @property
    def encl_chains(self) -> list[EnclChain]:
        return list(analysis.encl_chain for analysis in self.clitic_complexes 
        if analysis.encl_chain is not None)
    
    def select_lemma_by_log_probs(self, log_probs: dict, vocabs: dict[str, dict[str, int]]):
        attrs = sorted(log_probs)
        for i, sentence in tqdm(list(enumerate(self))):
            for j, segment in enumerate(sentence):
                grouped = group_by(
                    lambda analysis: tuple(analysis.attrs[attr] for attr in attrs),
                    segment.new_options.values()
                )
                options = [value[0] for value in grouped.values()]
                if len(segment.new_options) > 0:
                    clitic_group = max(
                        options,
                        key = lambda clitic_group: clitic_group.score(
                            {attr: log_probs[attr][i][j] for attr in log_probs},
                            vocabs
                        )
                    )
                    segment.final_lemma = clitic_group.morpholex.lemma
                    segment.final_label = clitic_group.label
                else:
                    segment.final_lemma = None
                    segment.final_label = None
    
    def eval_lemmata(self, all_segments: bool = False) -> Counter[tuple[str, str | None, str | None]]:
        corr_lemma = 0
        total = 0
        errors = Counter[tuple[str, str | None, str | None]]()
        for segment in self.segments:
            if not segment.text.isdigit() and segment.lemma is not None or all_segments:
                if segment.final_lemma == segment.lemma:
                    corr_lemma += 1
                else:
                    errors[segment.text, segment.final_lemma, segment.lemma] += 1
                total += 1
        print('Lemma accuracy: {} ({}/{})'.format(
            round(100*corr_lemma/total, 2),
            corr_lemma,
            total
        ))
        return errors
    
    def eval_labels(self, all_segments: bool = False) -> Counter[tuple[str, str | None, str]]:
        corr_label = 0
        total = 0
        errors = Counter[tuple[str, str | None, str]]()
        for segment in self.segments:
            if not segment.text.isdigit() or all_segments:
                if segment.final_label == segment.label:
                    corr_label += 1
                else:
                    errors[segment.text, segment.final_label, segment.label] += 1
                total += 1
        print('Morph accuracy: {} ({}/{})'.format(
            round(100*corr_label/total, 2),
            corr_label,
            total
        ))
        return errors

    def to_ud_document(self) -> UDDocument:
      document = UDDocument()
      for sentence in self:
        root = document.create_bundle().create_tree()
        for key, group in groupby(sentence.segments, lambda segment: segment.idx):
          segments = list(group)
          if len(segments) > 1:
            words = list[Node]()
            for segment in segments:
              node = root.create_child(form=segment.exponent or '_', misc=segment.misc)
              words.append(node)
            mwt_form = ' '.join(node.form for node in words)
            mwt = root.create_multiword_token(words, mwt_form)
          else:
            segment = one(segments)
            node = root.create_child(form=segment.exponent or '_', misc=segment.misc)
      return document
