from abc import ABC, abstractmethod


class KeywordStrategy(ABC):
    """Strategy interface for keyword generation algorithm."""

    @abstractmethod
    def generate(self, keywords: list[str], min_length: int, max_length: int) -> str:
        """generates new keywords based on current keywords provided."""
        pass
