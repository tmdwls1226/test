from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from . import config, db
from .embedding import get_embedder
from .textutil import normalize

app = FastAPI(title="SEARCHTOON API")

if config.CORS_ORIGINS:
    app.add_middleware(CORSMiddleware, allow_origins=config.CORS_ORIGINS, allow_methods=["GET"])

Q = Query(min_length=1, max_length=100)


@app.get("/api/health")
def health():
    return {"ok": True, "count": db.count(), "embedder": get_embedder().name}


@app.get("/api/search/title")
def search_title(q: str = Q, limit: int = Query(24, ge=1, le=100)):
    """제목(한글/영문) 부분 일치 검색. 공백·대소문자는 무시한다."""
    conn = db.connect()
    try:
        rows = db.search_title(conn, q, limit)
    finally:
        conn.close()
    return [db.row_to_dict(r) for r in rows]


@app.get("/api/search/semantic")
def search_semantic(q: str = Q, limit: int = Query(24, ge=1, le=100)):
    """줄거리·장르·태그 임베딩 기반 '설명으로 검색'. 제목이 일치하면 가산점을 준다."""
    embedder = get_embedder()
    rows, matrix = db.cached_embeddings(embedder.name)
    if not rows:
        return []
    scores = matrix @ embedder.embed_query(q)
    nq = normalize(q)
    ranked = []
    for row, score in zip(rows, scores):
        title_hit = nq in normalize(row["title"])
        if score >= embedder.min_score or title_hit:
            ranked.append((float(score) + (0.3 if title_hit else 0.0), row))
    ranked.sort(key=lambda x: -x[0])
    return [{**db.row_to_dict(r), "score": round(s, 4)} for s, r in ranked[:limit]]
