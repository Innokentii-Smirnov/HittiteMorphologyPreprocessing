import os
from contextlib import AbstractContextManager
from types import TracebackType

class DM(AbstractContextManager[None, None]):

    def __init__(self, direct: str):
        self.direct = direct

    def __enter__(self) -> None:
        self.old_direct = os.getcwd()
        os.chdir(self.direct)

    def __exit__(self, exc_type: type[BaseException] | None, exc: BaseException | None, traceback: TracebackType | None) -> None:
        os.chdir(self.old_direct)
