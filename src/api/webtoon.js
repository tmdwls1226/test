import { searchAniList } from "./anilist";

// 검색 소스 목록. 새 API(Kitsu 등)는 같은 형태의 함수를 여기에 추가하면 된다.
const SOURCES = [searchAniList];

export async function searchWebtoons(query, signal) {
  const results = await Promise.allSettled(
    SOURCES.map((search) => search(query, signal)),
  );
  const ok = results.filter((r) => r.status === "fulfilled");
  if (ok.length === 0) throw results[0].reason;
  return ok.flatMap((r) => r.value);
}
