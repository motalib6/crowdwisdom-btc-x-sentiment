"""Walk-forward training: one Ridge model per horizon h = 0..5.

Model (transparent baseline, no hidden state):
  Ridge regression (closed-form, numpy only) on standardised features,
  alpha = 1.0, predicting log-return to the horizon target, converted
  back to a price:  pred_close = prev_close * exp(pred_log_return).

Walk-forward protocol (strictly out-of-sample in time):
  - Initial training window: first 500 daily bars.
  - Then 5 expanding-window folds: each fold trains on ALL bars before
    the fold and tests on the next 180 bars (the last fold is shorter
    if the data ends). No future bar is ever in a training window.
  - Metrics are computed ONLY on out-of-sample fold predictions.

Baselines reported for every horizon:
  - Persistence: pred_close = prev_close (i.e. predict no change).
  - Mean-return: pred_log_return = training mean log-return.

Outputs: data/predictions_walkforward.csv (one row per test bar and
horizon, with fold id) and data/metrics.json.
"""
import argparse
import json

import numpy as np
import pandas as pd

from src.features import FEATURES, HORIZONS

INITIAL_TRAIN = 500
FOLD_SIZE = 180
ALPHA = 1.0


class Ridge:
    def __init__(self, alpha: float = ALPHA):
        self.alpha = alpha

    def fit(self, X: np.ndarray, y: np.ndarray):
        self.mu_ = X.mean(axis=0)
        self.sd_ = X.std(axis=0)
        self.sd_[self.sd_ == 0] = 1.0
        Xs = (X - self.mu_) / self.sd_
        Xb = np.column_stack([np.ones(len(Xs)), Xs])
        A = Xb.T @ Xb + self.alpha * np.eye(Xb.shape[1])
        A[0, 0] -= self.alpha  # do not penalise the intercept
        self.coef_ = np.linalg.solve(A, Xb.T @ y)
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        Xs = (X - self.mu_) / self.sd_
        Xb = np.column_stack([np.ones(len(Xs)), Xs])
        return Xb @ self.coef_


def rmse(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.sqrt(np.mean((a - b) ** 2)))


def mae(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.mean(np.abs(a - b)))


def run_walkforward(df: pd.DataFrame):
    X_all = df[FEATURES].to_numpy(dtype=float)
    preds = []
    for fold in range(5):
        test_start = INITIAL_TRAIN + fold * FOLD_SIZE
        test_end = min(test_start + FOLD_SIZE, len(df))
        if test_start >= len(df):
            break
        for h in HORIZONS:
            y_all = df[f"target_return_h{h}"].to_numpy(dtype=float)
            model = Ridge().fit(X_all[:test_start], y_all[:test_start])
            pred_ret = model.predict(X_all[test_start:test_end])
            chunk = df.iloc[test_start:test_end][["date", "prev_close", f"target_close_h{h}"]].copy()
            chunk["horizon"] = h
            chunk["fold"] = fold
            chunk["pred_close"] = chunk["prev_close"] * np.exp(pred_ret)
            chunk["pred_return"] = pred_ret
            chunk["actual_return"] = np.log(chunk[f"target_close_h{h}"]) - np.log(chunk["prev_close"])
            chunk["persist_close"] = chunk["prev_close"]
            preds.append(chunk[["date", "horizon", "fold", "prev_close",
                                f"target_close_h{h}", "pred_close", "pred_return",
                                "actual_return", "persist_close"]]
                         .rename(columns={f"target_close_h{h}": "actual_close"}))
    return pd.concat(preds, ignore_index=True)


def metrics_for(pred: pd.DataFrame) -> dict:
    out = {}
    for h in HORIZONS:
        sub = pred[pred["horizon"] == h]
        out[f"h{h}"] = {
            "n_test": int(len(sub)),
            "rmse_price": rmse(sub["actual_close"].to_numpy(), sub["pred_close"].to_numpy()),
            "mae_price": mae(sub["actual_close"].to_numpy(), sub["pred_close"].to_numpy()),
            "rmse_persistence_price": rmse(sub["actual_close"].to_numpy(), sub["persist_close"].to_numpy()),
            "mae_persistence_price": mae(sub["actual_close"].to_numpy(), sub["persist_close"].to_numpy()),
            "mean_actual_close": float(sub["actual_close"].mean()),
        }
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bars", default="data/joined_daily_bars.csv")
    ap.add_argument("--out-pred", default="data/predictions_walkforward.csv")
    ap.add_argument("--out-metrics", default="data/metrics.json")
    args = ap.parse_args()
    df = pd.read_csv(args.bars, parse_dates=["date"])
    pred = run_walkforward(df)
    pred.to_csv(args.out_pred, index=False)
    metrics = {
        "n_daily_bars": int(len(df)),
        "bars_start": str(df["date"].min().date()),
        "bars_end": str(df["date"].max().date()),
        "initial_train_bars": INITIAL_TRAIN,
        "fold_size": FOLD_SIZE,
        "model": "Ridge (numpy closed-form, alpha=1.0), one model per horizon, "
                 "features standardised on training window only",
        "per_horizon": metrics_for(pred),
    }
    with open(args.out_metrics, "w") as fh:
        json.dump(metrics, fh, indent=2)
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
