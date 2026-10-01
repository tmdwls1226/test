import re
import zlib
from functools import lru_cache

import numpy as np

from . import config


class HashEmbedder:
    """글자 2·3-gram을 해싱한 벡터. 한국어도 동작하지만 단어가 겹쳐야만 유사도가 높다."""

    name = "hash-512"
    dim = 512

    def _encode(self, text: str) -> np.ndarray:
        text = re.sub(r"\s+", " ", text.lower()).strip()
        vec = np.zeros(self.dim, dtype=np.float32)
        for n in (2, 3):
            for i in range(len(text) - n + 1):
                vec[zlib.crc32(text[i : i + n].encode()) % self.dim] += 1.0
        norm = np.linalg.norm(vec)
        return vec / norm if norm else vec

    def embed_passages(self, texts: list[str]) -> np.ndarray:
        return np.stack([self._encode(t) for t in texts])

    def embed_query(self, text: str) -> np.ndarray:
        return self._encode(text)


class SentenceTransformerEmbedder:
    """다국어 의미 임베딩 (E5 계열은 query:/passage: 접두어를 요구한다)."""

    def __init__(self, model_name: str):
        from sentence_transformers import SentenceTransformer

        self.name = model_name
        self.model = SentenceTransformer(model_name)

    def embed_passages(self, texts: list[str]) -> np.ndarray:
        return self.model.encode(
            [f"passage: {t}" for t in texts], normalize_embeddings=True
        ).astype(np.float32)

    def embed_query(self, text: str) -> np.ndarray:
        return self.model.encode(f"query: {text}", normalize_embeddings=True).astype(
            np.float32
        )


@lru_cache(maxsize=1)
def get_embedder():
    if config.EMBEDDER == "st":
        return SentenceTransformerEmbedder(config.ST_MODEL)
    return HashEmbedder()
