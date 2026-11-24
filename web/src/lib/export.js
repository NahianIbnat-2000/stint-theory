// Downloads. Only derived numbers leave the page: no lap times.
export function toCSV(rows, columns) {
  const esc = (v) => {
    const s = v === null || v === undefined ? "" : String(v);
    return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
  };
  return [columns.map((c) => esc(c.label)).join(","),
    ...rows.map((r) => columns.map((c) => esc(typeof c.value === "function" ? c.value(r) : r[c.value])).join(","))].join("\n") + "\n";
}

export function download(name, text, type = "text/plain") {
  const url = URL.createObjectURL(new Blob([text], { type }));
  const a = Object.assign(document.createElement("a"), { href: url, download: name });
  document.body.appendChild(a); a.click(); a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

// Render an on-page SVG chart to PNG at 2x, with computed styles inlined.
export function svgToPng(svg, name) {
  const clone = svg.cloneNode(true);
  const src = svg.querySelectorAll("*"), dst = clone.querySelectorAll("*");
  const keep = ["fill", "stroke", "stroke-width", "stroke-dasharray", "opacity", "font-family", "font-size", "font-weight", "text-anchor"];
  src.forEach((el, i) => {
    const cs = getComputedStyle(el);
    dst[i].setAttribute("style", keep.map((k) => `${k}:${cs.getPropertyValue(k)}`).join(";"));
  });
  const { width, height } = svg.viewBox.baseVal;
  clone.setAttribute("width", width); clone.setAttribute("height", height);
  clone.setAttribute("xmlns", "http://www.w3.org/2000/svg");
  const img = new Image();
  img.onload = () => {
    const c = Object.assign(document.createElement("canvas"), { width: width * 2, height: height * 2 });
    const ctx = c.getContext("2d");
    ctx.fillStyle = "#ffffff"; ctx.fillRect(0, 0, c.width, c.height);
    ctx.scale(2, 2); ctx.drawImage(img, 0, 0);
    c.toBlob((b) => {
      const url = URL.createObjectURL(b);
      const a = Object.assign(document.createElement("a"), { href: url, download: name });
      document.body.appendChild(a); a.click(); a.remove();
      setTimeout(() => URL.revokeObjectURL(url), 1000);
    });
  };
  img.src = `data:image/svg+xml;charset=utf-8,${encodeURIComponent(new XMLSerializer().serializeToString(clone))}`;
}
