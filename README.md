# Zero-Day Defense (Multi-Layered)

This project implements a **multi-layered zero-day detection** pipeline using the datasets already present in `dataset/`:

- **Perception layer (statistical detection)**: Isolation Forest over flow features (CIC-IDS and IoT botnet flows).
- **Forecasting layer**: linear-regression baseline + residual anomaly scoring over time-bucketed traffic metrics.
- **Deep sequence layer**: LSTM over **raw HTTP request strings** (CSIC), trained on *Normal* traffic and scored by reconstruction/next-token loss.
- **Reasoning + action layer**: an agent that fuses signals into a decision and can execute mitigations (default is dry-run).

## Setup

Create a virtual environment, then install dependencies:

```bash
pip install -r requirements.txt
```

## Run

Train and evaluate using your local datasets:

```bash
python -m zero_day_defense.cli run --dataset-root dataset --dry-run
```

Outputs (metrics + example decisions) are written to `artifacts/`.

## Dataset assumptions (auto-detected)

- **CIC-IDS**: CSVs under `dataset/CIC-IDS_Network_Intrusion/*.csv` with a `Label` column (BENIGN vs attacks).
- **CSIC**: `dataset/csic_database/csic_database.csv` with `classification` and `URL` columns.
- **IoT botnet**: `dataset/IoT_Botnet_Traffic_Dataset/file.csv` with an `attack` column (1 = attack).

If your local layout differs, edit `src/zero_day_defense/config.yaml`.
