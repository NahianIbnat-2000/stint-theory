import React from "react";
import { createRoot } from "react-dom/client";
import App from "./App.jsx";
// fonts are bundled with the site (latin subset), no third-party requests
import "@fontsource-variable/anybody/standard.css";
import "@fontsource-variable/anybody/standard-italic.css";
import "@fontsource/atkinson-hyperlegible/latin-400.css";
import "@fontsource/atkinson-hyperlegible/latin-700.css";
import "@fontsource/atkinson-hyperlegible/latin-400-italic.css";
import "@fontsource-variable/martian-mono/standard.css";
import "./styles.css";

createRoot(document.getElementById("root")).render(<App />);
