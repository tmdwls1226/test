import "./WebtoonCard.scss";

function WebtoonCard({ webtoon }) {
  const { title, subtitle, thumbnail, platforms, infoUrl, source } = webtoon;

  return (
    <li className="WebtoonCard">
      <a href={infoUrl} target="_blank" rel="noreferrer" className="thumb">
        {thumbnail ? (
          <img src={thumbnail} alt={`${title} 썸네일`} loading="lazy" />
        ) : (
          <div className="no-thumb">NO IMAGE</div>
        )}
      </a>
      <div className="info">
        <strong className="title">{title}</strong>
        {subtitle && subtitle !== title && (
          <span className="subtitle">{subtitle}</span>
        )}
        <div className="platforms">
          {platforms.length > 0 ? (
            platforms.map((p) => (
              <a
                key={p.url}
                href={p.url}
                target="_blank"
                rel="noreferrer"
                className="platform"
              >
                {p.name}
              </a>
            ))
          ) : (
            <span className="platform none">플랫폼 정보 없음 · {source}</span>
          )}
        </div>
      </div>
    </li>
  );
}

export default WebtoonCard;
