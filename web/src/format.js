export const fmt = (x, d = 3) => (x === null || x === undefined || Number.isNaN(x) ? "–" : Number(x).toFixed(d));
export const signed = (x, d = 3) => (x > 0 ? "+" : "") + fmt(x, d);
