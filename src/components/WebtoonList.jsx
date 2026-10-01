import WebtoonCard from "./WebtoonCard";
import "./WebtoonList.scss";

function WebtoonList({ webtoons }) {
  return (
    <ul className="WebtoonList">
      {webtoons.map((w) => (
        <WebtoonCard key={w.id} webtoon={w} />
      ))}
    </ul>
  );
}

export default WebtoonList;
