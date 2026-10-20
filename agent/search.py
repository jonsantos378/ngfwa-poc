"""Semantic search over the knowledge base: python search.py "question" [k]"""
from __future__ import annotations

import os
import sys

import psycopg

from embeddings import embed_query, to_pgvector

SEARCH_SQL = """
SELECT doc_id, doc_version, section, 1 - (embedding <=> %(q)s::vector) AS score, content
FROM kb_chunks
WHERE is_current
ORDER BY embedding <=> %(q)s::vector
LIMIT %(k)s
"""


def search(question: str, k: int = 3) -> list[tuple]:
    with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
        return conn.execute(SEARCH_SQL, {"q": to_pgvector(embed_query(question)), "k": k}).fetchall()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit('usage: python search.py "question" [k]')
    question = sys.argv[1]
    k = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    print(f"Q: {question}")
    for doc_id, version, section, score, content in search(question, k):
        snippet = " ".join(content.split("\n\n", 1)[-1].split())[:140]
        print(f"  {score:.3f}  {doc_id} v{version} § {section}\n         {snippet}…")
