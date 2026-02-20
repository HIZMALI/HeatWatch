"""
Data schemas for HEATWATCH+ Demo.
Defines expected structure for all data contracts.
"""

from dataclasses import dataclass, field
from typing import List, Optional


# ---------- KPI Schema ----------

@dataclass
class LocationSchema:
    country: str
    city: str
    district: str


@dataclass
class PeriodSchema:
    start: str  # YYYY-MM-DD
    end: str    # YYYY-MM-DD
    forecast_days: int


@dataclass
class HeatRespiratoryRiskIndex:
    value: int        # 0-100
    level: str        # High / Med / Low
    delta_48h: int


@dataclass
class RespiratoryDiseaseSurgeProbability:
    value_pct: int    # 0-100
    delta_48h: int
    subtitle: str


@dataclass
class CombinedRespiratoryStressIndex:
    value: float      # 0.0 - 1.0
    convergence: bool


@dataclass
class ICUDualLoadRisk:
    icu_strain_pct: int
    peak_date: str    # YYYY-MM-DD


@dataclass
class AlertLevel:
    value: str        # WATCH / WARNING / EMERGENCY
    reason: str


@dataclass
class KPIs:
    heat_respiratory_risk_index: HeatRespiratoryRiskIndex
    respiratory_disease_surge_probability: RespiratoryDiseaseSurgeProbability
    combined_respiratory_stress_index: CombinedRespiratoryStressIndex
    icu_dual_load_risk: ICUDualLoadRisk
    alert_level: AlertLevel


@dataclass
class KPIData:
    location: LocationSchema
    period: PeriodSchema
    data_mode: str
    last_update: str
    kpis: KPIs
    drivers: List[str]


# ---------- CSV Column Definitions ----------

ENV_TIMESERIES_COLUMNS = [
    "date", "temp_c", "nighttime_temp_c", "humidity_pct", "pm25_ugm3"
]

MICRO_SIGNALS_COLUMNS = [
    "date", "symptom_search_index", "pharmacy_visits_index", "clinic_cases_index"
]

VULNERABILITY_COLUMNS = [
    "district_name", "elderly_pct", "cooling_access_proxy",
    "ses_proxy", "vulnerability_score", "current_risk_score"
]

# Valid alert levels
VALID_ALERT_LEVELS = ["WATCH", "WARNING", "EMERGENCY"]

# Valid risk levels
VALID_RISK_LEVELS = ["High", "Med", "Low"]
