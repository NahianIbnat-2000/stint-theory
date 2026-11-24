import { useState } from "react";
import { useSearchParams } from "react-router-dom";
import Report from "../components/Report.jsx";

const DOCS = [
  ["methodology", "Overview and validation"],
  ["methodology_models", "Models"],
  ["preregistration", "Pre-registration, Task 1"],
  ["preregistration_task2", "Pre-registration, Task 2"],
  ["methodology_tyre", "Tyre wear model"],
  ["methodology_simulator", "Strategy simulator"],
  ["sim_backtest", "Simulator backtest"],
  ["model_changes", "Every change and run, in order"],
  ["phase2_dev", "Development results: statistical and ML models"],
  ["phase3_dev", "Development results: deep learning"],
  ["task2_dev", "Development results: ten laps"],
];

export default function Methods() {
  const [params, setParams] = useSearchParams();
  const want = params.get("doc");
  const [doc, setDocState] = useState(DOCS.some(([id]) => id === want) ? want : DOCS[0][0]);
  const setDoc = (id) => { setDocState(id); setParams({ doc: id }, { replace: true }); };
  return (
    <div className="page">
      <header className="page-head">
        <h1>Methods</h1>
        <p className="lede">How the tests were set up so that the results can be trusted: train on 2023–2024, develop on
          the first half of 2025, test once on the second half. The test races were locked in code, every opening was
          logged, and each change to a model is recorded with the run that prompted it.</p>
      </header>
      <section className="docs">
        <nav className="doc-list" aria-label="Documents">
          {DOCS.map(([id, label]) => (
            <button key={id} className={doc === id ? "on" : ""} aria-pressed={doc === id} onClick={() => setDoc(id)}>{label}</button>
          ))}
        </nav>
        <div className="doc-body"><Report key={doc} name={doc} open /></div>
      </section>
    </div>
  );
}
