from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from langchain_core.runnables import RunnableLambda
from langchain_core.output_parsers import StrOutputParser


@dataclass
class AgentDecision:
    threat: bool
    confidence: float
    rationale: str
    recommended_actions: List[Dict[str, Any]]


def build_langchain_agent(*, decision_threshold: float = 0.75, weights: Optional[Dict[str, float]] = None):
    """
    Offline-safe LangChain "agent":
    - Uses a RunnableLambda to produce a JSON decision deterministically from scores
    """
    w = {"perception": 0.45, "forecasting": 0.15, "lstm": 0.40}
    if weights:
        w.update({k: float(v) for k, v in weights.items()})

    def decide(inputs: Dict[str, Any]) -> str:
        p = float(inputs.get("perception", 0.0))
        f = float(inputs.get("forecasting", 0.0))
        l = float(inputs.get("lstm", 0.0))
        fused = w["perception"] * p + w["forecasting"] * f + w["lstm"] * l
        threat = fused >= float(decision_threshold)
        rationale = (
            f"fused={fused:.3f} using weights {w}; "
            f"perception={p:.3f}, forecasting={f:.3f}, lstm={l:.3f}; "
            f"threshold={float(decision_threshold):.2f}"
        )
        actions = []
        if threat:
            actions.append({"type": "firewall_block", "ip": inputs.get("src_ip", "unknown"), "mode": "dry_run"})
        return json.dumps(
            {"threat": threat, "confidence": float(max(0.0, min(1.0, fused))), "rationale": rationale, "recommended_actions": actions}
        )

    # Keep the runnable input as the evidence dict.
    return RunnableLambda(decide) | StrOutputParser()


def decide_with_langchain(
    *,
    chain,
    context: str,
    perception: float,
    forecasting: float,
    lstm: float,
    src_ip: str = "unknown",
    dst_ip: str = "unknown",
    dst_port: str = "unknown",
) -> AgentDecision:
    raw = chain.invoke(
        {
            "context": context,
            "perception": float(perception),
            "forecasting": float(forecasting),
            "lstm": float(lstm),
            "src_ip": src_ip,
            "dst_ip": dst_ip,
            "dst_port": dst_port,
        }
    )
    try:
        obj = json.loads(raw)
        return AgentDecision(
            threat=bool(obj.get("threat", False)),
            confidence=float(obj.get("confidence", 0.0)),
            rationale=str(obj.get("rationale", "")),
            recommended_actions=list(obj.get("recommended_actions", [])),
        )
    except Exception:
        # Safe fallback if the LLM returns malformed output
        fused = 0.45 * perception + 0.15 * forecasting + 0.40 * lstm
        return AgentDecision(
            threat=bool(fused >= 0.75),
            confidence=float(min(1.0, max(0.0, fused))),
            rationale=f"Fallback heuristic used due to malformed JSON. fused={fused:.3f}",
            recommended_actions=[],
        )

