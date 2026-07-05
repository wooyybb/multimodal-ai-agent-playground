from abc import ABC, abstractmethod


class BaseReasoner(ABC):
    @abstractmethod
    def reason(self, system_prompt: str, user_prompt: str) -> dict:
        """Return structured JSON-style reasoning output."""
