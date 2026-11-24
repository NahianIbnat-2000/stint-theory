import { HashRouter, NavLink, Route, Routes, useLocation } from "react-router-dom";
import { useEffect } from "react";
import Home from "./pages/Home.jsx";
import Data from "./pages/Data.jsx";
import NextLap from "./pages/NextLap.jsx";
import TenLaps from "./pages/TenLaps.jsx";
import Tyres from "./pages/Tyres.jsx";
import Simulator from "./pages/Simulator.jsx";
import Methods from "./pages/Methods.jsx";
import Limits from "./pages/Limits.jsx";

const PAGES = [
  ["/", "Home", Home], ["/data", "Data", Data], ["/next-lap", "Next lap", NextLap],
  ["/ten-laps", "Ten laps", TenLaps], ["/tyres", "Tyre wear", Tyres], ["/simulator", "Simulator", Simulator],
  ["/methods", "Methods", Methods], ["/limits", "Limits", Limits],
];

function ScrollTop() {
  const { pathname } = useLocation();
  useEffect(() => { window.scrollTo(0, 0); }, [pathname]);
  return null;
}

export default function App() {
  return (
    <HashRouter>
      <ScrollTop />
      <a className="skip" href="#main">Skip to content</a>
      <nav className="top" aria-label="Pages">
        <NavLink to="/" end className="brand">STINT THEORY</NavLink>
        <ul>{PAGES.slice(1).map(([to, label]) => <li key={to}><NavLink to={to}>{label}</NavLink></li>)}</ul>
      </nav>
      <main id="main">
        <Routes>{PAGES.map(([to, , C]) => <Route key={to} path={to} element={<C />} />)}</Routes>
      </main>
      <footer>
        Nahian Ibnat. Data: OpenF1, 2023–2025. Not affiliated with Formula 1, the FIA or Pirelli.{" "}
        <a href="https://github.com/NahianIbnat-2000/stint-theory">Code and reports</a>
      </footer>
    </HashRouter>
  );
}
