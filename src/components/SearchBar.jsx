import { useState } from "react";
import { MdSearch } from "react-icons/md";
import "./SearchBar.scss";

const MODES = [
  { value: "title", label: "제목", placeholder: "웹툰 제목을 검색하세요" },
  { value: "semantic", label: "설명", placeholder: "예: 회귀하는 먼치킨 판타지" },
];

function SearchBar({ onSearch, mode, onModeChange }) {
  const [value, setValue] = useState("");

  const onSubmit = (e) => {
    e.preventDefault();
    const text = value.trim();
    if (text) onSearch(text);
  };

  const current = MODES.find((m) => m.value === mode);

  return (
    <form className="SearchBar" onSubmit={onSubmit} role="search">
      <select
        value={mode}
        onChange={(e) => onModeChange(e.target.value)}
        aria-label="검색 방식"
      >
        {MODES.map((m) => (
          <option key={m.value} value={m.value}>
            {m.label}
          </option>
        ))}
      </select>
      <input
        type="search"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        placeholder={current.placeholder}
        aria-label="웹툰 검색"
      />
      <button type="submit" aria-label="검색">
        <MdSearch />
      </button>
    </form>
  );
}

export default SearchBar;
