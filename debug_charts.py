
import os
import sys
import pandas as pd
import django
from django.conf import settings

# Setup Django environment
sys.path.append(r'd:\SACHIN RAWAL FILES\python\graphy')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shark_tank_graphy.settings')
django.setup()

from dashboard.utils import load_data, get_filter_options
from dashboard.charts import deals_by_season_chart, shark_investment_trend_chart

print("--- Data Loading Test ---")
try:
    df = load_data()
    print(f"Data loaded successfully. Shape: {df.shape}")
    print("Columns:", df.columns.tolist())
except Exception as e:
    print(f"Error loading data: {e}")
    sys.exit(1)

print("\n--- Filter Options Test ---")
try:
    options = get_filter_options()
    print("Seasons:", options['seasons'][:5], "...")
    print("Industries:", options['industries'][:5], "...")
    print("Sharks:", options['sharks'])
except Exception as e:
    print(f"Error getting filter options: {e}")

print("\n--- Chart Generation Test ---")
try:
    html = deals_by_season_chart(df)
    print("Chart HTML generated successfully.")
    print("Length:", len(html))
    print("Preview:", html[:200])
except Exception as e:
    print(f"Error generating chart: {e}")

print("\n--- Shark Chart Test ---")
try:
    # Test with Kevin O Leary
    html = shark_investment_trend_chart(df, "Kevin O Leary")
    print("Shark Chart HTML generated successfully.")
    print("Length:", len(html))
except Exception as e:
    print(f"Error generating shark chart: {e}")
