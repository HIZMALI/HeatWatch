"""
Signal Fusion for HEATWATCH+ Demo.
Combines environmental and micro-signal data into unified risk assessment inputs.
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple


def fuse_signals(
    df_env: pd.DataFrame,
    df_micro: pd.DataFrame,
) -> pd.DataFrame:
    """
    Merge environmental and micro-signal timeseries on date,
    compute combined metrics for each day.
    """
    # Merge on date
    df = pd.merge(df_env, df_micro, on="date", how="inner")

    # Compute daily environmental stress index (0-100)
    temp_norm = ((df["temp_c"] - 25) / 20 * 100).clip(0, 100)
    night_norm = ((df["nighttime_temp_c"] - 15) / 15 * 100).clip(0, 100)
    pm25_norm = ((df["pm25_ugm3"] - 10) / 70 * 100).clip(0, 100)

    df["env_stress_index"] = (0.35 * temp_norm + 0.30 * night_norm + 0.35 * pm25_norm).round(1)

    # Compute daily population signal index (0-100)
    df["pop_signal_index"] = (
        0.4 * df["symptom_search_index"]
        + 0.35 * df["pharmacy_visits_index"]
        + 0.25 * df["clinic_cases_index"]
    ).round(1)

    # Compute fusion score (overall daily risk proxy)
    df["fusion_score"] = (0.55 * df["env_stress_index"] + 0.45 * df["pop_signal_index"]).round(1)

    return df


def compute_signal_convergence(df_fused: pd.DataFrame) -> Dict[str, any]:
    """
    Determine if environmental and population signals are converging
    (both rising), which indicates higher risk.
    """
    if len(df_fused) < 3:
        return {"converging": False, "trend": "insufficient_data"}

    # Check last 3 days trend
    recent = df_fused.tail(3)
    env_trend = recent["env_stress_index"].diff().mean()
    pop_trend = recent["pop_signal_index"].diff().mean()

    converging = env_trend > 0 and pop_trend > 0
    if converging:
        trend = "both_rising"
    elif env_trend > 0:
        trend = "env_rising"
    elif pop_trend > 0:
        trend = "pop_rising"
    else:
        trend = "stable_or_declining"

    return {
        "converging": converging,
        "trend": trend,
        "env_trend_rate": round(float(env_trend), 2),
        "pop_trend_rate": round(float(pop_trend), 2),
    }


def get_latest_fused_scores(df_fused: pd.DataFrame) -> Dict[str, float]:
    """Get the latest day's fused scores."""
    latest = df_fused.iloc[-1]
    return {
        "env_stress_index": float(latest["env_stress_index"]),
        "pop_signal_index": float(latest["pop_signal_index"]),
        "fusion_score": float(latest["fusion_score"]),
        "temp_c": float(latest["temp_c"]),
        "pm25_ugm3": float(latest["pm25_ugm3"]),
    }
