from abc import ABC, abstractmethod


class BaseCollector(ABC):
    @abstractmethod
    async def collect(self) -> None:
        ...
