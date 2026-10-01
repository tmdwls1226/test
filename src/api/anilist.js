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

// 웹툰을 볼 수 있는 플랫폼 (AniList externalLinks의 site 이름 기준)
const PLATFORMS = [
  "Webtoon",
  "Naver",
  "Kakao",
  "Tapas",
  "Lezhin",
  "Tappytoon",
  "Manta",
  "Toomics",
  "Toptoon",
  "Bomtoon",
  "Ridi",
  "Munpia",
  "Mr. Blue",
];

function pickPlatforms(links = []) {
  return links
    .filter(
      (link) =>
        link.type === "STREAMING" ||
        PLATFORMS.some((p) => link.site.toLowerCase().includes(p.toLowerCase())),
    )
    .map(({ site, url }) => ({ name: site, url }));
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
