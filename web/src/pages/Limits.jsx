import Report from "../components/Report.jsx";

export default function Limits() {
  return (
    <div className="page">
      <header className="page-head">
        <h1>Limits and reproducing</h1>
        <p className="lede">What these results cannot tell you, and how to rerun everything from scratch.</p>
      </header>
      <section><Report name="limitations" open /></section>
      <section>
        <h2>Rerun it</h2>
        <pre><code>{`git clone https://github.com/NahianIbnat-2000/stint-theory
cd stint-theory
pip install -r requirements.txt
python -m pipelines all          # download from OpenF1 and build the lap tables
python -m models dev             # development runs (the test set stays locked)
python -m simulation build       # simulator parameters
python -m webexport              # data for this website`}</code></pre>
        <p>The code, the reports and the full history of changes are on{" "}
          <a href="https://github.com/NahianIbnat-2000/stint-theory">GitHub</a>.</p>
      </section>
      <section>
        <h2>About</h2>
        <p>Built by Nahian Ibnat (MA Economics, Data and Policy, Central European University) as an independent research
          project. Data from <a href="https://openf1.org">OpenF1</a>. Not affiliated with Formula 1, the FIA, Pirelli or any
          team. Formula 1 timing data belongs to Formula 1 and its partners.</p>
      </section>
    </div>
  );
}
