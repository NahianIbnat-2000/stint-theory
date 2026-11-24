// Mulberry32 + Box-Muller, identical to simulation/rng.py (same draws, same order).
export class Mulberry32 {
  constructor(seed) { this.state = seed >>> 0; }
  nextU32() {
    this.state = (this.state + 0x6d2b79f5) >>> 0;
    let t = this.state;
    t = Math.imul(t ^ (t >>> 15), t | 1) >>> 0;
    t = (t ^ ((t + (Math.imul(t ^ (t >>> 7), t | 61) >>> 0)) >>> 0)) >>> 0;
    return (t ^ (t >>> 14)) >>> 0;
  }
  uniform() { return (this.nextU32() + 0.5) / 4294967296; }
  normal() {
    const u1 = this.uniform(), u2 = this.uniform();
    return Math.sqrt(-2 * Math.log(u1)) * Math.cos(2 * Math.PI * u2);
  }
  normals(n) { const a = new Array(n); for (let i = 0; i < n; i++) a[i] = this.normal(); return a; }
  uniforms(n) { const a = new Array(n); for (let i = 0; i < n; i++) a[i] = this.uniform(); return a; }
}
