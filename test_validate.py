import sys
sys.path.insert(0, '.')
from datetime import datetime, timedelta
from src.data.real_data_fetcher import fetch_and_prepare
from src.models.risk_engine import compute_all_kpis
from src.data.loaders import load_vulnerability

end = datetime.now() - timedelta(days=1)
start = end - timedelta(days=6)
print(f"Fetching {start.date()} to {end.date()}")
df_env, df_micro = fetch_and_prepare(start, end)
print(f"df_env rows: {len(df_env)}, cols: {list(df_env.columns)}")
print(f"df_micro rows: {len(df_micro)}, cols: {list(df_micro.columns)}")
df_vuln = load_vulnerability()
kpis = compute_all_kpis(df_env, df_micro, df_vuln)
alert = kpis["kpis"]["alert_level"]["value"]
print(f"KPIs ok: alert={alert}")
print(f"Last update: {kpis['last_update']}")
print("ALL OK")
