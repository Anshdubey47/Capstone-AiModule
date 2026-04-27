from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from zero_day_defense.pipeline import run_pipeline, train_all
from zero_day_defense.settings import load_config

app = typer.Typer(add_completion=False)
console = Console()


@app.command()
def train(
    dataset_root: str = typer.Option("dataset", help="Path to dataset root folder."),
    config_path: Optional[str] = typer.Option(
        None, help="Path to config.yaml (defaults to package config.yaml)."
    ),
):
    """Train all ML components and write artifacts."""
    cfg = load_config(config_path=config_path, dataset_root=dataset_root)
    artifacts = train_all(cfg)
    console.print(f"[bold green]Training complete.[/bold green] Artifacts in {artifacts}")


@app.command()
def run(
    dataset_root: str = typer.Option("dataset", help="Path to dataset root folder."),
    config_path: Optional[str] = typer.Option(None, help="Path to config.yaml."),
    dry_run: bool = typer.Option(True, help="Do not execute mitigation commands."),
    max_events: int = typer.Option(50, help="Limit number of events to score."),
):
    """Train (if needed) then run detection + agentic reasoning."""
    cfg = load_config(config_path=config_path, dataset_root=dataset_root)
    result = run_pipeline(cfg, dry_run=dry_run, max_events=max_events)
    console.print("[bold]Agent decisions (sample)[/bold]")
    console.print_json(json.dumps(result["decisions"][:10], indent=2))
    console.print(f"[bold green]Done.[/bold green] Wrote {result['artifacts_dir']}")


if __name__ == "__main__":
    app()

