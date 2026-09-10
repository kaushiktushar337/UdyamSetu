from __future__ import annotations

import os
import threading

_MODEL = None
_LOCK = threading.Lock()


def get_embedding_model():
    """Return the single process-wide SentenceTransformer instance.

    The decision engine and chatbot deliberately share one model instance.
    Loading the same multilingual model twice is a major memory cost on small
    Render instances and can cause an out-of-memory restart.
    """
    global _MODEL

    if _MODEL is not None:
        return _MODEL

    with _LOCK:
        if _MODEL is None:
            # Keep tokenizer/thread overhead bounded on small CPU instances.
            os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
            os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")
            try:
                import torch
                torch.set_num_threads(max(1, min(2, os.cpu_count() or 1)))
                torch.set_num_interop_threads(1)
            except Exception:
                pass

            from sentence_transformers import SentenceTransformer

            model_name = os.getenv(
                "MODEL_NAME",
                "paraphrase-multilingual-MiniLM-L12-v2",
            )
            _MODEL = SentenceTransformer(model_name, device="cpu")

    return _MODEL


def embedding_model_loaded() -> bool:
    return _MODEL is not None
