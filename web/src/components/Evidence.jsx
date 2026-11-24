import { Link } from "react-router-dom";

// "Where does this number come from?" Every field must be filled from an artifact or
// a document; nothing is filled in by hand on the page.
export default function Evidence({ title = "Evidence for this figure", items, doc }) {
  return (
    <details className="evidence">
      <summary>{title}</summary>
      <dl>
        {items.filter(([, v]) => v !== undefined && v !== null && v !== "").map(([k, v]) => (
          <div key={k}><dt>{k}</dt><dd>{v}</dd></div>
        ))}
      </dl>
      {doc && <p className="note">Method: <Link to={`/methods?doc=${doc[0]}`}>{doc[1]}</Link></p>}
    </details>
  );
}

export const shortHash = (h) => (h ? h.slice(0, 8) : null);
export const day = (t) => (t ? t.slice(0, 10) : null);
