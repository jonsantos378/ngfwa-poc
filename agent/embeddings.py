"""Local embedding model (BAAI/bge-small-en-v1.5 via fastembed, CPU/ONNX).

The model is downloaded once at image build time and baked into the image;
at runtime it loads from MODEL_CACHE with no network access. Running this
module directly downloads the model, smoke-tests it, and writes a manifest
recording exactly which model files are in the image.
"""
from __future__ import annotations

import hashlib
import json
import os
from functools import lru_cache
from pathlib import Path

from fastembed import TextEmbedding

MODEL_NAME = "BAAI/bge-small-en-v1.5"
MODEL_DIM = 384
MODEL_CACHE = os.environ.get("MODEL_CACHE", "/models")
MANIFEST_PATH = Path(MODEL_CACHE) / "MODEL_MANIFEST.json"

# BGE models retrieve better when queries (not passages) carry this instruction.
QUERY_PREFIX = "Represent this sentence for searching relevant passages: "


@lru_cache(maxsize=1)
def _model() -> TextEmbedding:
    return TextEmbedding(model_name=MODEL_NAME, cache_dir=MODEL_CACHE)


def model_id() -> str:
    """Model name plus a fingerprint of the baked-in weights, for the audit trail."""
    if MANIFEST_PATH.exists():
        return json.loads(MANIFEST_PATH.read_text())["model_id"]
    return MODEL_NAME


def embed_passages(texts: list[str]) -> list[list[float]]:
    return [vector.tolist() for vector in _model().embed(texts)]


def embed_query(text: str) -> list[float]:
    return next(iter(_model().embed([QUERY_PREFIX + text]))).tolist()


def to_pgvector(vector: list[float]) -> str:
    return "[" + ",".join(f"{x:.7f}" for x in vector) + "]"


def _write_manifest() -> dict:
    weights = sorted(Path(MODEL_CACHE).rglob("*.onnx"))
    if not weights:
        raise SystemExit(f"no ONNX weights found under {MODEL_CACHE}")
    digest = hashlib.sha256()
    for path in weights:
        digest.update(path.read_bytes())
    sha = digest.hexdigest()
    manifest = {
        "model_name": MODEL_NAME,
        "dimensions": MODEL_DIM,
        "weights_sha256": sha,
        "model_id": f"{MODEL_NAME}@sha256:{sha[:12]}",
        "files": [str(p.relative_to(MODEL_CACHE)) for p in weights],
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2))
    return manifest


if __name__ == "__main__":
    passage = embed_passages(["Sector load above 95 percent means the sector is congested."])[0]
    query = embed_query("What does a congested sector look like?")
    assert len(passage) == len(query) == MODEL_DIM, (len(passage), len(query))
    similarity = sum(a * b for a, b in zip(passage, query))
    manifest = _write_manifest()
    print(f"model OK: {manifest['model_id']}, {MODEL_DIM} dims, smoke-test similarity {similarity:.3f}")
