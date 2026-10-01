# SEARCHTOON

웹툰 검색 사이트. 제목으로 찾거나, 줄거리·분위기를 설명해서 찾을 수 있다.

- 프론트: React + Vite + Sass (`src/`)
- 백엔드: FastAPI + SQLite + 임베딩 검색 (`backend/`, 자세한 내용은 [backend/README.md](backend/README.md))

## 빠른 시작

```bash
npm run dev:all      # 백엔드 venv 준비 → 샘플 데이터 적재(DB가 비었을 때) → 백엔드(8000) + 프론트(5173)
```

http://localhost:5173 에서 확인. 검색창 왼쪽에서 **제목 / 설명** 검색을 고른다.

## 데이터

| 방법 | 명령 | 비고 |
|---|---|---|
| 샘플 (개발용) | `cd backend && python -m app.ingest --sample` | 오프라인 가능. 플랫폼 링크는 플랫폼 홈이며 작품별 링크가 아님 |
| AniList 한국 웹툰 | `cd backend && python -m app.ingest --pages 10` | 네트워크 필요. 네이버/카카오 링크가 등록된 작품만 플랫폼이 표시됨 |

## 명령어

```bash
npm run lint && npm run build   # 프론트 검사/빌드
npm run test:api                # 백엔드 테스트 (backend/.venv 필요)
```

## 로드맵
1. ✅ 백엔드/DB, AniList 적재, 설명으로 검색
2. 네이버·카카오 데이터 수집 (약관/robots.txt 확인 후 방식 결정)
3. 추천 문장 생성(RAG의 G), 실제 임베딩 모델(`EMBEDDER=st`) 적용
