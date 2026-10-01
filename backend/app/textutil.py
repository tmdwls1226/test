import re


def normalize(text: str) -> str:
    """제목 비교용: 소문자 + 모든 공백 제거 ('나 혼자만' == '나혼자만')."""
    return re.sub(r"\s+", "", text or "").lower()


def escape_like(text: str) -> str:
    """LIKE 와일드카드(%, _)를 문자 그대로 검색하도록 이스케이프 (ESCAPE '\\')."""
    return text.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def safe_url(url: str | None) -> str | None:
    """http(s) URL만 허용 (javascript: 등 차단)."""
    return url if url and re.match(r"^https?://", url, re.I) else None
