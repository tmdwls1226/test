"""AniList 한국 웹툰을 가져와 임베딩과 함께 DB에 적재한다.

사용: python -m app.ingest [--pages 10]
"""
import argparse

from . import db
from .anilist import fetch_webtoons
from .embedding import get_embedder


def embedding_text(w: dict) -> str:
    parts = [w["title"], w["subtitle"] or "", " ".join(w["genres"]), " ".join(w["tags"]), w["description"]]
    return "\n".join(p for p in parts if p)


def ingest(webtoons, batch_size: int = 32) -> int:
    embedder = get_embedder()
    conn = db.connect()
    count, batch = 0, []

    def flush():
        nonlocal count
        if not batch:
            return
        vectors = embedder.embed_passages([embedding_text(w) for w in batch])
        for w, vec in zip(batch, vectors):
            db.upsert_webtoon(conn, w, vec, embedder.name)
        conn.commit()
        count += len(batch)
        batch.clear()

    for w in webtoons:
        batch.append(w)
        if len(batch) >= batch_size:
            flush()
    flush()
    conn.close()
    return count


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pages", type=int, default=10, help="가져올 AniList 페이지 수 (페이지당 50개)")
    args = parser.parse_args()
    print(f"{ingest(fetch_webtoons(args.pages))}개 적재 완료")
