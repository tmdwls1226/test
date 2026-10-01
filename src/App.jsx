import { useState } from "react";
import SearchBar from "./components/SearchBar";
import "./App.scss";

function App() {
  const [query, setQuery] = useState("");

  const onSearch = (text) => {
    setQuery(text);
    // TODO: 검색 결과 연동 (다음 단계)
  };

  return (
    <main className="App">
      <h1 className="App-title">SEARCHTOON</h1>
      <SearchBar onSearch={onSearch} />
      {query && <p className="App-query">"{query}" 검색 준비 중...</p>}
    </main>
  );
}

export default App;
