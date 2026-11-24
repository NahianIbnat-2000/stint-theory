import { PAPER_URL } from "./lib/paper.js";
import { HashRouter, NavLink, Route, Routes, useLocation } from "react-router-dom";
import { lazy, Suspense, useEffect } from "react";
import { ROUTES } from "./routes.js";
import Home from "./pages/Home.jsx";

// Home loads first; other pages are fetched when visited.
const PAGES = {
  "/": Home,
  "/faq": lazy(() => import("./pages/Faq.jsx")),
  "/simulator": lazy(() => import("./pages/Simulator.jsx")),
  "/case-study": lazy(() => import("./pages/CaseStudy.jsx")),
  "/reliability": lazy(() => import("./pages/Reliability.jsx")),
  "/races": lazy(() => import("./pages/Races.jsx")),
  "/models": lazy(() => import("./pages/Models.jsx")),
  "/next-lap": lazy(() => import("./pages/NextLap.jsx")),
  "/ten-laps": lazy(() => import("./pages/TenLaps.jsx")),
  "/tyres": lazy(() => import("./pages/Tyres.jsx")),
  "/data": lazy(() => import("./pages/Data.jsx")),
  "/methods": lazy(() => import("./pages/Methods.jsx")),
  "/limits": lazy(() => import("./pages/Limits.jsx")),
};

function Chrome() {
  const { pathname } = useLocation();
  useEffect(() => {
    window.scrollTo(0, 0);
    const r = ROUTES.find((x) => x.path === pathname);
    document.title = r && r.path !== "/" ? `${r.title} · STINT THEORY` : "STINT THEORY";
  }, [pathname]);
  return null;
}

function NotFound() {
  return <div className="page"><div className="page-head"><h1>Page not found</h1><p>That address is not part of this site. <NavLink to="/">Go to the home page</NavLink>.</p></div></div>;
}

export default function App() {
  return (
    <HashRouter>
      <Chrome />
      <a className="skip" href="#main">Skip to content</a>
      <div className="shell">
      <nav className="rail" aria-label="Main">
        <NavLink to="/" end className="brand">STINT THEORY<small>F1 strategy research, 2023–2025</small></NavLink>
        <ul>
          {ROUTES.filter((r) => r.nav).map((r) => (
            <li key={r.path}>
              <NavLink to={r.path}>{r.label}</NavLink>
            </li>
          ))}
        </ul>
        <div className="rail-foot">Data: OpenF1. Not affiliated with Formula 1, the FIA or Pirelli.<br /><a href={PAPER_URL}>Research report (PDF)</a><br /><a href="https://github.com/NahianIbnat-2000/stint-theory">Code and reports</a></div>
      </nav>
      <div>
      <main id="main">
        <Suspense fallback={<div className="page"><div className="skeleton" style={{ marginTop: "3rem" }} aria-label="Loading page" /></div>}>
          <Routes>
            {ROUTES.map((r) => { const C = PAGES[r.path]; return <Route key={r.path} path={r.path} element={<C />} />; })}
            <Route path="*" element={<NotFound />} />
          </Routes>
        </Suspense>
      </main>
      <footer>
        <div className="inner">
          <span>STINT THEORY, by Nahian Ibnat</span>
          <span>Data: OpenF1, 2023–2025</span>
          <span>Not affiliated with Formula 1, the FIA or Pirelli</span>
          <a href={PAPER_URL}>Research report (PDF)</a>
          <a href="https://github.com/NahianIbnat-2000/stint-theory">Code and reports on GitHub</a>
        </div>
      </footer>
      </div>
      </div>
    </HashRouter>
  );
}
