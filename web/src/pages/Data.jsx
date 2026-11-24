import Report from "../components/Report.jsx";

export default function Data() {
  return (
    <>
      <header className="page-head">
        <h1>Data</h1>
        <p className="lede">Lap timing, pit stops, tyres, flags and weather for the 2023–2025 seasons, from the free OpenF1
          API. Nothing is dropped: laps behind a safety car, pit laps and outliers are flagged and the models decide what
          to use. Lap times are not republished here; anyone can rebuild them with the project’s pipeline.</p>
      </header>
      <section><h2>Coverage and checks</h2><Report name="coverage" open /></section>
      <section><Report name="data_dictionary" title="Data dictionary" /></section>
    </>
  );
}
