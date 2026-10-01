import "./WebtoonCard.scss";

// 썸네일이 없을 때 제목으로 고정된 색을 만든다
function placeholderColor(title) {
  let hash = 0;
  for (const ch of title) hash = (hash * 31 + ch.codePointAt(0)) % 360;
  return `hsl(${hash} 45% 62%)`;
}

function WebtoonCard({ webtoon }) {
  const { title, subtitle, thumbnail, platforms, infoUrl, description } = webtoon;

  const thumb = thumbnail ? (
    <img src={thumbnail} alt={`${title} 썸네일`} loading="lazy" />
  ) : (
    <div className="no-thumb" style={{ background: placeholderColor(title) }}>
      {title}
    </div>
  );

  return (
    <li className="WebtoonCard">
      {infoUrl ? (
        <a href={infoUrl} target="_blank" rel="noreferrer" className="thumb">
          {thumb}
        </a>
      ) : (
        <div className="thumb">{thumb}</div>
      )}
      <div className="info">
        <strong className="title">{title}</strong>
        {subtitle && subtitle !== title && (
          <span className="subtitle">{subtitle}</span>
        )}
        {description && <p className="desc">{description}</p>}
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
            <span className="platform none">플랫폼 정보 없음</span>
          )}
        </div>
      </div>
    </li>
  );
}

export default WebtoonCard;
