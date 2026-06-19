from __future__ import annotations
from typing import TYPE_CHECKING
from library.serializable import Serializable
from gen_morph.exceptions import CannotParseEnclChain
from collections.abc import Iterator
if TYPE_CHECKING:
  from .clitic_complex import CliticComplex
  from .segment import Segment
String = str | None

class EnclChain(Serializable):
    sep = '@'
    clitic_complex: 'CliticComplex'
    segment: 'Segment'

    def get_elements(self) -> tuple[String, String]:
        return self.exponents, self.tags

    @classmethod
    def from_strings(cls, exponents: str, tags: str) -> EnclChain:
        return cls(exponents, tags, None)

    def __init__(self, exponents: str | None, tags: str | None, other_tags: str | None):
        self.exponents = exponents if exponents != '' else None
        self.tags = tags
        self.other_tags = other_tags if other_tags != '' else None
        return
    
    @classmethod
    def copy(cls, other: EnclChain, tags: str | None) -> EnclChain:
        return cls(other.exponents, tags, other.other_tags)

    def check(self) -> None:
        if self.tags is None or self.exponents is None:
            raise CannotParseEnclChain(str(self))
        if len(self.tags.split('=')) != len(self.exponents.split('=')):
            raise CannotParseEnclChain(str(self))

    def __lt__(self, other: object) -> bool:
        if isinstance(other, EnclChain):
            return self.__tuple__().__lt__(other.__tuple__())
        return False
    
    def __iter__(self) -> Iterator[tuple[str, str]]:
        if self.exponents is None:
            raise ValueError('Cannot iterate over enclitics in a chain \
              with tags {0} because the exponents are None'.format(self.tags))
        if self.tags is None:
            raise ValueError('Cannot iterate over enclitics in a chain \
              with exponents {0} because the tags are None'.format(self.exponents))
        return zip(self.tags.split('='), self.exponents.split('='), strict=True)
    
