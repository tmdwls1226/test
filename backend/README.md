# SEARCHTOON 백엔드 (FastAPI + SQLite)

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

python -m app.ingest --sample          # 개발용 샘플 적재 (오프라인)
python -m app.ingest --pages 10      # AniList 한국 웹툰 적재 (페이지당 50개, 네트워크 필요)
uvicorn app.main:app --reload        # http://127.0.0.1:8000
python -m pytest                     # 테스트
```

프론트는 `npm run dev` (vite가 `/api`를 8000번으로 프록시).

## 임베딩 모델
- 기본 `EMBEDDER=hash`: 모델 다운로드 없이 동작하는 개발용. 글자가 겹쳐야만 유사해서 **의미 검색은 아님**(낮은 유사도 결과는 걸러냄).
- 실제 의미 검색: `pip install sentence-transformers` 후 `EMBEDDER=st`로 적재·서버 실행
  (기본 모델 `intfloat/multilingual-e5-small`, `ST_MODEL`로 변경). 모델을 바꾸면 다시 적재해야 한다.

## API
- `GET /api/search/title?q=` 제목 부분 일치
- `GET /api/search/semantic?q=` 줄거리·장르·태그 임베딩 유사도

`GET /api/health` 는 적재된 작품 수와 임베더 이름을 반환한다. 배포 시 다른 출처에서 호출하려면 `CORS_ORIGINS=https://example.com`.
