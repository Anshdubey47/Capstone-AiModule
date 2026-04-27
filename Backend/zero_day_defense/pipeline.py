from __future__ import annotations

import json
import pickle
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd
import torch

from zero_day_defense.agent.lang_agent import build_langchain_agent, decide_with_langchain
from zero_day_defense.data.loaders import load_csic_http, load_iot_botnet
from zero_day_defense.models.forecasting import train_forecasting
from zero_day_defense.models.lstm_char import train_lstm_char
from zero_day_defense.models.perception import train_perception
from zero_day_defense.settings import ensure_artifacts_dir


def _save_pickle(obj: Any, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as f:
        pickle.dump(obj, f)


def _load_pickle(path: Path) -> Any:
    with path.open("rb") as f:
        return pickle.load(f)


def _load_cic_ids_sample(cfg: Dict[str, Any], *, row_limit: int) -> Tuple[pd.DataFrame, pd.Series | None]:
    """Fast loader for CIC-IDS: reads up to row_limit across CSVs."""
    root = Path(cfg["dataset_root"])
    glob_pat = cfg["cic_ids"]["glob"]
    label_col = cfg["cic_ids"]["label_column"]
    benign = str(cfg["cic_ids"]["benign_label"])

    # Resolve files
    folder = glob_pat.split("/")[0]
    inner = glob_pat.split("/", 1)[1]
    paths = sorted((root / folder).glob(inner))
    if not paths:
        paths = sorted(root.rglob(glob_pat))
    if not paths:
        raise FileNotFoundError(f"No CIC-IDS CSVs matched {glob_pat!r} under {root}")

    frames: List[pd.DataFrame] = []
    remaining = int(row_limit)
    for p in paths:
        if remaining <= 0:
            break
        chunk = pd.read_csv(p, low_memory=False, nrows=remaining)
        frames.append(chunk)
        remaining -= len(chunk)
    df = pd.concat(frames, ignore_index=True)
    y = None
    if label_col in df.columns:
        y = (df[label_col].astype(str) != benign).astype(int)
        df = df.drop(columns=[label_col], errors="ignore")
    return df, y


def train_all(cfg: Dict[str, Any]) -> Path:
    artifacts = ensure_artifacts_dir(cfg)

    # Perception model must match the feature schema we score at runtime.
    # For this prototype we score IoT flow records, so we train on IoT normals only.
    iot = load_iot_botnet(cfg)
    if iot.y is not None and (iot.y == 0).any():
        X_train = iot.df.loc[iot.y == 0].sample(n=min(200_000, int((iot.y == 0).sum())), random_state=0).to_numpy()
    else:
        X_train = iot.df.sample(n=min(200_000, len(iot.df)), random_state=0).to_numpy()

    perception = train_perception(X_train, cfg)
    _save_pickle(perception, artifacts / "perception.pkl")

    # Forecasting baseline: build a synthetic time index from row order (no timestamps in provided CSVs)
    # This is a baseline residual detector: significant trend shifts become anomalies.
    t_idx = np.arange(len(iot.df), dtype=np.float32)
    y = np.ones_like(t_idx)  # "flow_count" proxy per record
    forecasting = train_forecasting(t_idx, y, cfg)
    _save_pickle(forecasting, artifacts / "forecasting.pkl")

    # LSTM char model on CSIC "Normal"
    csic = load_csic_http(cfg)
    label_col = cfg["csic"]["label_column"]
    normal = cfg["csic"]["normal_label"]
    text_col = cfg["csic"]["text_column"]
    train_texts = csic.loc[csic[label_col] == normal, text_col].astype(str).tolist()
    train_limit = int(cfg["lstm"]["train_limit"])
    train_texts = train_texts[:train_limit]
    device = "cuda" if torch.cuda.is_available() else "cpu"
    lstm = train_lstm_char(train_texts, cfg, device=device)
    # Save weights separately (torch) and vocab/config (pickle)
    torch.save(lstm.net.state_dict(), artifacts / "lstm_char.pt")
    _save_pickle({"stoi": lstm.stoi, "itos": lstm.itos, "max_len": lstm.max_len}, artifacts / "lstm_char_meta.pkl")

    return artifacts


def _load_models(cfg: Dict[str, Any]) -> Dict[str, Any]:
    artifacts = ensure_artifacts_dir(cfg)
    required = [artifacts / "perception.pkl", artifacts / "forecasting.pkl", artifacts / "lstm_char.pt", artifacts / "lstm_char_meta.pkl"]
    if not all(p.exists() for p in required):
        train_all(cfg)
    perception = _load_pickle(artifacts / "perception.pkl")
    forecasting = _load_pickle(artifacts / "forecasting.pkl")
    meta = _load_pickle(artifacts / "lstm_char_meta.pkl")

    from zero_day_defense.models.lstm_char import CharLSTM, LSTMCharModel

    device = "cuda" if torch.cuda.is_available() else "cpu"
    net = CharLSTM(vocab_size=len(meta["itos"]), embedding_dim=int(cfg["lstm"]["embedding_dim"]), hidden_dim=int(cfg["lstm"]["hidden_dim"]))
    net.load_state_dict(torch.load(artifacts / "lstm_char.pt", map_location=device))
    net.to(device)
    lstm = LSTMCharModel(stoi=meta["stoi"], itos=meta["itos"], net=net, max_len=int(meta["max_len"]))
    return {"perception": perception, "forecasting": forecasting, "lstm": lstm, "device": device, "artifacts": artifacts}


def run_pipeline(cfg: Dict[str, Any], *, dry_run: bool, max_events: int) -> Dict[str, Any]:
    models = _load_models(cfg)
    artifacts: Path = models["artifacts"]

    iot = load_iot_botnet(cfg)
    csic = load_csic_http(cfg)

    # Build a scored event table from IoT botnet (has IPs/ports)
    base = pd.read_csv(Path(cfg["dataset_root"]) / cfg["iot_botnet"]["path"], low_memory=False)
    base = base.head(max_events).copy()
    X = iot.df.head(len(base)).to_numpy()

    perception_scores = models["perception"].score(X)
    t_idx = np.arange(len(base), dtype=np.float32)
    y = np.ones_like(t_idx)
    forecasting_scores = models["forecasting"].score(t_idx, y)

    # LSTM score on corresponding CSIC rows (textual requests)
    text_col = cfg["csic"]["text_column"]
    eval_texts = csic[text_col].astype(str).head(max_events).tolist()
    lstm_scores = models["lstm"].score(eval_texts, device=models["device"])

    chain = build_langchain_agent(
        decision_threshold=float(cfg["agent"]["decision_threshold"]),
        weights=dict(cfg["agent"]["weights"]),
    )
    decisions: List[Dict[str, Any]] = []
    for i in range(min(max_events, len(base))):
        src_ip = str(base.get("saddr", "unknown").iloc[i]) if "saddr" in base.columns else "unknown"
        dst_ip = str(base.get("daddr", "unknown").iloc[i]) if "daddr" in base.columns else "unknown"
        dst_port = str(base.get("dport", "unknown").iloc[i]) if "dport" in base.columns else "unknown"
        ctx = f"IoT flow row={i}; proto={base.get('proto','').iloc[i] if 'proto' in base.columns else ''}; attack_label={base.get('attack','').iloc[i] if 'attack' in base.columns else ''}"
        dec = decide_with_langchain(
            chain=chain,
            context=ctx,
            perception=float(perception_scores[i]),
            forecasting=float(forecasting_scores[i]),
            lstm=float(lstm_scores[i]) if i < len(lstm_scores) else 0.0,
            src_ip=src_ip,
            dst_ip=dst_ip,
            dst_port=dst_port,
        )
        actions = _execute_actions(dec.recommended_actions, cfg, dry_run=dry_run)
        decisions.append(
            {
                "event_index": i,
                "src_ip": src_ip,
                "dst_ip": dst_ip,
                "dst_port": dst_port,
                "scores": {"perception": float(perception_scores[i]), "forecasting": float(forecasting_scores[i]), "lstm": float(lstm_scores[i]) if i < len(lstm_scores) else 0.0},
                "threat": dec.threat,
                "confidence": dec.confidence,
                "rationale": dec.rationale,
                "actions_executed": actions,
            }
        )

    out_path = artifacts / "run_output.json"
    out_path.write_text(json.dumps({"decisions": decisions}, indent=2), encoding="utf-8")
    return {"decisions": decisions, "artifacts_dir": str(artifacts)}


def _execute_actions(recommended: List[Dict[str, Any]], cfg: Dict[str, Any], *, dry_run: bool) -> List[Dict[str, Any]]:
    executed: List[Dict[str, Any]] = []
    fw_cfg = (cfg.get("actions") or {}).get("firewall") or {}
    enabled = bool(fw_cfg.get("enabled", False))
    template = str(fw_cfg.get("command_template", ""))

    for act in recommended:
        act = dict(act)
        act_type = act.get("type")
        if act_type == "firewall_block" and template:
            ip = str(act.get("ip", "")).strip()
            if ip and ip != "{ip}":
                cmd = template.format(ip=ip)
            else:
                cmd = template.format(ip="0.0.0.0")  # placeholder for demo
            act["command"] = cmd
            act["executed"] = False
            if enabled and not dry_run:
                # Deliberately not executing arbitrary commands here.
                # If you want real execution, we can wire this into a controlled allow-list.
                act["executed"] = False
                act["note"] = "Execution disabled by design (safety)."
            else:
                act["note"] = "Dry-run (no changes made)."
            executed.append(act)
        else:
            act["note"] = "Unsupported action type (ignored)."
            executed.append(act)
    return executed

