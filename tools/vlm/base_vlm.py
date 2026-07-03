from abc import ABC, abstractmethod


class BaseVLM(ABC):
    @abstractmethod
    def analyze(self, image, prompt: str | None = None) -> dict:
        """Return structured vision understanding for an input image."""
