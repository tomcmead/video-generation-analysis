import logging

import gensim.downloader as api

from video_generation_analysis.config import GENSIM_MODEL_NAME
from video_generation_analysis.video_generator.keyword_strategy import KeywordStrategy


class KeywordGensimStrategy(KeywordStrategy):
    """Generates new keywords using Gensim word2vec model similarity"""

    def __init__(self):
        self._logger: logging.Logger = logging.getLogger(__name__)
        self._model = None
        try:
            self._model = api.load(GENSIM_MODEL_NAME)
        except Exception as e:
            self._logger.error(f"Failed to load gensim model: {e}")

    def generate_keywords(
        self, current_keywords: list[str], num_new_keywords: int
    ) -> list[str]:
        """Generates new keywords based on current keywords using Gensim model"""
        if self._model is None:
            return []

        new_keywords = {}
        lower_keywords = [keyword.lower() for keyword in current_keywords]

        for keyword in lower_keywords:
            try:
                similar = self._model.most_similar(keyword, topn=num_new_keywords)
                for word, similarity in similar:
                    if word not in new_keywords:
                        new_keywords[word] = similarity
                    else:
                        new_keywords[word] += similarity

            except KeyError:
                self._logger.debug(f"'{keyword}' not found in model vocabulary.")

        sorted_keywords = sorted(
            new_keywords.items(), key=lambda item: item[1], reverse=True
        )
        keywords = [keyword[0] for keyword in sorted_keywords]
        return keywords[:num_new_keywords]
