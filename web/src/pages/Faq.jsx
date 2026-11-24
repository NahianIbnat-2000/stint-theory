import { useEffect, useMemo, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { FAQ, GROUPS } from "../content/faq.js";
import { filterFaq } from "../lib/faq.js";
import { PAPER_URL } from "../lib/paper.js";

export default function Faq() {
  const [params, setParams] = useSearchParams();
  const linked = params.get("q");
  const [group, setGroup] = useState("all");
  const [query, setQuery] = useState("");
  const [open, setOpen] = useState(() => new Set(linked ? [linked] : []));
  const [copied, setCopied] = useState(null);

  const shown = useMemo(() => filterFaq(FAQ, group, query), [group, query]);

  // a shared link (?q=id) opens that question and scrolls to it
  useEffect(() => {
    if (!linked) return;
    setOpen((s) => new Set(s).add(linked));
    const el = document.getElementById(`faq-${linked}`);
    if (el) el.scrollIntoView({ block: "start" });
  }, [linked]);

  const toggle = (id, isOpen) => setOpen((s) => {
    const n = new Set(s);
    if (isOpen) n.add(id); else n.delete(id);
    return n;
  });
  const share = async (id) => {
    setParams({ q: id }, { replace: true });
    const url = `${window.location.origin}${window.location.pathname}#/faq?q=${id}`;
    try { await navigator.clipboard.writeText(url); setCopied(id); }
    catch { setCopied(null); }
  };
  const allOpen = shown.length > 0 && shown.every((f) => open.has(f.id));
  const setAll = () => setOpen(allOpen ? new Set() : new Set(shown.map((f) => f.id)));

  return (
    <div className="page faq">
      <header className="page-head">
        <h1>Questions, answered plainly</h1>
        <p className="lede">New to Formula 1, to machine learning, or to both? Start here. Every answer is written for
          someone who has never seen a race or trained a model, and links to the page where you can see it for yourself.</p>
      </header>

      <div className="faq-tools">
        <div className="segmented" role="group" aria-label="Show questions about">
          <button aria-pressed={group === "all"} onClick={() => setGroup("all")}>All</button>
          {GROUPS.map((g) => (
            <button key={g.id} aria-pressed={group === g.id} onClick={() => setGroup(g.id)}>{g.label}</button>
          ))}
        </div>
        <label className="faq-search">
          <span>Search</span>
          <input type="search" value={query} onChange={(e) => setQuery(e.target.value)} placeholder="tyres, safety car, LSTM…" />
        </label>
        <button className="btn btn-quiet" onClick={setAll} disabled={!shown.length}>{allOpen ? "Close all" : "Open all"}</button>
      </div>

      {!shown.length && (
        <p className="faq-empty">No question matches “{query}”. Try a shorter word, or <button className="link-button" onClick={() => { setQuery(""); setGroup("all"); }}>show every question</button>.</p>
      )}

      {GROUPS.map((g) => {
        const items = shown.filter((f) => f.group === g.id);
        if (!items.length) return null;
        return (
          <section key={g.id} className="faq-group" aria-labelledby={`faq-h-${g.id}`}>
            <h2 id={`faq-h-${g.id}`}>{g.label}</h2>
            {items.map((f) => (
              <details key={f.id} id={`faq-${f.id}`} className="faq-item" open={open.has(f.id)}
                onToggle={(e) => toggle(f.id, e.currentTarget.open)}>
                <summary>{f.q}</summary>
                <div className="faq-answer">
                  {f.a.map((p, i) => <p key={i}>{p}</p>)}
                  {f.fact && <p className="fact">{f.fact}</p>}
                  {(f.links?.length || f.report) && (
                    <p className="faq-links">
                      {f.links?.map((l, i) => <span key={l.to}>{i > 0 && " · "}<Link to={l.to}>{l.label}</Link></span>)}
                      {f.report && <span>{f.links?.length ? " · " : ""}<a href={PAPER_URL}>Research report (PDF)</a></span>}
                    </p>
                  )}
                  <p className="faq-share"><button className="link-button" onClick={() => share(f.id)}>Copy a link to this question</button>
                    <span role="status" aria-live="polite">{copied === f.id ? " Link copied" : ""}</span></p>
                </div>
              </details>
            ))}
          </section>
        );
      })}
    </div>
  );
}
