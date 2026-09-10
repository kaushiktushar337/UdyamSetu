"""Dependency-free 384D text hashing fallback for the Vercel runtime.

The original local MiniLM model is intentionally not bundled into Vercel because
its PyTorch/CUDA dependency graph exceeds Vercel's function bundle limit.  This
module preserves the 384-dimensional interface used by the application while
keeping the deployment package tiny.  Existing database embeddings are not
modified.
"""
from __future__ import annotations
import hashlib, math, re

_DIM = 384
_LOADED = False
_TOKEN_RE = re.compile(r"\w+", re.UNICODE)

def _vector(text: str):
    v = [0.0] * _DIM
    tokens = _TOKEN_RE.findall((text or "").lower())
    for token in tokens:
        digest = hashlib.blake2b(token.encode("utf-8"), digest_size=16).digest()
        for j in range(0, 16, 4):
            idx = int.from_bytes(digest[j:j+2], "little") % _DIM
            sign = 1.0 if digest[j+2] & 1 else -1.0
            v[idx] += sign
    norm = math.sqrt(sum(x*x for x in v)) or 1.0
    return [x / norm for x in v]

class _HashEmbeddingModel:
    def encode(self, sentences, normalize_embeddings=True, convert_to_numpy=False, **kwargs):
        if isinstance(sentences, str):
            return _vector(sentences)
        return [_vector(s) for s in sentences]

def get_embedding_model():
    global _LOADED
    _LOADED = True
    return _HashEmbeddingModel()

def embedding_model_loaded() -> bool:
    return _LOADED
