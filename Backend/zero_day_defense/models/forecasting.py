from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple

import numpy as np
from sklearn.linear_model import LinearRegression


@dataclass
class ForecastingModel:
    lr: LinearRegression
    resid_scale: float

    def score(self, t_idx: np.ndarray, y: np.ndarray) -> np.ndarray:
        pred = self.lr.predict(t_idx.reshape(-1, 1))
        resid = np.abs(y - pred)
        s = resid / max(self.resid_scale, 1e-9)
        # squash to [0,1)
        return 1.0 - np.exp(-s)


def train_forecasting(t_idx: np.ndarray, y: np.ndarray, cfg: Dict) -> ForecastingModel:
    lr = LinearRegression()
    lr.fit(t_idx.reshape(-1, 1), y)
    pred = lr.predict(t_idx.reshape(-1, 1))
    resid = np.abs(y - pred)
    # robust scale estimate
    scale = float(np.median(resid) + 1.4826 * np.median(np.abs(resid - np.median(resid))))
    if scale <= 0:
        scale = float(np.mean(resid) + 1e-6)
    return ForecastingModel(lr=lr, resid_scale=scale)

