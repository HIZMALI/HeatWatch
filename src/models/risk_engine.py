"""
Risk Engine for HEATWATCH+ Demo.
All formulas from spec section 6.
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List
from datetime import datetime


def _sigmoid(x: float) -> float:
    """Standard sigmoid function."""
    return 1.0 / (1.0 + np.exp(-x))


def _normalize(value: float, min_val: float, max_val: float) -> float:
    """Normalize value to 0-100 range."""
    if max_val == min_val:
        return 50.0
    return max(0.0, min(100.0, (value - min_val) / (max_val - min_val) * 100.0))


def compute_heat_score(temp_c: float, nighttime_temp_c: float) -> float:
    """
    HeatScore = normalize(daytime_temp + nighttime_weight * night_temp)
    Range: 0-100
    """
    nighttime_weight = 1.5  # nighttime heat is more dangerous
    combined = temp_c + nighttime_weight * nighttime_temp_c
    # Expected range: ~40 (25+1.5*10) to ~100 (42+1.5*30)
    return _normalize(combined, 40, 105)


def compute_pollution_score(pm25: float) -> float:
    """
    PollutionScore = normalize(pm25)
    Range: 0-100
    """
    return _normalize(pm25, 10, 80)


def compute_micro_signal_score(search: float, pharmacy: float, clinic: float) -> float:
    """
    MicroSignalScore = weighted mean(search, pharmacy, clinic)
    Range: 0-100
    """
    return 0.4 * search + 0.35 * pharmacy + 0.25 * clinic


def compute_heat_respiratory_risk_index(
    heat_score: float,
    pollution_score: float,
    vulnerability_score: float,
    micro_signal_score: float,
) -> int:
    """
    HeatRespRisk = 0.35*Heat + 0.25*Pollution + 0.25*Vulnerability + 0.15*MicroSignal
    Returns: int 0-100
    """
    risk = (
        0.35 * heat_score
        + 0.25 * pollution_score
        + 0.25 * vulnerability_score
        + 0.15 * micro_signal_score
    )
    return int(max(0, min(100, round(risk))))


def compute_respiratory_surge_probability(
    micro_signal_score: float,
    pm25: float,
    nighttime_temp: float,
) -> int:
    """
    Respiratory Disease Surge Probability (%).
    Sigmoid: p = sigmoid(a*(micro-50) + b*(pm25-35) + c*(night_temp-18))
    Returns: int 0-100
    """
    a, b, c = 0.06, 0.05, 0.08
    x = a * (micro_signal_score - 50) + b * (pm25 - 35) + c * (nighttime_temp - 18)
    p = _sigmoid(x)
    return int(max(0, min(100, round(p * 100))))


def compute_combined_stress(heat_resp_risk: int, surge_prob: int) -> float:
    """
    Combined = 0.6*(HeatRespRisk/100) + 0.4*(SurgeProb/100)
    Returns: float 0.0-1.0
    """
    return round(0.6 * (heat_resp_risk / 100.0) + 0.4 * (surge_prob / 100.0), 2)


def compute_icu_strain(heat_resp_risk: int, surge_prob: int) -> int:
    """
    ICU strain % = 5 + 0.25*HeatRespRisk + 0.15*SurgeProb
    Clamped to 0-40.
    """
    strain = 5 + 0.25 * heat_resp_risk + 0.15 * surge_prob
    return int(max(0, min(40, round(strain))))


def compute_alert_level(
    heat_resp_risk: int,
    surge_prob: int,
    combined: float,
    icu_strain: int,
    thresholds: Dict[str, int] = None,
) -> Dict[str, str]:
    """
    Determine alert level: WATCH / WARNING / EMERGENCY.
    Returns: {"value": ..., "reason": ...}
    """
    if thresholds is None:
        thresholds = {
            "watch_heat_risk": 55,
            "warning_heat_risk": 70,
            "emergency_heat_risk": 85,
            "watch_surge_prob": 35,
            "warning_surge_prob": 55,
            "emergency_surge_prob": 70,
            "emergency_icu_strain": 30,
        }

    # Check EMERGENCY first
    reasons = []
    if heat_resp_risk >= thresholds["emergency_heat_risk"]:
        reasons.append("Heat-Respiratory Risk Critical")
    if surge_prob >= thresholds["emergency_surge_prob"]:
        reasons.append("Surge Probability Critical")
    if icu_strain >= thresholds["emergency_icu_strain"]:
        reasons.append("ICU Strain Critical")
    if reasons:
        return {"value": "EMERGENCY", "reason": " + ".join(reasons)}

    # Check WARNING
    reasons = []
    if heat_resp_risk >= thresholds["warning_heat_risk"]:
        reasons.append("Elevated Heat-Respiratory Risk")
    if surge_prob >= thresholds["warning_surge_prob"]:
        reasons.append("Elevated Surge Probability")
    if combined >= 0.65:
        reasons.append("Multi-signal Threshold")
    if reasons:
        return {"value": "WARNING", "reason": " + ".join(reasons)}

    # Check WATCH
    if heat_resp_risk >= thresholds["watch_heat_risk"] or surge_prob >= thresholds["watch_surge_prob"]:
        return {"value": "WATCH", "reason": "Elevated Indicators"}

    return {"value": "NORMAL", "reason": "All indicators within normal range"}


def identify_drivers(
    df_env: pd.DataFrame,
    df_micro: pd.DataFrame,
    top_n: int = 5,
) -> List[Dict[str, Any]]:
    """
    Identify top risk drivers based on data patterns.
    Returns list of dicts with name, value, change_pct, direction.
    Always returns at least top_n items so the section is never empty.
    """
    drivers_scored = []

    # Latest values (last row)
    latest_env = df_env.iloc[-1]
    latest_micro = df_micro.iloc[-1]

    # Helper: compute % change between start and end of period
    def _pct_change(series):
        if len(series) < 2:
            return 0.0
        early = series.iloc[:max(1, len(series)//3)].mean()
        late = series.iloc[-max(1, len(series)//3):].mean()
        if early == 0:
            return 0.0
        return round((late - early) / early * 100, 1)

    # --- Environmental drivers (always included) ---
    temp_change = _pct_change(df_env["temp_c"])
    drivers_scored.append({
        "name": "Daytime Temperature",
        "value": f"{float(latest_env['temp_c']):.1f}°C",
        "change_pct": temp_change,
        "direction": "↑" if temp_change > 0 else ("↓" if temp_change < 0 else "→"),
        "score": abs(temp_change) + (20 if latest_env["temp_c"] >= 35 else 0),
    })

    night_change = _pct_change(df_env["nighttime_temp_c"])
    drivers_scored.append({
        "name": "Night-time Temperature",
        "value": f"{float(latest_env['nighttime_temp_c']):.1f}°C",
        "change_pct": night_change,
        "direction": "↑" if night_change > 0 else ("↓" if night_change < 0 else "→"),
        "score": abs(night_change) + (25 if latest_env["nighttime_temp_c"] >= 22 else 0),
    })

    pm25_change = _pct_change(df_env["pm25_ugm3"])
    drivers_scored.append({
        "name": "PM2.5 Air Quality",
        "value": f"{float(latest_env['pm25_ugm3']):.1f} µg/m³",
        "change_pct": pm25_change,
        "direction": "↑" if pm25_change > 0 else ("↓" if pm25_change < 0 else "→"),
        "score": abs(pm25_change) + (20 if latest_env["pm25_ugm3"] >= 35 else 0),
    })

    # --- Micro-signal drivers (always included) ---
    search_change = _pct_change(df_micro["symptom_search_index"])
    drivers_scored.append({
        "name": "Symptom Search Index",
        "value": f"{float(latest_micro['symptom_search_index']):.1f}",
        "change_pct": search_change,
        "direction": "↑" if search_change > 0 else ("↓" if search_change < 0 else "→"),
        "score": abs(search_change),
    })

    pharmacy_change = _pct_change(df_micro["pharmacy_visits_index"])
    drivers_scored.append({
        "name": "Pharmacy Respiratory Sales",
        "value": f"{float(latest_micro['pharmacy_visits_index']):.1f}",
        "change_pct": pharmacy_change,
        "direction": "↑" if pharmacy_change > 0 else ("↓" if pharmacy_change < 0 else "→"),
        "score": abs(pharmacy_change),
    })

    clinic_change = _pct_change(df_micro["clinic_cases_index"])
    drivers_scored.append({
        "name": "Clinic Respiratory Cases",
        "value": f"{float(latest_micro['clinic_cases_index']):.1f}",
        "change_pct": clinic_change,
        "direction": "↑" if clinic_change > 0 else ("↓" if clinic_change < 0 else "→"),
        "score": abs(clinic_change),
    })

    # Sort by impact score descending
    drivers_scored.sort(key=lambda x: x["score"], reverse=True)
    return drivers_scored[:top_n]


def _get_risk_level(value: int) -> str:
    """Map score to High/Med/Low."""
    if value >= 70:
        return "High"
    elif value >= 40:
        return "Med"
    return "Low"


def compute_all_kpis(
    df_env: pd.DataFrame,
    df_micro: pd.DataFrame,
    df_vuln: pd.DataFrame,
) -> Dict[str, Any]:
    """
    Compute all KPIs from the data and return the full KPI JSON structure.
    """
    # Latest environmental values
    latest_env = df_env.iloc[-1]
    temp_c = float(latest_env["temp_c"])
    nighttime_temp = float(latest_env["nighttime_temp_c"])
    pm25 = float(latest_env["pm25_ugm3"])

    # Latest micro signal values
    latest_micro = df_micro.iloc[-1]
    search = float(latest_micro["symptom_search_index"])
    pharmacy = float(latest_micro["pharmacy_visits_index"])
    clinic = float(latest_micro["clinic_cases_index"])

    # Average vulnerability
    avg_vulnerability = float(df_vuln["vulnerability_score"].mean())

    # Compute individual scores
    heat_score = compute_heat_score(temp_c, nighttime_temp)
    pollution_score = compute_pollution_score(pm25)
    micro_signal_score = compute_micro_signal_score(search, pharmacy, clinic)

    # Compute KPIs
    heat_resp_risk = compute_heat_respiratory_risk_index(
        heat_score, pollution_score, avg_vulnerability, micro_signal_score
    )
    surge_prob = compute_respiratory_surge_probability(
        micro_signal_score, pm25, nighttime_temp
    )
    combined = compute_combined_stress(heat_resp_risk, surge_prob)
    icu_strain = compute_icu_strain(heat_resp_risk, surge_prob)
    alert = compute_alert_level(heat_resp_risk, surge_prob, combined, icu_strain)
    drivers = identify_drivers(df_env, df_micro)

    # Peak date: find max risk day in forecast
    # Use temp + pm25 as proxy for peak
    env_stress = df_env["temp_c"] + df_env["pm25_ugm3"]
    peak_idx = env_stress.idxmax()
    peak_date = df_env.iloc[peak_idx]["date"]
    if isinstance(peak_date, pd.Timestamp):
        peak_date = peak_date.strftime("%Y-%m-%d")

    # Delta 48h: simulated
    delta_risk = max(5, int(heat_resp_risk * 0.17))
    delta_surge = max(3, int(surge_prob * 0.09))

    # Determine convergence
    convergence = combined >= 0.65

    # Build KPI JSON
    dates = df_env["date"].tolist()
    start_date = dates[0]
    end_date = dates[-1]
    if isinstance(start_date, pd.Timestamp):
        start_date = start_date.strftime("%Y-%m-%d")
    if isinstance(end_date, pd.Timestamp):
        end_date = end_date.strftime("%Y-%m-%d")

    kpi_json = {
        "location": {
            "country": "Turkey",
            "city": "Ankara",
            "district": "Altındağ",
        },
        "period": {
            "start": start_date,
            "end": end_date,
            "forecast_days": 7,
        },
        "data_mode": "real (meteostat + aqicn based)",
        "last_update": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "kpis": {
            "heat_respiratory_risk_index": {
                "value": heat_resp_risk,
                "level": _get_risk_level(heat_resp_risk),
                "delta_48h": delta_risk,
            },
            "respiratory_disease_surge_probability": {
                "value_pct": surge_prob,
                "delta_48h": delta_surge,
                "subtitle": "COPD/asthma exacerbations + LRTIs + respiratory distress trend",
            },
            "combined_respiratory_stress_index": {
                "value": combined,
                "convergence": convergence,
            },
            "icu_dual_load_risk": {
                "icu_strain_pct": icu_strain,
                "peak_date": peak_date,
            },
            "alert_level": alert,
        },
        "drivers": drivers,
        "sub_scores": {
            "heat_score": round(heat_score, 1),
            "pollution_score": round(pollution_score, 1),
            "micro_signal_score": round(micro_signal_score, 1),
            "avg_vulnerability": round(avg_vulnerability, 1),
        },
    }

    return kpi_json
