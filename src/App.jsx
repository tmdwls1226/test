import { useRef, useState } from "react";
import SearchBar from "./components/SearchBar";
import WebtoonList from "./components/WebtoonList";
import { searchWebtoons } from "./api/webtoon";
import { searchSemantic } from "./api/semantic";
import "./App.scss";

function App() {
  const [query, setQuery] = useState("");
  const [webtoons, setWebtoons] = useState([]);
  const [status, setStatus] = useState("idle"); // idle | loading | done | error
  const [mode, setMode] = useState("title"); // title | semantic
  const controllerRef = useRef(null);

  const onSearch = async (text) => {
    controllerRef.current?.abort(); // 이전 검색 취소
    const controller = new AbortController();
    controllerRef.current = controller;

    setQuery(text);
    setStatus("loading");
    try {
      const search = mode === "semantic" ? searchSemantic : searchWebtoons;
      const list = await search(text, controller.signal);
      setWebtoons(list);
      setStatus("done");
    } catch (err) {
      if (err.name !== "AbortError") setStatus("error");
    }
  };

  return (
    <main className={`App${status === "idle" ? " is-idle" : ""}`}>
      <h1 className="App-title">SEARCHTOON</h1>
      <SearchBar onSearch={onSearch} mode={mode} onModeChange={setMode} />
      {status === "loading" && <p className="App-message">검색 중...</p>}
      {status === "error" && (
        <p className="App-message">검색에 실패했어요. 잠시 후 다시 시도해 주세요.</p>
      )}
      {status === "done" && webtoons.length === 0 && (
        <p className="App-message">"{query}"에 대한 결과가 없어요.</p>
      )}
      {status === "done" && webtoons.length > 0 && (
        <WebtoonList webtoons={webtoons} />
      )}
    </main>
  );
}

export default App;
