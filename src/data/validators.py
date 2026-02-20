"""
Data validators for HEATWATCH+ Demo.
Validates loaded data against schemas.
"""

import pandas as pd
from typing import Dict, Any, List

from src.data.schema import (
    ENV_TIMESERIES_COLUMNS,
    MICRO_SIGNALS_COLUMNS,
    VULNERABILITY_COLUMNS,
    VALID_ALERT_LEVELS,
    VALID_RISK_LEVELS,
)


def validate_kpi_json(data: Dict[str, Any]) -> List[str]:
    """Validate KPI JSON structure. Returns list of error messages (empty = valid)."""
    errors = []

    # Top-level keys
    required_top = ["location", "period", "data_mode", "last_update", "kpis", "drivers"]
    for key in required_top:
        if key not in data:
            errors.append(f"Missing top-level key: '{key}'")

    if "location" in data:
        for k in ["country", "city", "district"]:
            if k not in data["location"]:
                errors.append(f"Missing location.{k}")

    if "period" in data:
        for k in ["start", "end", "forecast_days"]:
            if k not in data["period"]:
                errors.append(f"Missing period.{k}")

    if "kpis" in data:
        kpis = data["kpis"]
        kpi_keys = [
            "heat_respiratory_risk_index",
            "respiratory_disease_surge_probability",
            "combined_respiratory_stress_index",
            "icu_dual_load_risk",
            "alert_level",
        ]
        for k in kpi_keys:
            if k not in kpis:
                errors.append(f"Missing kpis.{k}")

        # Range checks
        if "heat_respiratory_risk_index" in kpis:
            v = kpis["heat_respiratory_risk_index"].get("value", -1)
            if not (0 <= v <= 100):
                errors.append(f"heat_respiratory_risk_index.value={v} out of range [0,100]")
            lvl = kpis["heat_respiratory_risk_index"].get("level", "")
            if lvl not in VALID_RISK_LEVELS:
                errors.append(f"Invalid risk level: '{lvl}'")

        if "respiratory_disease_surge_probability" in kpis:
            v = kpis["respiratory_disease_surge_probability"].get("value_pct", -1)
            if not (0 <= v <= 100):
                errors.append(f"surge_probability.value_pct={v} out of range [0,100]")

        if "combined_respiratory_stress_index" in kpis:
            v = kpis["combined_respiratory_stress_index"].get("value", -1)
            if not (0.0 <= v <= 1.0):
                errors.append(f"combined_stress.value={v} out of range [0,1]")

        if "alert_level" in kpis:
            v = kpis["alert_level"].get("value", "")
            if v not in VALID_ALERT_LEVELS:
                errors.append(f"Invalid alert_level: '{v}'")

    if "drivers" in data:
        if not isinstance(data["drivers"], list):
            errors.append("drivers must be a list")

    return errors


def validate_env_timeseries(df: pd.DataFrame) -> List[str]:
    """Validate environmental timeseries DataFrame."""
    errors = []
    for col in ENV_TIMESERIES_COLUMNS:
        if col not in df.columns:
            errors.append(f"Missing column: '{col}'")
    if len(df) == 0:
        errors.append("DataFrame is empty")
    return errors


def validate_micro_signals(df: pd.DataFrame) -> List[str]:
    """Validate micro signals DataFrame."""
    errors = []
    for col in MICRO_SIGNALS_COLUMNS:
        if col not in df.columns:
            errors.append(f"Missing column: '{col}'")
    if len(df) == 0:
        errors.append("DataFrame is empty")
    return errors


def validate_vulnerability(df: pd.DataFrame) -> List[str]:
    """Validate vulnerability DataFrame."""
    errors = []
    for col in VULNERABILITY_COLUMNS:
        if col not in df.columns:
            errors.append(f"Missing column: '{col}'")
    if len(df) == 0:
        errors.append("DataFrame is empty")
    # Range checks
    if "vulnerability_score" in df.columns:
        if df["vulnerability_score"].min() < 0 or df["vulnerability_score"].max() > 100:
            errors.append("vulnerability_score out of range [0,100]")
    return errors
