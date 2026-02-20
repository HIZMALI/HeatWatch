"""
Dummy data generator for HEATWATCH+ Demo.
Uses realistic Ankara August heatwave data patterns based on
historical records from Meteostat and AQICN monitoring stations.
Seed-based for reproducible demos.
"""

import json
import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta


def generate_all(seed: int = 42, output_dir: str = None):
    """Generate all baseline data files."""
    if output_dir is None:
        output_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "data", "simulated"
        )
    os.makedirs(output_dir, exist_ok=True)

    rng = np.random.RandomState(seed)

    df_env = _generate_env_timeseries(rng)
    df_micro = _generate_micro_signals(rng, df_env)
    df_vuln = _generate_vulnerability(rng)
    kpis = _generate_kpis(rng, df_env, df_micro, df_vuln)

    # Save files
    df_env.to_csv(os.path.join(output_dir, "baseline_env_timeseries.csv"), index=False)
    df_micro.to_csv(os.path.join(output_dir, "baseline_micro_signals.csv"), index=False)
    df_vuln.to_csv(os.path.join(output_dir, "baseline_vulnerability.csv"), index=False)

    with open(os.path.join(output_dir, "baseline_kpis.json"), "w", encoding="utf-8") as f:
        json.dump(kpis, f, indent=2, ensure_ascii=False)

    return df_env, df_micro, df_vuln, kpis


def _generate_env_timeseries(rng: np.random.RandomState) -> pd.DataFrame:
    """
    Generate 24-day environmental timeseries based on realistic
    Ankara August 2025 heatwave patterns.

    Data sources:
      - Temperature: Based on Meteostat station 17130 (Ankara)
        https://meteostat.net/en/place/tr/ankara?s=17130&t=2025-08-01/2025-08-24
      - PM2.5: Based on AQICN Ankara monitoring network
        https://aqicn.org/city/ankara/m/

    Ankara Aug 2025 typical pattern:
      - Daytime highs: 30-40°C during heatwave events
      - Nighttime lows: 16-26°C
      - Humidity: 15-50% (dry continental climate)
      - PM2.5: 15-75 µg/m³ (spikes during heat + traffic)
    """
    start = datetime(2025, 8, 1)
    n_days = 24
    dates = [start + timedelta(days=i) for i in range(n_days)]

    # Real-like Ankara August 2025 temperature data
    # Based on Meteostat daily records: gradual heatwave build-up
    base_temps = [
        31.2, 32.5, 33.8, 35.1, 36.4, 37.2, 38.0, 38.5,  # Aug 1-8: ramp up
        39.2, 39.8, 40.1, 39.5, 38.8, 37.5, 36.2, 35.0,  # Aug 9-16: peak then ease
        33.8, 34.5, 36.0, 37.8, 38.5, 39.0, 38.2, 36.5,  # Aug 17-24: second wave
    ]

    nighttime_base = [
        17.5, 18.2, 19.0, 20.5, 21.8, 22.5, 23.2, 24.0,  # Aug 1-8
        24.8, 25.5, 26.0, 25.2, 24.0, 22.5, 21.0, 20.2,  # Aug 9-16
        19.5, 20.0, 21.5, 23.0, 24.2, 25.0, 24.5, 22.8,  # Aug 17-24
    ]

    # Humidity: drops during heatwave, Ankara is dry continental
    humidity_base = [
        42, 38, 35, 30, 28, 25, 22, 20,   # Aug 1-8
        18, 16, 15, 18, 22, 28, 32, 35,   # Aug 9-16
        38, 35, 30, 25, 22, 18, 20, 25,   # Aug 17-24
    ]

    # PM2.5: Based on AQICN Ankara data, spikes during heat events
    # Ankara typically sees 20-50 baseline, spikes to 60-80+ during heat
    pm25_base = [
        28, 32, 38, 42, 48, 55, 62, 68,   # Aug 1-8: rising with heat
        72, 75, 68, 58, 48, 38, 32, 28,   # Aug 9-16: peak then drop
        25, 30, 42, 55, 65, 72, 62, 48,   # Aug 17-24: second spike
    ]

    # Add realistic noise
    temps = [round(t + rng.normal(0, 0.8), 1) for t in base_temps]
    nighttime = [round(t + rng.normal(0, 0.5), 1) for t in nighttime_base]
    humidity = [round(max(10, min(60, h + rng.normal(0, 2))), 1) for h in humidity_base]
    pm25 = [round(max(10, p + rng.normal(0, 3)), 1) for p in pm25_base]

    df = pd.DataFrame({
        "date": [d.strftime("%Y-%m-%d") for d in dates],
        "temp_c": temps,
        "nighttime_temp_c": nighttime,
        "humidity_pct": humidity,
        "pm25_ugm3": pm25,
    })
    return df


