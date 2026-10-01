import os
from pathlib import Path

DB_PATH = Path(os.getenv("SEARCHTOON_DB", Path(__file__).resolve().parent.parent / "searchtoon.db"))

# hash: 모델 다운로드 없이 동작하는 개발/테스트용 (글자 n-gram 해싱, 의미 이해 없음)
# st:   sentence-transformers 다국어 모델 (실제 의미 검색, pip install sentence-transformers 필요)
EMBEDDER = os.getenv("EMBEDDER", "hash")
ST_MODEL = os.getenv("ST_MODEL", "intfloat/multilingual-e5-small")

# 쉼표로 구분한 허용 출처. 개발 중에는 vite 프록시를 쓰므로 필요 없다.
CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", "").split(",") if o.strip()]
