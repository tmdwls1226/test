const ENDPOINT = "https://graphql.anilist.co";

// 한국 웹툰(countryOfOrigin: KR)만 검색
const QUERY = `
  query ($search: String) {
    Page(perPage: 24) {
      media(search: $search, type: MANGA, countryOfOrigin: KR, sort: SEARCH_MATCH) {
        id
        siteUrl
        title { romaji english native }
        coverImage { large }
        externalLinks { site url type }
      }
    }
  }
`;

// 표시할 플랫폼: AniList externalLinks의 site 이름 또는 URL 도메인으로 판별
const PLATFORMS = [
  { label: "네이버웹툰", site: /naver/i, host: /(^|\.)naver\.com$/ },
  { label: "카카오웹툰", site: /kakao/i, host: /(^|\.)kakao\.com$/ },
];

function hostOf(url) {
  try {
    return new URL(url).hostname;
  } catch {
    return "";
  }
}

function pickPlatforms(links = []) {
  const found = new Map();
  for (const { site, url } of links) {
    const platform = PLATFORMS.find(
      (p) => p.site.test(site) || p.host.test(hostOf(url)),
    );
    if (platform && !found.has(platform.label)) {
      found.set(platform.label, { name: platform.label, url });
    }
  }
  return [...found.values()];
}

function toWebtoon(media) {
  const { title } = media;
  return {
    id: `anilist-${media.id}`,
    title: title.native || title.english || title.romaji,
    subtitle: title.english || title.romaji,
    thumbnail: media.coverImage?.large ?? null,
    platforms: pickPlatforms(media.externalLinks),
    infoUrl: media.siteUrl,
    source: "AniList",
  };
}

export async function searchAniList(search, signal) {
  const res = await fetch(ENDPOINT, {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify({ query: QUERY, variables: { search } }),
    signal,
  });
  if (!res.ok) throw new Error(`AniList 요청 실패 (${res.status})`);
  const json = await res.json();
  if (json.errors) throw new Error(json.errors[0].message);
  return json.data.Page.media.map(toWebtoon);
}
