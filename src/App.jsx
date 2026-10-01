import { useRef, useState } from "react";
import SearchBar from "./components/SearchBar";
import WebtoonList from "./components/WebtoonList";
import { searchWebtoons } from "./api/search";
import "./App.scss";

function App() {
  const [query, setQuery] = useState("");
  const [mode, setMode] = useState("title"); // title | semantic
  const [webtoons, setWebtoons] = useState([]);
  const [status, setStatus] = useState("idle"); // idle | loading | done | error
  const controllerRef = useRef(null);

  const runSearch = async (text, searchMode) => {
    controllerRef.current?.abort(); // 이전 검색 취소
    const controller = new AbortController();
    controllerRef.current = controller;

    setQuery(text);
    setStatus("loading");
    try {
      const list = await searchWebtoons(text, searchMode, controller.signal);
      setWebtoons(list);
      setStatus("done");
    } catch (err) {
      if (err.name !== "AbortError") setStatus("error");
    }
  };

  // 검색 방식을 바꾸면 같은 검색어로 바로 다시 검색
  const onModeChange = (next) => {
    setMode(next);
    if (query) runSearch(query, next);
  };

  return (
    <main className={`App${status === "idle" ? " is-idle" : ""}`}>
      <h1 className="App-title">SEARCHTOON</h1>
      <SearchBar
        onSearch={(text) => runSearch(text, mode)}
        mode={mode}
        onModeChange={onModeChange}
      />
      <div className="App-result" aria-live="polite">
        {status === "loading" && <p className="App-message">검색 중...</p>}
        {status === "error" && (
          <p className="App-message">
            검색 서버에 연결하지 못했어요. 백엔드가 실행 중인지 확인해 주세요.
          </p>
        )}
        {status === "done" && webtoons.length === 0 && (
          <p className="App-message">
            "{query}"에 대한 결과가 없어요.
            {mode === "title" && " '설명' 검색으로 내용을 찾아보세요."}
          </p>
        )}
        {status === "done" && webtoons.length > 0 && (
          <>
            <p className="App-count">검색 결과 {webtoons.length}개</p>
            <WebtoonList webtoons={webtoons} />
          </>
        )}
      </div>
    </main>
  );
}

export default App;
