from library.serializable import Serializable
from gen_morph.exceptions import CannotParseEnclChain
from collections.abc import Iterator
String = str | None

class EnclChain(Serializable):
    sep = '@'

    def get_elements(self) -> tuple[String, String]:
        return self.exponents, self.tags

    @classmethod
    def from_strings(cls, exponents: str, tags: str):
        return cls(exponents, tags, None)

    def __init__(self, exponents: str, tags: str, other_tags: str | None):
        self.exponents = exponents if exponents != '' else None
        self.tags = tags
        self.other_tags = other_tags if other_tags != '' else None
        return
    
    @classmethod
    def copy(cls, other, tags: str):
        return cls(other.exponents, tags, other.other_tags)

    def check(self):
        if self.tags is None or self.exponents is None:
            raise CannotParseEnclChain(self)
        if len(self.tags.split('=')) != len(self.exponents.split('=')):
            raise CannotParseEnclChain(self)

    def __lt__(self, other):
        return self.__tuple__().__lt__(other.__tuple__())
    
    def __iter__(self) -> Iterator[tuple[str, str]]:
        return zip(self.tags.split('='), self.exponents.split('='), strict=True)
    
