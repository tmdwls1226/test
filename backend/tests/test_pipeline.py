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


def test_title_search_ignores_spaces_and_case(client):
    assert [x["title"] for x in client.get("/api/search/title", params={"q": "나혼자만"}).json()] == ["나 혼자만 레벨업"]
    assert len(client.get("/api/search/title", params={"q": "solo LEVELING"}).json()) == 1


def test_title_search_treats_wildcards_literally(client):
    assert client.get("/api/search/title", params={"q": "%"}).json() == []
    assert client.get("/api/search/title", params={"q": "_"}).json() == []


def test_semantic_drops_unrelated(client):
    assert client.get("/api/search/semantic", params={"q": "zzzqqq"}).json() == []


def test_urls_are_sanitized():
    media = {**MEDIA[0], "siteUrl": "javascript:alert(1)", "coverImage": {"large": "data:text/html,x"}}
    w = to_webtoon(media)
    assert w["info_url"] is None and w["thumbnail"] is None


def test_sample_data_loads_and_searches(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "DB_PATH", tmp_path / "s.db")
    assert ingest.ingest(ingest.load_sample()) >= 10
    from app.main import app
    c = TestClient(app)
    top = c.get("/api/search/semantic", params={"q": "좀비 학교 생존"}).json()
    assert top[0]["title"] == "지금 우리 학교는"
    assert c.get("/api/health").json()["count"] >= 10


def test_empty_db_returns_empty(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "DB_PATH", tmp_path / "empty.db")
    from app.main import app
    c = TestClient(app)
    assert c.get("/api/search/semantic", params={"q": "로맨스"}).json() == []
    assert c.get("/api/search/title", params={"q": "로맨스"}).json() == []
