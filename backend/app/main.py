from fastapi import FastAPI, Query

from . import db
from .embedding import get_embedder

app = FastAPI(title="SEARCHTOON API")


@app.get("/api/health")
def health():
    return {"ok": True}


@app.get("/api/search/title")
def search_title(q: str = Query(min_length=1), limit: int = Query(24, le=100)):
    """제목(한글/영문) 부분 일치 검색."""
    like = f"%{q}%"
    with db.close(db.connect()) as conn:
        rows = conn.execute(
            "SELECT * FROM webtoons WHERE title LIKE ? OR subtitle LIKE ? LIMIT ?",
            (like, like, limit),
        ).fetchall()
    return [db.row_to_dict(r) for r in rows]


@app.get("/api/search/semantic")
def search_semantic(q: str = Query(min_length=1), limit: int = Query(24, le=100)):
    """줄거리·장르·태그 임베딩 기반 '설명으로 검색'."""
    embedder = get_embedder()
    with db.close(db.connect()) as conn:
        rows, matrix = db.all_embeddings(conn, embedder.name)
    if not rows:
        return []
    scores = matrix @ embedder.embed_query(q)  # 벡터가 정규화되어 있어 내적 = 코사인 유사도
    top = scores.argsort()[::-1][:limit]
    return [{**db.row_to_dict(rows[i]), "score": round(float(scores[i]), 4)} for i in top]
