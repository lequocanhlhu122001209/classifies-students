"""normalize_dataset.py

Usage:
    python scripts/normalize_dataset.py --csv student_classification_supabase_ready_final.csv

What it does:
- Reads the CSV file
- Detects numeric columns to normalize (excludes obvious ID/text columns)
- Produces two CSV files:
  - <original>_minmax.csv  (Min-Max scaled to [0,1])
  - <original>_zscore.csv  (Z-score standardized to mean=0, std=1)
- Prints a short summary of columns normalized and output file paths

Note: Requires pandas and scikit-learn installed in the environment.
"""
from __future__ import annotations
import argparse
import os
import sys
import json

import pandas as pd
from sklearn.preprocessing import MinMaxScaler, StandardScaler, RobustScaler

TEXT_COLUMNS = {
    "id",
    "student_id",
    "name",
    "class",
    "class_code",
    "department",
    "Khoa",
    "khoa",
    "sex",
    "level_prediction",
    "predicted_level",
    "risk_level",
}


def detect_numeric_columns(df: pd.DataFrame) -> list[str]:
    # pick numeric dtypes, but exclude likely identifier/text columns
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    # also consider JSON-string columns that may contain numbers — skip those
    filtered = [c for c in numeric_cols if c not in TEXT_COLUMNS]
    return filtered


