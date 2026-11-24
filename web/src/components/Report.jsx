import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { useData } from "../data.js";

export function Markdown({ text }) {
  return (
    <div className="prose">
      <ReactMarkdown remarkPlugins={[remarkGfm]}
        components={{ table: ({ node, ...p }) => <div className="table-wrap"><table {...p} /></div> }}>
        {text}
      </ReactMarkdown>
    </div>
  );
}

// A generated report or doc, rendered as it is in the repository.
export default function Report({ name, title, open = false }) {
  const { data, error } = useData(`reports/${name}.md`, "text");
  const body = error ? <Missing what={`${name}.md`} /> : data === undefined ? <p className="muted">Loading…</p> : <Markdown text={data} />;
  if (open) return body;
  return (
    <details className="report">
      <summary>{title || "Full report, as generated"}</summary>
      {body}
    </details>
  );
}

export function Missing({ what }) {
  return <p className="missing">Not published yet: {what} has not been exported from the project.</p>;
}
