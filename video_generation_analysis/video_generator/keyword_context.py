from abc import ABC, abstractmethod


class KeywordContext(ABC):
    """Strategy interface for keyword generation algorithm."""

    @abstractmethod
    def generate_keywords(
        self, current_keywords: list[str], num_new_keywords: int
    ) -> list[str]:
        """generates new keywords based on current keywords provided."""
        pass
