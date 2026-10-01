import json
import sqlite3
from contextlib import closing

import numpy as np

from . import config

SCHEMA = """
CREATE TABLE IF NOT EXISTS webtoons (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  source TEXT NOT NULL,
  source_id TEXT NOT NULL,
  title TEXT NOT NULL,
  subtitle TEXT,
  description TEXT,
  genres TEXT NOT NULL DEFAULT '[]',
  tags TEXT NOT NULL DEFAULT '[]',
  thumbnail TEXT,
  info_url TEXT,
  platforms TEXT NOT NULL DEFAULT '[]',
  embedding BLOB,
  embedding_model TEXT,
  UNIQUE (source, source_id)
);
"""


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    return conn


def upsert_webtoon(conn: sqlite3.Connection, w: dict, embedding: np.ndarray, model: str):
    conn.execute(
        """
        INSERT INTO webtoons (source, source_id, title, subtitle, description, genres,
                              tags, thumbnail, info_url, platforms, embedding, embedding_model)
        VALUES (:source, :source_id, :title, :subtitle, :description, :genres,
                :tags, :thumbnail, :info_url, :platforms, :embedding, :model)
        ON CONFLICT (source, source_id) DO UPDATE SET
          title=excluded.title, subtitle=excluded.subtitle, description=excluded.description,
          genres=excluded.genres, tags=excluded.tags, thumbnail=excluded.thumbnail,
          info_url=excluded.info_url, platforms=excluded.platforms,
          embedding=excluded.embedding, embedding_model=excluded.embedding_model
        """,
        {
            **w,
            "genres": json.dumps(w["genres"], ensure_ascii=False),
            "tags": json.dumps(w["tags"], ensure_ascii=False),
            "platforms": json.dumps(w["platforms"], ensure_ascii=False),
            "embedding": embedding.astype(np.float32).tobytes(),
            "model": model,
        },
    )


def row_to_dict(row: sqlite3.Row) -> dict:
    """프론트 카드(WebtoonCard)가 쓰는 형태로 변환."""
    return {
        "id": f"{row['source']}-{row['source_id']}",
        "title": row["title"],
        "subtitle": row["subtitle"],
        "thumbnail": row["thumbnail"],
        "platforms": json.loads(row["platforms"]),
        "infoUrl": row["info_url"],
        "source": row["source"],
        "genres": json.loads(row["genres"]),
        "description": row["description"],
    }


def all_embeddings(conn: sqlite3.Connection, model: str):
    """현재 임베딩 모델로 만든 벡터만 (rows, matrix)로 반환."""
    rows = conn.execute(
        "SELECT * FROM webtoons WHERE embedding IS NOT NULL AND embedding_model = ?",
        (model,),
    ).fetchall()
    if not rows:
        return [], np.zeros((0, 0), dtype=np.float32)
    matrix = np.stack([np.frombuffer(r["embedding"], dtype=np.float32) for r in rows])
    return rows, matrix


def close(conn):
    return closing(conn)
