// Display names for model ids used in the result files.
export const MODEL = {
  persistence: "Persistence (repeat the last lap)",
  compound_drift: "Compound drift",
  ridge: "Ridge regression",
  mixed_effects: "Mixed-effects model",
  random_forest: "Random forest",
  rf: "Random forest",
  xgboost: "XGBoost",
  xgb: "XGBoost",
  xgboost_ens5: "XGBoost (5 seeds averaged)",
  mlp: "MLP",
  lstm: "LSTM",
  tcn: "TCN",
};
export const name = (id) => MODEL[id] || id;
export const comparison = (s) => s.split(" vs ").map(name).join(" vs ");

// Rows of a pre-registered comparison table -> IntervalChart rows.
export function intervalRows(primary, diffKey) {
  return primary.map((r) => ({
    label: comparison(r.comparison), point: r[diffKey], lo95: r["95% low"], hi95: r["95% high"],
    lo90: r["90% low"], hi90: r["90% high"], verdict: r.label, holm: r["Holm p"],
  }));
}
