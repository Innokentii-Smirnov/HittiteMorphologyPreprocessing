from __future__ import annotations
from library.read import read_text
from library.write import write_text
from typing import TypeVar, Sequence, Type, Iterable
from functools import partial

def to_string(x: object) -> str:
    if isinstance(x, Serializable):
        return x.to_string()
    elif isinstance(x, str):
        return x
    else:
        return repr(x)

def from_string(string: str) -> str | None:
  if string == 'None':
    return None
  return string

TSerializable = TypeVar('TSerializable', bound='BasicSerializable')

class BasicSerializable:

    @staticmethod
    def element_func(x: str) -> str | None:
        if x == 'None':
            return None
        return x

    sep = '%'

    def get_elements(self) -> Sequence[object]:
        raise NotImplementedError
    
    def __tuple__(self) -> tuple[object, ...]:
        return tuple(self.get_elements())
    
    def __eq__(self, other: object) -> bool:
        if isinstance(other, BasicSerializable):
            return self.__tuple__() == other.__tuple__()
        return False

    def __lt__(self, other: object) -> bool:
        if isinstance(other, BasicSerializable):
            return self.__tuple__().__lt__(other.__tuple__())
        return False

    def __gt__(self, other: object) -> bool:
        if isinstance(other, BasicSerializable):
            return self.__tuple__().__gt__(other.__tuple__())
        return False

    @classmethod
    def from_strings(cls: Type[TSerializable], strings: Iterable[str | None]) -> TSerializable:
        raise NotImplementedError

    def to_string(self) -> str:
        return self.sep.join(map(to_string, self.get_elements()))
    
    def __repr__(self) -> str:
        return self.to_string()

    @classmethod
    def from_string(cls: Type[TSerializable], string: str) -> TSerializable:
        return cls.from_strings(map(cls.element_func, string.split(cls.sep)))

    def save(self, filename: str) -> None:
        write_text(self.to_string(), filename)

    @classmethod
    def load(cls: Type[TSerializable], filename: str) -> TSerializable:
        return cls.from_string(read_text(filename))

class Serializable(BasicSerializable):

    def __hash__(self) -> int:
        return self.__tuple__().__hash__()
    
T = TypeVar('T')

class SerializableList[T](BasicSerializable, list[T]):
    
    @staticmethod
    def get_element(string: str) -> T:
        raise NotImplementedError

    def get_elements(self) -> Sequence[T]:
        return self

    @classmethod
    def from_string(cls, string: str) -> SerializableList[T]:
        return cls(map(cls.get_element, string.split(cls.sep))) if string != '' else cls()
    
TKey = TypeVar('TKey')
TValue = TypeVar('TValue')

class SerializableDict[TKey, TValue](BasicSerializable, dict[TKey, TValue]):
    separator = ' \u2192 '
    sep = ' \u222a '

    @staticmethod
    def get_key(string: str) -> TKey:
        raise NotImplementedError
    
    @staticmethod
    def get_value(string: str) -> TValue:
        raise NotImplementedError
    
    def get_elements(self) -> Sequence[str]:
        return [self.separator.join([to_string(key), to_string(value)]) for key, value in self.items()]

    @classmethod
    def from_string(cls, string: str) -> SerializableDict[TKey, TValue]:
        d: SerializableDict[TKey, TValue] = cls()
        if string != '':
            for elem in string.split(cls.sep):
                str_key, str_value = elem.split(cls.separator, 1)
                key = cls.get_key(str_key)
                value = cls.get_value(str_value)
                d[key] = value
        return d

class StringList(SerializableList[str]):

    @staticmethod
    def get_element(string: str) -> str:
      return string

class StringStringDict(SerializableDict[str | None, str | None]):

    @staticmethod
    def get_key(string: str) -> str | None:
      return from_string(string)

    @staticmethod
    def get_value(string: str) -> str | None:
      return from_string(string)

        
