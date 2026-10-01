// 백엔드(FastAPI)의 '설명으로 검색' (줄거리 임베딩 기반)
export async function searchSemantic(query, signal) {
  const res = await fetch(`/api/search/semantic?q=${encodeURIComponent(query)}`, {
    signal,
  });
  if (!res.ok) throw new Error(`검색 서버 오류 (${res.status})`);
  return res.json();
}