def normalize_minmax(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    scaler = MinMaxScaler()
    df_out = df.copy()
    if cols:
        df_out[cols] = scaler.fit_transform(df[cols])
    return df_out


def normalize_zscore(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    scaler = StandardScaler()
    df_out = df.copy()
    if cols:
        df_out[cols] = scaler.fit_transform(df[cols])
    return df_out


def normalize_robust(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    """Robust scaling using median and IQR (less sensitive to outliers)."""
    scaler = RobustScaler()
    df_out = df.copy()
    if cols:
        df_out[cols] = scaler.fit_transform(df[cols])
    return df_out


def winsorize_df(df: pd.DataFrame, cols: list[str], lower_pct: float = 0.01, upper_pct: float = 0.99) -> pd.DataFrame:
    """Clip values outside [lower_pct, upper_pct] quantiles for each column.

    lower_pct and upper_pct are in (0,1) and represent quantiles (e.g. 0.01 and 0.99).
    """
    df_out = df.copy()
    for c in cols:
        try:
            low = float(df_out[c].quantile(lower_pct))
            high = float(df_out[c].quantile(upper_pct))
            df_out[c] = df_out[c].clip(lower=low, upper=high)
        except Exception:
            # if quantile fails (e.g., non-numeric col), skip
            continue
    return df_out


def main(csv_path: str, method: str = "all", winsorize_pct: float | None = None):
    if not os.path.exists(csv_path):
        print(f"CSV file not found: {csv_path}")
        sys.exit(2)

    print(f"Loading CSV: {csv_path}")
    df = pd.read_csv(csv_path)
    print(f"Rows: {len(df)}, columns: {len(df.columns)}")

    numeric_cols = detect_numeric_columns(df)
    if not numeric_cols:
        print("No numeric columns detected to normalize.")
        sys.exit(1)

    # If winsorization is requested, only apply it to non-binary numeric columns
    # (binary / indicator columns shouldn't be clipped or they'll become constant).
    if winsorize_pct is not None:
        # choose candidate cols for winsorization: numeric columns with >2 unique values
        candidate_winsorize_cols = [c for c in numeric_cols if df[c].nunique(dropna=False) > 2]
        if candidate_winsorize_cols:
            low_q = winsorize_pct
            high_q = 1.0 - winsorize_pct
            print(f"Applying winsorization to {len(candidate_winsorize_cols)} columns with lower={low_q}, upper={high_q}")
            df = winsorize_df(df, candidate_winsorize_cols, lower_pct=low_q, upper_pct=high_q)
        else:
            print("No numeric columns eligible for winsorization (all are binary/low-unique). Skipping winsorize.")

    # detect low-variance (near-constant) columns after any winsorization so metadata
    # reflects the actual values being normalized and we avoid producing constant columns
    var_stats = {}
    low_variance_cols = []
    EPS_STD = 1e-8
    for c in numeric_cols:
        try:
            series = df[c].dropna().astype(float)
            std = float(series.std(ddof=0)) if not series.empty else 0.0
            mean = float(series.mean()) if not series.empty else 0.0
        except Exception:
            mean = 0.0
            std = 0.0
        var_stats[c] = {"mean": mean, "std": std}
        if std <= EPS_STD:
            low_variance_cols.append(c)

    # filter out low-variance columns from normalization (leave them unchanged in outputs)
    numeric_cols_to_normalize = [c for c in numeric_cols if c not in low_variance_cols]

    if not numeric_cols_to_normalize:
        print("No numeric columns with variance found to normalize after excluding low-variance columns.")
    else:
        print(f"Numeric columns to normalize ({len(numeric_cols_to_normalize)}): {numeric_cols_to_normalize}")
    if low_variance_cols:
        print(f"Excluded low-variance columns ({len(low_variance_cols)}): {low_variance_cols}")

    base, ext = os.path.splitext(csv_path)

    # Note: winsorization was already handled above (only applied to eligible columns)

    methods = [m.strip().lower() for m in (method.split(",") if isinstance(method, str) else [method])]

    if "minmax" in methods or "all" in methods:
        # apply MinMax only to selected columns; keep excluded columns unchanged
        df_minmax = df.copy()
        if numeric_cols_to_normalize:
            df_minmax[numeric_cols_to_normalize] = MinMaxScaler().fit_transform(df[numeric_cols_to_normalize])
        out_minmax = f"{base}_minmax{ext}"
        df_minmax.to_csv(out_minmax, index=False)
        print(f"Wrote Min-Max scaled CSV: {out_minmax}")

    if "zscore" in methods or "all" in methods:
        df_z = df.copy()
        if numeric_cols_to_normalize:
            df_z[numeric_cols_to_normalize] = StandardScaler().fit_transform(df[numeric_cols_to_normalize])
        out_z = f"{base}_zscore{ext}"
        df_z.to_csv(out_z, index=False)
        print(f"Wrote Z-score normalized CSV: {out_z}")

    if "robust" in methods or "all" in methods:
        df_r = df.copy()
        if numeric_cols_to_normalize:
            df_r[numeric_cols_to_normalize] = RobustScaler().fit_transform(df[numeric_cols_to_normalize])
        out_r = f"{base}_robust{ext}"
        df_r.to_csv(out_r, index=False)
        print(f"Wrote Robust-scaled CSV: {out_r}")

    # Save metadata about columns and basic stats
    meta = {
        "source": csv_path,
        "rows": len(df),
        "all_numeric_columns": numeric_cols,
        "normalized_columns": numeric_cols_to_normalize,
        "excluded_low_variance": low_variance_cols,
        "variance_stats": var_stats,
        "method": method,
        "winsorize_pct": winsorize_pct,
    }
    meta_path = f"{base}_normalization_metadata.json"
    with open(meta_path, "w", encoding="utf-8") as fh:
        json.dump(meta, fh, ensure_ascii=False, indent=2)
    print(f"Wrote metadata: {meta_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", default="student_classification_supabase_ready_final.csv",
                        help="Path to CSV to normalize")
    parser.add_argument("--method", default="all",
                        help="Which method to run: minmax,zscore,robust or comma-separated list (default: all)")
    parser.add_argument("--winsorize-pct", type=float, default=None,
                        help="If set, winsorize extremes by this pct (e.g. 0.01 will clip below 1 percentile and above 99 percentile)")
    args = parser.parse_args()
    main(args.csv, method=args.method, winsorize_pct=args.winsorize_pct)
