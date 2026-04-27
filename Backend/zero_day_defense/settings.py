from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

import yaml


def _deep_update(base: Dict[str, Any], upd: Dict[str, Any]) -> Dict[str, Any]:
    out = dict(base)
    for k, v in upd.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _deep_update(out[k], v)
        else:
            out[k] = v
    return out


def load_config(*, config_path: Optional[str] = None, dataset_root: str = "dataset") -> Dict[str, Any]:
    pkg_cfg_path = Path(__file__).with_name("config.yaml")
    with pkg_cfg_path.open("r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    if config_path:
        with Path(config_path).open("r", encoding="utf-8") as f:
            override = yaml.safe_load(f)
        cfg = _deep_update(cfg, override)

    cfg["dataset_root"] = dataset_root
    return cfg


def ensure_artifacts_dir(cfg: Dict[str, Any]) -> Path:
    out = Path(cfg.get("artifacts_dir", "artifacts"))
    out.mkdir(parents=True, exist_ok=True)
    return out