def _generate_micro_signals(rng: np.random.RandomState, df_env: pd.DataFrame) -> pd.DataFrame:
    """
    Generate micro signals with lagged response to environmental factors.
    Search: lags 1 day behind PM2.5/heat
    Pharmacy: lags 1 day behind search
    Clinic: lags 1 day behind pharmacy (latest signal)
    """
    dates = df_env["date"].tolist()
    n_days = len(dates)

    # Base environmental stress (normalized PM2.5 + temp)
    pm25_norm = (df_env["pm25_ugm3"].values - 20) / 60 * 100
    temp_norm = (df_env["temp_c"].values - 25) / 20 * 100

    env_stress = 0.5 * np.clip(pm25_norm, 0, 100) + 0.5 * np.clip(temp_norm, 0, 100)

    # Symptom search: 1-day lag behind env stress
    search = np.zeros(n_days)
    search[0] = 20 + rng.normal(0, 3)
    for i in range(1, n_days):
        search[i] = 0.3 * search[i - 1] + 0.7 * env_stress[i - 1] + rng.normal(0, 2)

    # Pharmacy visits: 1-day lag behind search
    pharmacy = np.zeros(n_days)
    pharmacy[0] = 15 + rng.normal(0, 3)
    for i in range(1, n_days):
        pharmacy[i] = 0.3 * pharmacy[i - 1] + 0.7 * search[i - 1] + rng.normal(0, 2)

    # Clinic cases: 1-day lag behind pharmacy
    clinic = np.zeros(n_days)
    clinic[0] = 10 + rng.normal(0, 2)
    for i in range(1, n_days):
        clinic[i] = 0.3 * clinic[i - 1] + 0.7 * pharmacy[i - 1] + rng.normal(0, 2)

    df = pd.DataFrame({
        "date": dates,
        "symptom_search_index": np.clip(search, 0, 100).round(1),
        "pharmacy_visits_index": np.clip(pharmacy, 0, 100).round(1),
        "clinic_cases_index": np.clip(clinic, 0, 100).round(1),
    })
    return df


def _generate_vulnerability(rng: np.random.RandomState) -> pd.DataFrame:
    """
    Generate district-level vulnerability data for 10 Ankara districts.
    Based on real demographic patterns:
    - Altındağ: older population, lower SES
    - Çankaya: younger, higher SES
    - Keçiören/Mamak: mixed, moderate-high vulnerability
    """
    districts = [
        # (name, elderly%, cooling_access, ses, vulnerability, risk)
        ("Altındağ",      26, 30, 25, 88, 85),
        ("Çankaya",       14, 75, 80, 32, 35),
        ("Keçiören",      22, 45, 50, 72, 78),
        ("Yenimahalle",   16, 65, 65, 42, 45),
        ("Mamak",         24, 35, 30, 82, 80),
        ("Etimesgut",     15, 60, 60, 45, 48),
        ("Sincan",        18, 50, 45, 58, 55),
        ("Gölbaşı",       12, 70, 70, 35, 38),
        ("Pursaklar",     20, 40, 40, 65, 62),
        ("Polatlı",       19, 55, 50, 52, 50),
    ]

    rows = []
    for name, elderly, cooling, ses, vuln, risk in districts:
        rows.append({
            "district_name": name,
            "elderly_pct": elderly + rng.randint(-2, 3),
            "cooling_access_proxy": max(10, min(100, cooling + rng.randint(-3, 4))),
            "ses_proxy": max(10, min(100, ses + rng.randint(-3, 4))),
            "vulnerability_score": max(0, min(100, vuln + rng.randint(-3, 4))),
            "current_risk_score": max(0, min(100, risk + rng.randint(-3, 4))),
        })

    return pd.DataFrame(rows)


def _generate_kpis(
    rng: np.random.RandomState,
    df_env: pd.DataFrame,
    df_micro: pd.DataFrame,
    df_vuln: pd.DataFrame,
) -> dict:
    """Generate KPI JSON from the generated data (uses risk engine logic)."""
    from src.models.risk_engine import compute_all_kpis

    kpis = compute_all_kpis(df_env, df_micro, df_vuln)
    return kpis


if __name__ == "__main__":
    generate_all()
    print("✓ Data generated successfully.")
