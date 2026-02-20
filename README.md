# HEATWATCH+ Demo

**Heat-Respiratory Risk Intelligence Platform** — Ankara, Turkey

A web-based demo for the MIT Solve submission showcasing early warning for heat-related respiratory disease surges using multi-signal fusion.

## Features

- **Heat-Respiratory Risk Index** (0–100) combining environmental, health, and population signals
- **Respiratory Disease Surge Probability** with COPD/asthma/LRTI tracking
- **Elderly Vulnerability Map** — Ankara district-level choropleth
- **ICU Dual Load Risk** projection with peak-day forecast
- **Action Recommendations** for Municipality, Primary Care, and Hospitals
- **Environmental & Population Micro-Signal Trends**

## Setup

```bash
python -m venv .venv

# Windows:
.venv\Scripts\activate

# macOS/Linux:
# source .venv/bin/activate

pip install -r requirements.txt
```

## Run

```bash
streamlit run app.py
```

## Demo Notes

- Default city: **Ankara** (simulated data)
- Scenario can be changed from the sidebar
- Data is generated with a fixed seed for reproducible demos
- All data is simulated — no real patient or personal data is used

## Data & Ethics

- All data is aggregated and privacy-preserving
- No individual-level health records are used
- Designed for public health decision support, not clinical diagnosis
