from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class LabeledFrame:
    df: pd.DataFrame
    y: Optional[pd.Series] = None


def load_cic_ids(cfg: Dict) -> LabeledFrame:
    root = Path(cfg["dataset_root"])
    glob_pat = cfg["cic_ids"]["glob"]
    paths = sorted((root / glob_pat.split("/")[0]).glob(glob_pat.split("/", 1)[1]))
    if not paths:
        # fallback: use rglob for safety
        paths = sorted(root.rglob(glob_pat))
    if not paths:
        raise FileNotFoundError(f"No CIC-IDS CSVs matched {glob_pat!r} under {root}")

    frames: List[pd.DataFrame] = []
    for p in paths:
        frames.append(pd.read_csv(p, low_memory=False))
    df = pd.concat(frames, ignore_index=True)

    label_col = cfg["cic_ids"]["label_column"]
    benign = cfg["cic_ids"]["benign_label"]
    if label_col in df.columns:
        y = (df[label_col].astype(str) != str(benign)).astype(int)
    else:
        y = None
    drop_cols = set(cfg["cic_ids"].get("drop_columns") or [])
    drop_cols |= {label_col} if label_col in df.columns else set()

    X = df.drop(columns=[c for c in drop_cols if c in df.columns], errors="ignore")
    X = _to_numeric_frame(X)
    X = _clean_inf_nan(X)
    return LabeledFrame(df=X, y=y)


def load_iot_botnet(cfg: Dict) -> LabeledFrame:
    root = Path(cfg["dataset_root"])
    p = root / cfg["iot_botnet"]["path"]
    df = pd.read_csv(p, low_memory=False)
    label_col = cfg["iot_botnet"]["label_column"]
    normal_value = cfg["iot_botnet"]["normal_value"]
    y = None
    if label_col in df.columns:
        y = (df[label_col] != normal_value).astype(int)
    X = df.drop(columns=[c for c in [label_col, "category", "subcategory"] if c in df.columns], errors="ignore")
    X = _to_numeric_frame(X)
    X = _clean_inf_nan(X)
    return LabeledFrame(df=X, y=y)


def load_csic_http(cfg: Dict) -> pd.DataFrame:
    root = Path(cfg["dataset_root"])
    p = root / cfg["csic"]["path"]
    df = pd.read_csv(p, low_memory=False)
    # Keep only what we need (label + raw request string)
    label_col = cfg["csic"]["label_column"]
    text_col = cfg["csic"]["text_column"]

    if text_col not in df.columns:
        raise ValueError(f"CSIC CSV missing text column {text_col!r}")

    # CSIC exports sometimes include a leading unnamed column that actually holds the class label
    # (e.g. header starts with ',' and first field is 'Normal'), while a later 'classification'
    # column may be numeric (often 0/1). We auto-select the column that best matches normal_label.
    normal_label = str(cfg["csic"]["normal_label"])
    candidate_cols = [label_col] if label_col in df.columns else []
    candidate_cols += [c for c in df.columns if c not in candidate_cols]

    head = df.head(2000)
    best_col = None
    best_rate = -1.0
    for c in candidate_cols:
        s = head[c].astype(str)
        rate = float((s == normal_label).mean())
        if rate > best_rate:
            best_rate = rate
            best_col = c

    if best_col is None:
        raise ValueError("Could not determine CSIC label column.")

    return df[[best_col, text_col]].rename(columns={best_col: label_col}).copy()


def _to_numeric_frame(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for c in out.columns:
        if not pd.api.types.is_numeric_dtype(out[c]):
            out[c] = pd.to_numeric(out[c], errors="coerce")
    # Drop all-nan columns
    out = out.dropna(axis=1, how="all")
    return out


def _clean_inf_nan(df: pd.DataFrame) -> pd.DataFrame:
    out = df.replace([np.inf, -np.inf], np.nan)
    # Fill remaining NaNs with column median (robust enough for anomaly models)
    for c in out.columns:
        if out[c].isna().any():
            med = out[c].median()
            out[c] = out[c].fillna(med if pd.notna(med) else 0.0)
    return out.astype(np.float32)

