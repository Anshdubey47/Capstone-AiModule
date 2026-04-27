from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple

import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler


@dataclass
class PerceptionModel:
    scaler: StandardScaler
    model: IsolationForest

    def score(self, X: np.ndarray) -> np.ndarray:
        Xs = self.scaler.transform(X)
        # IsolationForest: higher score_samples => more normal.
        s = self.model.score_samples(Xs)
        # Convert to anomaly score in [0,1] via rank normalization.
        # (Stable across datasets without assuming distribution.)
        ranks = s.argsort().argsort().astype(np.float32)
        return 1.0 - (ranks / max(1, len(ranks) - 1))


def train_perception(X_train: np.ndarray, cfg: Dict) -> PerceptionModel:
    scaler = StandardScaler(with_mean=True, with_std=True)
    Xs = scaler.fit_transform(X_train)
    model = IsolationForest(
        n_estimators=int(cfg["perception"]["n_estimators"]),
        contamination=float(cfg["perception"]["contamination"]),
        random_state=int(cfg["perception"]["random_state"]),
        n_jobs=-1,
    )
    model.fit(Xs)
    return PerceptionModel(scaler=scaler, model=model)

