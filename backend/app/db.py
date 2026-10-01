import json
import sqlite3
import numpy as np

from . import config
from .textutil import escape_like, normalize

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


def count() -> int:
    conn = connect()
    try:
        return conn.execute("SELECT COUNT(*) FROM webtoons").fetchone()[0]
    finally:
        conn.close()


def search_title(conn: sqlite3.Connection, query: str, limit: int) -> list[sqlite3.Row]:
    """공백·대소문자 무시 부분 일치. 정확히 일치 > 앞부분 일치 > 포함 순으로 정렬."""
    q = escape_like(normalize(query))
    cols = "REPLACE(title, ' ', '')"
    sub = "REPLACE(COALESCE(subtitle, ''), ' ', '')"
    return conn.execute(
        f"""
        SELECT * FROM webtoons
        WHERE {cols} LIKE :any ESCAPE '\\' OR {sub} LIKE :any ESCAPE '\\'
        ORDER BY CASE
                   WHEN LOWER({cols}) = :exact OR LOWER({sub}) = :exact THEN 0
                   WHEN {cols} LIKE :prefix ESCAPE '\\' OR {sub} LIKE :prefix ESCAPE '\\' THEN 1
                   ELSE 2 END,
                 title
        LIMIT :limit
        """,
        {"any": f"%{q}%", "prefix": f"{q}%", "exact": normalize(query), "limit": limit},
    ).fetchall()


_cache: dict = {}


def cached_embeddings(model: str):
    """(rows, matrix). DB 파일이 바뀌면(mtime) 다시 읽고, 아니면 메모리 캐시를 쓴다."""
    stamp = config.DB_PATH.stat().st_mtime_ns if config.DB_PATH.exists() else 0
    key = (str(config.DB_PATH), model)
    hit = _cache.get(key)
    if hit and hit[0] == stamp:
        return hit[1], hit[2]
    conn = connect()
    try:
        rows, matrix = all_embeddings(conn, model)
    finally:
        conn.close()
    _cache[key] = (stamp, rows, matrix)
    return rows, matrix
