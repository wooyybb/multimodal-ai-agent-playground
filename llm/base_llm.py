from abc import ABC, abstractmethod


class BaseLLM(ABC):
    @abstractmethod
    def reason(self, state: dict) -> dict:
        raise NotImplementedError

    @abstractmethod
    def critic(self, state: dict, mode: str = "mock") -> dict:
        raise NotImplementedError

    @abstractmethod
    def optimize(self, state: dict, mode: str = "mock") -> dict:
        raise NotImplementedError
