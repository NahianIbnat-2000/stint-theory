import { useEffect, useState } from "react";
export { fmt, signed } from "./format.js";

const BASE = `${import.meta.env.BASE_URL}data/`;
const cache = new Map();

export function load(path, kind = "json") {
  const key = `${kind}:${path}`;
  if (!cache.has(key)) {
    cache.set(key, fetch(BASE + path).then((r) => {
      if (!r.ok) throw new Error(`${path}: ${r.status}`);
      return kind === "json" ? r.json() : r.text();
    }));
  }
  return cache.get(key);
}

// { data, error } ; data stays undefined while loading
export function useData(path, kind = "json") {
  const [state, set] = useState({});
  useEffect(() => {
    let live = true;
    if (!path) return undefined;
    set({});
    load(path, kind).then((data) => live && set({ data }), (error) => live && set({ error }));
    return () => { live = false; };
  }, [path, kind]);
  return state;
}

export const COMPOUND = {
  SOFT: { color: "var(--soft)", short: "S", name: "Soft" },
  MEDIUM: { color: "var(--medium)", short: "M", name: "Medium" },
  HARD: { color: "var(--hard)", short: "H", name: "Hard" },
};
