"""Phase 3 neural models for next-lap time (CPU, PyTorch).

Three architectures, chosen so that each comparison isolates one thing:

  mlp   : the Phase 2 tabular inputs only. Tests "neural network vs boosted trees"
          on identical information.
  lstm  : tabular inputs + the driver's last K laps as a sequence (LSTM encoder).
  tcn   : tabular inputs + the same sequence (causal dilated convolutions).

mlp vs lstm/tcn is the temporal-history ablation: does reading the raw lap sequence
add anything beyond the hand-built summaries (last green lap, 3-lap mean, 5-lap
trend) that the tabular inputs already contain?

Target, scored laps, splits and tuning blocks are the Phase 2 ones. Loss is Huber
(delta 0.5 s), matching the pseudo-Huber loss XGBoost chose in Phase 2. Early
stopping uses the last races of each training fold, never the race predicted.
"""
from __future__ import annotations

import copy
import os

import numpy as np
import pandas as pd

from .zoo import _design, _preprocessor

SEQ_LEN = 10
SEED_BASE = 1000
_COMP = ["SOFT", "MEDIUM", "HARD"]


# --------------------------------------------------------------------- inputs
def build_sequences(df: pd.DataFrame, k: int = SEQ_LEN) -> np.ndarray:
    """For every row (origin = end of lap t), the driver's laps t-k+1..t of the
    same race, oldest first, front-padded. Uses only laps up to t.

    Channels per lap: lap time minus the origin's reference pace (scaled, clipped),
    lap-time-missing, real-time green, pit in, pit out, SC, VSC, yellow, restart,
    same stint as origin, tyre life / 30, compound one-hot (3), present.
    """
    ref = df["ref"].to_numpy(float)
    n_ch = 15
    out = np.zeros((len(df), k, n_ch), dtype=np.float32)
    order = df.sort_values(["race_id", "driver", "lap_number"]).index
    d = df.loc[order]
    pos = {ix: p for p, ix in enumerate(df.index)}
    for _, g in d.groupby(["race_id", "driver"], sort=False):
        lt = g["lt_lag0"].to_numpy(float)
        rows = np.column_stack([
            np.isnan(lt),
            g["is_rt_green"].astype(float),
            g["flag_pit_in"].astype(float), g["flag_pit_out"].astype(float),
            g["flag_sc"].astype(float), g["flag_vsc"].astype(float),
            g["flag_yellow"].astype(float), g["flag_post_neutralisation"].astype(float),
        ]).astype(np.float32)
        stint = g["stint"].to_numpy(float)
        tl = np.nan_to_num(g["tyre_life"].to_numpy(float) / 30.0)
        comp = np.column_stack([(g["compound_relative"] == c).to_numpy(float) for c in _COMP])
        idx = g.index.to_numpy()
        for j in range(len(g)):
            lo = max(0, j - k + 1)
            span = slice(lo, j + 1)
            p = pos[idx[j]]
            r0 = ref[p]
            dt = (lt[span] - r0) / 5.0
            seq = np.column_stack([
                np.clip(np.nan_to_num(dt), -3, 6), rows[span],
                (stint[span] == stint[j]).astype(float), tl[span], comp[span],
                np.ones(j + 1 - lo)])
            out[p, k - (j + 1 - lo):, :] = seq
    return out


class Tabular:
    """Phase 2 design matrix, imputed / scaled / one-hot, fitted on training rows."""

    def fit(self, df):
        self.prep = _preprocessor(scale=True).fit(_design(df))
        return self

    def transform(self, df):
        return self.prep.transform(_design(df)).astype(np.float32)


# --------------------------------------------------------------------- networks
def _nets():
    import torch
    from torch import nn

    class MLP(nn.Module):
        def __init__(self, d_tab, hidden=64, dropout=0.1, n_out=1, **_):
            super().__init__()
            self.n_out = n_out
            self.f = nn.Sequential(nn.Linear(d_tab, 2 * hidden), nn.ReLU(), nn.Dropout(dropout),
                                   nn.Linear(2 * hidden, hidden), nn.ReLU(), nn.Dropout(dropout),
                                   nn.Linear(hidden, n_out))

        def forward(self, tab, seq):
            out = self.f(tab)
            return out.squeeze(-1) if self.n_out == 1 else out

    class _SeqHead(nn.Module):
        def __init__(self, d_tab, d_seq_out, hidden, dropout, n_out=1):
            super().__init__()
            self.n_out = n_out
            self.tab = nn.Sequential(nn.Linear(d_tab, hidden), nn.ReLU(), nn.Dropout(dropout))
            self.head = nn.Sequential(nn.Linear(hidden + d_seq_out, hidden), nn.ReLU(),
                                      nn.Dropout(dropout), nn.Linear(hidden, n_out))

        def combine(self, tab, h):
            out = self.head(torch.cat([self.tab(tab), h], dim=-1))
            return out.squeeze(-1) if self.n_out == 1 else out

    class LSTMNet(_SeqHead):
        def __init__(self, d_tab, d_seq, hidden=64, dropout=0.1, n_out=1, **_):
            super().__init__(d_tab, hidden, hidden, dropout, n_out)
            self.rnn = nn.LSTM(d_seq, hidden, batch_first=True)

        def forward(self, tab, seq):
            _, (h, _) = self.rnn(seq)          # padding is at the front; last step = lap t
            return self.combine(tab, h[-1])

    class TCNNet(_SeqHead):
        def __init__(self, d_tab, d_seq, hidden=64, dropout=0.1, n_out=1, **_):
            super().__init__(d_tab, hidden, hidden, dropout, n_out)
            self.inp = nn.Conv1d(d_seq, hidden, 1)
            self.blocks = nn.ModuleList()
            for dil in (1, 2, 4):              # receptive field 1 + 2*(1+2+4) = 15 >= SEQ_LEN
                self.blocks.append(nn.Conv1d(hidden, hidden, 3, dilation=dil))
            self.dils = (1, 2, 4)
            self.drop = nn.Dropout(dropout)

        def forward(self, tab, seq):
            x = self.inp(seq.transpose(1, 2))
            for conv, dil in zip(self.blocks, self.dils):
                y = conv(nn.functional.pad(x, (2 * dil, 0)))   # left pad only: causal
                x = x + self.drop(torch.relu(y))
            return self.combine(tab, x[:, :, -1])

    return {"mlp": MLP, "lstm": LSTMNet, "tcn": TCNNet}


