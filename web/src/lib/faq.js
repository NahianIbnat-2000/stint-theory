// Filter FAQ items by group and a free-text query (case- and accent-insensitive).
const norm = (s) => s.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();

export function filterFaq(items, group = "all", query = "") {
  const words = norm(query).split(/\s+/).filter(Boolean);
  return items.filter((f) => {
    if (group !== "all" && f.group !== group) return false;
    if (!words.length) return true;
    const text = norm([f.q, ...f.a, f.fact || ""].join(" "));
    return words.every((w) => text.includes(w));
  });
}
