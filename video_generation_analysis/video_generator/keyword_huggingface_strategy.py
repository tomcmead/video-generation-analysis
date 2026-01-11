import logging

from transformers import pipeline

from video_generation_analysis.config import HUGGING_FACE_MODEL
from video_generation_analysis.video_generator.keyword_strategy import KeywordStrategy


class KeywordHuggingFaceStrategy(KeywordStrategy):
    """Generates new description using Hugging Face Transformers model"""

    def __init__(self):
        self._logger: logging.Logger = logging.getLogger(__name__)
        self._model = None
        try:
            self._model = pipeline("text2text-generation", model=HUGGING_FACE_MODEL)
        except Exception as e:
            self._logger.error(f"Failed to load Hugging Face model: {e}")

    def generate(self, keywords: list[str], min_length: int, max_length: int) -> str:
        """Generates new description based on keywords using Hugging Face model"""
        if self._model is None:
            return ""

        description = self._model(
            " ".join(keywords), max_new_tokens=max_length, min_length=min_length
        )

        return description[0]["generated_text"]
