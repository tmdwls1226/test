import { useState } from "react";
import { MdSearch } from "react-icons/md";
import "./SearchBar.scss";

function SearchBar({ onSearch }) {
  const [value, setValue] = useState("");

  const onSubmit = (e) => {
    e.preventDefault();
    const text = value.trim();
    if (text) onSearch(text);
  };

  return (
    <form className="SearchBar" onSubmit={onSubmit} role="search">
      <input
        type="search"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        placeholder="웹툰 제목을 검색하세요"
        aria-label="웹툰 검색"
      />
      <button type="submit" aria-label="검색">
        <MdSearch />
      </button>
    </form>
  );
}

export default SearchBar;
