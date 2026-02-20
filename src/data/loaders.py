"""
Data loaders for HEATWATCH+ Demo.
Loads data from JSON/CSV files in the data/ directory.
"""

import json
import os
import pandas as pd
from typing import Dict, Any

# Base data directory (relative to project root)
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")


def _data_path(*parts: str) -> str:
    """Construct path relative to data directory."""
    return os.path.join(DATA_DIR, *parts)


def load_kpis() -> Dict[str, Any]:
    """Load KPI data from JSON file."""
    path = _data_path("simulated", "baseline_kpis.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_env_timeseries() -> pd.DataFrame:
    """Load environmental timeseries CSV."""
    path = _data_path("simulated", "baseline_env_timeseries.csv")
    df = pd.read_csv(path, parse_dates=["date"])
    return df


def load_micro_signals() -> pd.DataFrame:
    """Load micro signals CSV."""
    path = _data_path("simulated", "baseline_micro_signals.csv")
    df = pd.read_csv(path, parse_dates=["date"])
    return df


def load_vulnerability() -> pd.DataFrame:
    """Load vulnerability CSV."""
    path = _data_path("simulated", "baseline_vulnerability.csv")
    df = pd.read_csv(path)
    return df


def load_geojson() -> Dict[str, Any]:
    """Load Ankara districts GeoJSON."""
    path = _data_path("geo", "ankara_districts.geojson")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
