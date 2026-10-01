import pytest
from fastapi.testclient import TestClient

from app import config, ingest
from app.anilist import to_webtoon

MEDIA = [
    {"id": 1, "siteUrl": "https://anilist.co/manga/1", "genres": ["Action", "Fantasy"],
     "description": "최약체 헌터가 던전에서 회귀해 최강이 되는 이야기<br>레벨업 판타지",
     "tags": [{"name": "Dungeon", "rank": 90}], "title": {"native": "나 혼자만 레벨업", "english": "Solo Leveling", "romaji": "x"},
     "coverImage": {"large": "https://img/1.jpg"},
     "externalLinks": [{"site": "Kakao Webtoon", "url": "https://webtoon.kakao.com/content/1"}, {"site": "Tapas", "url": "https://tapas.io/1"}]},
    {"id": 2, "siteUrl": "https://anilist.co/manga/2", "genres": ["Romance", "Comedy"],
     "description": "고등학교에서 펼쳐지는 달달한 학원 로맨스 코미디",
     "tags": [], "title": {"native": "학원 로맨스", "english": None, "romaji": "y"},
     "coverImage": None, "externalLinks": [{"site": "Official", "url": "https://comic.naver.com/webtoon/list?titleId=2"}]},
]


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "DB_PATH", tmp_path / "t.db")
    assert ingest.ingest(to_webtoon(m) for m in MEDIA) == 2
    from app.main import app
    return TestClient(app)


def test_platforms_only_naver_kakao():
    w = to_webtoon(MEDIA[0])
    assert [p["name"] for p in w["platforms"]] == ["카카오웹툰"]
    assert "<br>" not in w["description"]


def test_title_search(client):
    r = client.get("/api/search/title", params={"q": "Solo"}).json()
    assert [x["title"] for x in r] == ["나 혼자만 레벨업"]


def test_semantic_search_ranks_by_description(client):
    r = client.get("/api/search/semantic", params={"q": "학교 배경 로맨스 코미디"}).json()
    assert r[0]["title"] == "학원 로맨스"
    assert r[0]["platforms"][0]["name"] == "네이버웹툰"


def test_reingest_is_idempotent(client):
    assert ingest.ingest(to_webtoon(m) for m in MEDIA) == 2
    assert len(client.get("/api/search/title", params={"q": "로맨스"}).json()) == 1
