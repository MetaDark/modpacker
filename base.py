from abc import ABC, abstractmethod
from typing import Iterable
from url import Url

class Mod(ABC):
    @abstractmethod
    def url(self) -> Url:
        pass

    def doc(self) -> Url:
        return self.url()

    @abstractmethod
    def latest(self, mc_version: str) -> Iterable[Url]:
        pass

class Repo(ABC):
    @abstractmethod
    def url(self) -> Url:
        pass

    @abstractmethod
    def mod(self, mod_id: str) -> Mod:
        pass
