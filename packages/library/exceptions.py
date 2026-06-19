from typing import TypeVar
TKey = TypeVar('TKey')
TValue = TypeVar('TValue')

class InvalidOperationException(Exception):
    
    def __init__(self, text: str):
        self.text = text

    def __str__(self) -> str:
        return self.text

class MissingKeyException[TKey, TValue](Exception):
    
    def __init__(self, key: TKey, dic: dict[TKey, TValue]):
        self.key = key
        self.dic = dic

    def __str__(self) -> str:
        string = "The selected index '{0}' is not in the dictionary: {1}".format(self.key, self.dic)
        return string

class InitializationError(Exception):
    
    def __init__(self) -> None:
        self.text = 'Initialization failed'

    def __str__(self) -> str:
        return self.text

