import re
import time
from html import unescape
from urllib.parse import urlparse

import httpx

ENDPOINT = "https://graphql.anilist.co"

QUERY = """
query ($page: Int) {
  Page(page: $page, perPage: 50) {
    pageInfo { hasNextPage }
    media(type: MANGA, countryOfOrigin: KR, sort: POPULARITY_DESC) {
      id siteUrl description(asHtml: false) genres
      tags { name rank }
      title { romaji english native }
      coverImage { large }
      externalLinks { site url }
    }
  }
}
"""

# 프론트(src/api/anilist.js)와 동일한 플랫폼 기준
PLATFORMS = [
    ("네이버웹툰", re.compile("naver", re.I), re.compile(r"(^|\.)naver\.com$")),
    ("카카오웹툰", re.compile("kakao", re.I), re.compile(r"(^|\.)kakao\.com$")),
]


def pick_platforms(links: list[dict]) -> list[dict]:
    found: dict[str, dict] = {}
    for link in links or []:
        host = urlparse(link["url"]).hostname or ""
        for label, site_re, host_re in PLATFORMS:
            if label not in found and (site_re.search(link["site"]) or host_re.search(host)):
                found[label] = {"name": label, "url": link["url"]}
    return list(found.values())


def clean_description(text: str | None) -> str:
    text = re.sub(r"<[^>]+>", " ", text or "")
    return re.sub(r"\s+", " ", unescape(text)).strip()


def to_webtoon(media: dict) -> dict:
    t = media["title"]
    return {
        "source": "anilist",
        "source_id": str(media["id"]),
        "title": t.get("native") or t.get("english") or t["romaji"],
        "subtitle": t.get("english") or t.get("romaji"),
        "description": clean_description(media.get("description")),
        "genres": media.get("genres") or [],
        "tags": [x["name"] for x in sorted(media.get("tags") or [], key=lambda x: -x["rank"])[:10]],
        "thumbnail": (media.get("coverImage") or {}).get("large"),
        "info_url": media.get("siteUrl"),
        "platforms": pick_platforms(media.get("externalLinks")),
    }


def fetch_webtoons(max_pages: int = 10, client: httpx.Client | None = None):
    """AniList에서 한국 웹툰을 인기순으로 페이지 단위로 가져온다 (제너레이터)."""
    own = client is None
    client = client or httpx.Client(timeout=30)
    try:
        for page in range(1, max_pages + 1):
            res = client.post(ENDPOINT, json={"query": QUERY, "variables": {"page": page}})
            res.raise_for_status()
            data = res.json()["data"]["Page"]
            yield from (to_webtoon(m) for m in data["media"])
            if not data["pageInfo"]["hasNextPage"]:
                break
            time.sleep(1)  # AniList 제한: 분당 90회
    finally:
        if own:
            client.close()
