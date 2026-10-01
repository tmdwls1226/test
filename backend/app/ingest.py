"""웹툰 데이터를 임베딩과 함께 DB에 적재한다.

사용:
  python -m app.ingest [--pages 10]     # AniList 한국 웹툰 (네트워크 필요)
  python -m app.ingest --sample         # 개발용 샘플 데이터 (오프라인)
  python -m app.ingest --sample --if-empty
"""
import argparse
import json
from pathlib import Path

from . import db
from .anilist import fetch_webtoons
from .embedding import get_embedder

PLATFORM_HOME = {
    "네이버웹툰": "https://comic.naver.com/webtoon",
    "카카오웹툰": "https://webtoon.kakao.com",
}


def embedding_text(w: dict) -> str:
    parts = [w["title"], w["subtitle"] or "", " ".join(w["genres"]), " ".join(w["tags"]), w["description"]]
    return "\n".join(p for p in parts if p)


def load_sample() -> list[dict]:
    """개발용 샘플. 플랫폼 링크는 작품별 URL이 아니라 플랫폼 홈이다."""
    raw = json.loads((Path(__file__).parent / "sample_data.json").read_text(encoding="utf-8"))
    return [
        {
            "source": "sample",
            "source_id": item["title"],
            "title": item["title"],
            "subtitle": item["subtitle"],
            "description": item["description"],
            "genres": item["genres"],
            "tags": item["tags"],
            "thumbnail": None,
            "info_url": None,
            "platforms": [{"name": item["platform"], "url": PLATFORM_HOME[item["platform"]]}],
        }
        for item in raw
    ]


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

    try:
        for w in webtoons:
            batch.append(w)
            if len(batch) >= batch_size:
                flush()
        flush()
    finally:
        conn.close()
    return count


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pages", type=int, default=10, help="가져올 AniList 페이지 수 (페이지당 50개)")
    parser.add_argument("--sample", action="store_true", help="AniList 대신 내장 샘플 데이터 적재")
    parser.add_argument("--if-empty", action="store_true", help="DB가 비어 있을 때만 적재")
    args = parser.parse_args()

    if args.if_empty and db.count() > 0:
        print(f"이미 {db.count()}개가 있어 건너뜁니다")
    else:
        source = load_sample() if args.sample else fetch_webtoons(args.pages)
        print(f"{ingest(source)}개 적재 완료")
