// Display names and descriptions of every model, taken from docs/methodology_models.md.
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
  xgboost_direct: "XGBoost",
  trend_extrapolation: "Trend extrapolation",
  xgb_direct: "XGBoost",
  lstm_multi: "LSTM",
  mlp_multi: "MLP",
  tcn_multi: "TCN",
  persistence_multi: "Persistence (repeat the last lap)",
};
export const name = (id) => MODEL[id] || id;
export const comparison = (s) => s.split(" vs ").map(name).join(" vs ");

const TABULAR = "Tyre age and its square, fuel proxy (laps remaining), weather, recent pace (last green lap, 3-lap mean, 5-lap spread and trend), field pace, compound, circuit, team";
export const FAMILY_ORDER = ["Benchmark", "Statistical", "Tree ensemble", "Neural network"];
export const INFO = {
  persistence: { family: "Benchmark", objective: "None: predicts the reference pace (last clean lap in the stint)", inputs: "Reference pace only",
    strengths: "Impossible to overfit; sets the bar every model must clear.", limits: "Ignores tyre ageing, fuel burn and track evolution." },
  compound_drift: { family: "Benchmark", objective: "Reference pace plus the average lap-to-lap change for the compound in training", inputs: "Reference pace, compound",
    strengths: "Adds the typical drift with almost no parameters.", limits: "One drift per compound for every circuit and driver." },
  ridge: { family: "Statistical", objective: "Squared error with an L2 penalty (alpha tuned on 2024 blocks)", inputs: TABULAR,
    strengths: "Transparent and fast; coefficients can be read.", limits: "Linear in its inputs; interactions must be built by hand." },
  mixed_effects: { family: "Statistical", objective: "Linear mixed model (REML), random intercept and tyre-age slope by driver", inputs: `${TABULAR}; driver identity as a random effect`,
    strengths: "Lets each driver have their own tyre-age slope, shrunk toward the average.", limits: "Linear; driver slopes are noisy with few laps; on the test races it did worse than persistence." },
  random_forest: { family: "Tree ensemble", objective: "Squared error, 200 trees, half-sample bagging (leaf size and feature share tuned)", inputs: TABULAR,
    strengths: "Captures interactions without hand-built terms.", limits: "Averages leaves, so extreme laps are pulled to the middle." },
  xgboost: { family: "Tree ensemble", objective: "Pseudo-Huber loss, gradient-boosted trees (depth, trees, min child weight tuned)", inputs: TABULAR,
    strengths: "Strong on tabular data, robust to slow outlier laps.", limits: "A single fit varies a little with the random seed." },
  xgboost_ens5: { family: "Tree ensemble", objective: "As XGBoost, averaged over 5 seeds (the fair control for the 5-seed neural ensembles)", inputs: TABULAR,
    strengths: "Removes seed noise; the main comparator in the pre-registered tests.", limits: "Five times the training cost of one XGBoost fit." },
  mlp: { family: "Neural network", objective: "Huber loss (delta 0.5 s), 2 hidden layers, AdamW, early stopping; 5 seeds averaged", inputs: `${TABULAR} (exactly what XGBoost sees)`,
    strengths: "Isolates the learner: same inputs as XGBoost.", limits: "Needs scaling, tuning and seeds for the same accuracy as boosted trees." },
  lstm: { family: "Neural network", objective: "Huber loss; LSTM over the driver's last 10 laps joined with a tabular encoder; 5 seeds", inputs: `${TABULAR} + the raw sequence of the last 10 laps`,
    strengths: "Can learn from the raw lap sequence rather than hand-built summaries.", limits: "The sequence added nothing measurable beyond the summaries on these data." },
  tcn: { family: "Neural network", objective: "Huber loss; 3 causal dilated convolution blocks over the last 10 laps; 5 seeds", inputs: `${TABULAR} + the raw sequence of the last 10 laps`,
    strengths: "Sees the sequence with a fixed, causal receptive field.", limits: "Worse than XGBoost on very old tyres (secondary analysis S1); about twice the LSTM's training cost." },
};
export const familyOf = (id) => INFO[id]?.family || "Other";

// Rows of a pre-registered comparison table -> IntervalChart rows.
export function intervalRows(primary, diffKey) {
  return primary.map((r) => ({
    label: comparison(r.comparison), point: r[diffKey], lo95: r["95% low"], hi95: r["95% high"],
    lo90: r["90% low"], hi90: r["90% high"], verdict: r.label, holm: r["Holm p"],
  }));
}
