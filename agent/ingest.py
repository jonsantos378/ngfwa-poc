"""Load the knowledge base into Postgres/pgvector, one row per document section.

Idempotent: a document version whose chunks are unchanged is skipped. A new
version of a document is stored alongside the old one and becomes current;
older versions stay queryable, so answers that cited them remain traceable.
"""
from __future__ import annotations

import hashlib
import os
import re
from pathlib import Path

import psycopg

from embeddings import MODEL_DIM, embed_passages, model_id, to_pgvector

KB_DIR = Path(os.environ.get("KB_DIR", Path(__file__).parent / "kb"))
DATABASE_URL = os.environ["DATABASE_URL"]

SCHEMA_SQL = f"""
CREATE EXTENSION IF NOT EXISTS vector;
CREATE TABLE IF NOT EXISTS kb_chunks (
    id              BIGSERIAL   PRIMARY KEY,
    doc_id          TEXT        NOT NULL,
    doc_version     TEXT        NOT NULL,
    doc_title       TEXT        NOT NULL,
    section         TEXT        NOT NULL,
    chunk_index     INT         NOT NULL,
    content         TEXT        NOT NULL,
    content_sha256  TEXT        NOT NULL,
    embedding       VECTOR({MODEL_DIM}) NOT NULL,
    embedding_model TEXT        NOT NULL,
    is_current      BOOLEAN     NOT NULL DEFAULT TRUE,
    ingested_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (doc_id, doc_version, chunk_index)
);
CREATE INDEX IF NOT EXISTS idx_kb_chunks_embedding
    ON kb_chunks USING hnsw (embedding vector_cosine_ops);
"""


def parse_document(path: Path) -> tuple[dict, list[tuple[str, str]]]:
    text = path.read_text()
    match = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.DOTALL)
    if not match:
        raise ValueError(f"{path.name}: missing front matter")
    meta = {}
    for line in match.group(1).splitlines():
        key, _, value = line.partition(":")
        meta[key.strip()] = value.strip().strip('"')
    sections = []
    for block in re.split(r"(?m)^## ", match.group(2))[1:]:
        heading, _, body = block.partition("\n")
        sections.append((heading.strip(), body.strip()))
    return meta, sections


def chunk_texts(meta: dict, sections: list[tuple[str, str]]) -> list[tuple[str, str]]:
    # The document title travels with every chunk so a section retrieved
    # on its own still says what it belongs to.
    return [(heading, f"{meta['title']} — {heading}\n\n{body}") for heading, body in sections]


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def main() -> None:
    model = model_id()
    stored = skipped = 0
    with psycopg.connect(DATABASE_URL) as conn:
        conn.execute(SCHEMA_SQL)
        for path in sorted(KB_DIR.glob("KB-*.md")):
            meta, sections = parse_document(path)
            chunks = chunk_texts(meta, sections)
            hashes = [sha256(text) for _, text in chunks]

            existing = conn.execute(
                "SELECT content_sha256 FROM kb_chunks WHERE doc_id = %s AND doc_version = %s ORDER BY chunk_index",
                (meta["doc_id"], meta["version"]),
            ).fetchall()
            if [row[0] for row in existing] == hashes:
                skipped += 1
                continue

            vectors = embed_passages([text for _, text in chunks])
            with conn.transaction():
                conn.execute(
                    "DELETE FROM kb_chunks WHERE doc_id = %s AND doc_version = %s",
                    (meta["doc_id"], meta["version"]),
                )
                conn.execute(
                    "UPDATE kb_chunks SET is_current = FALSE WHERE doc_id = %s AND doc_version <> %s",
                    (meta["doc_id"], meta["version"]),
                )
                for index, ((heading, text), digest, vector) in enumerate(zip(chunks, hashes, vectors)):
                    conn.execute(
                        """INSERT INTO kb_chunks (doc_id, doc_version, doc_title, section, chunk_index,
                                                  content, content_sha256, embedding, embedding_model)
                           VALUES (%s, %s, %s, %s, %s, %s, %s, %s::vector, %s)""",
                        (meta["doc_id"], meta["version"], meta["title"], heading, index,
                         text, digest, to_pgvector(vector), model),
                    )
            stored += 1
            print(f"stored {meta['doc_id']} v{meta['version']}: {len(chunks)} chunks")

        total = conn.execute("SELECT count(*) FROM kb_chunks WHERE is_current").fetchone()[0]
    print(f"done: {stored} documents stored, {skipped} unchanged, {total} current chunks, model {model}")


if __name__ == "__main__":
    main()
