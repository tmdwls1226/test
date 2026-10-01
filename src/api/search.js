// 모든 검색은 백엔드(FastAPI)를 통한다. mode: "title" | "semantic"
export async function searchWebtoons(query, mode, signal) {
  const res = await fetch(`/api/search/${mode}?q=${encodeURIComponent(query)}`, {
    signal,
  });
  if (!res.ok) throw new Error(`검색 서버 오류 (${res.status})`);
  return res.json();
}