# --------------------------------------------------------------------- training
class NeuralModel:
    family = "deep_learning"

    def __init__(self, arch: str, hidden: int = 64, dropout: float = 0.1, lr: float = 1e-3,
                 weight_decay: float = 1e-4, max_epochs: int = 40, patience: int = 5,
                 batch_size: int = 256, val_races: int = 3, seed: int = 0):
        self.arch, self.hidden, self.dropout = arch, hidden, dropout
        self.lr, self.wd, self.max_epochs, self.patience = lr, weight_decay, max_epochs, patience
        self.bs, self.val_races, self.seed = batch_size, val_races, seed

    def _tensors(self, df, seq=None):
        import torch
        tab = torch.from_numpy(self.tab.transform(df))
        s = torch.from_numpy(seq if seq is not None else build_sequences(df))
        return tab, s

    def fit(self, df, seq: np.ndarray | None = None):
        import torch
        torch.manual_seed(SEED_BASE + self.seed)
        np.random.seed(SEED_BASE + self.seed)
        torch.set_num_threads(max(1, os.cpu_count() or 1))
        seq = build_sequences(df) if seq is None else seq
        y = (df["y_next_lap_time_s"] - df["ref"]).to_numpy(np.float32)
        # early-stopping races: the last `val_races` races of this training fold
        orders = np.sort(df["race_order"].unique())
        cut = orders[-self.val_races] if len(orders) > self.val_races else orders[-1] + 1
        is_val = (df["race_order"] >= cut).to_numpy()
        fit_df = df[~is_val]
        self.tab = Tabular().fit(fit_df)
        tab_all = torch.from_numpy(self.tab.transform(df))
        seq_all = torch.from_numpy(seq)
        y_all = torch.from_numpy(y)
        tr = torch.from_numpy(np.where(~is_val)[0])
        va = torch.from_numpy(np.where(is_val)[0])
        Net = _nets()[self.arch]
        self.net = Net(d_tab=tab_all.shape[1], d_seq=seq.shape[2], hidden=self.hidden,
                       dropout=self.dropout)
        opt = torch.optim.AdamW(self.net.parameters(), lr=self.lr, weight_decay=self.wd)
        loss_fn = torch.nn.HuberLoss(delta=0.5)
        g = torch.Generator().manual_seed(SEED_BASE + self.seed)
        best, best_state, bad = np.inf, None, 0
        self.history = []
        for epoch in range(self.max_epochs):
            self.net.train()
            perm = tr[torch.randperm(len(tr), generator=g)]
            for i in range(0, len(perm), self.bs):
                b = perm[i:i + self.bs]
                opt.zero_grad()
                loss = loss_fn(self.net(tab_all[b], seq_all[b]), y_all[b])
                loss.backward()
                opt.step()
            if len(va) == 0:
                best_state = copy.deepcopy(self.net.state_dict())
                continue
            self.net.eval()
            with torch.no_grad():
                v = torch.mean(torch.abs(self.net(tab_all[va], seq_all[va]) - y_all[va])).item()
            self.history.append(v)
            if v < best - 1e-4:
                best, best_state, bad = v, copy.deepcopy(self.net.state_dict()), 0
            else:
                bad += 1
                if bad >= self.patience:
                    break
        self.net.load_state_dict(best_state)
        self.epochs_run = len(self.history)
        return self

    def predict(self, df, seq: np.ndarray | None = None):
        import torch
        self.net.eval()
        tab, s = self._tensors(df, seq)
        with torch.no_grad():
            out = self.net(tab, s).numpy()
        return df["ref"].to_numpy(float) + out.astype(float)


ARCHS = ["mlp", "lstm", "tcn"]
GRID = [{"hidden": h, "dropout": d} for h in (32, 64) for d in (0.1, 0.3)]
