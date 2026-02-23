"""
Data processing utilities for Shark Tank dataset
"""
import pandas as pd
import os

# Path to the dataset
from django.conf import settings

# Path to the dataset
DATA_PATH = settings.BASE_DIR / 'Shark Tank US dataset.csv'

# Cache for loaded data
_data_cache = None

def load_data():
    """Load and clean the Shark Tank dataset"""
    global _data_cache
    
    if _data_cache is not None:
        return _data_cache
    
    try:
        df = pd.read_csv(DATA_PATH, encoding='utf-8')  # Ensure utf-8
    except FileNotFoundError:
        print(f"Error: Dataset not found at {DATA_PATH}")
        # Return empty DataFrame with expected structure to prevent crashes
        return pd.DataFrame()
    except Exception as e:
        print(f"Error loading dataset: {e}")
        return pd.DataFrame()
    
    # Clean column names (remove extra spaces)
    df.columns = df.columns.str.strip()
    
    # Standardize column names for key sharks to handle "Kevin O Leary" vs "Kevin O'Leary"
    # This addresses Audit Point #7
    rename_map = {}
    for col in df.columns:
        if "Kevin O" in col and "Leary" in col:
            new_col = col.replace("Kevin O'Leary", "Kevin O Leary")
            if new_col != col:
                rename_map[col] = new_col
    
    if rename_map:
        df = df.rename(columns=rename_map)
    
    # Convert numeric columns
    numeric_cols = [
        'Season Number', 'Episode Number', 'Pitch Number',
        'Original Ask Amount', 'Original Offered Equity', 'Valuation Requested',
        'Total Deal Amount', 'Total Deal Equity', 'Deal Valuation',
        'Number of Sharks in Deal', 'Investment Amount Per Shark', 'Equity Per Shark'
    ]
    
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Clean the Got Deal column
    if 'Got Deal' in df.columns:
        df['Got Deal'] = df['Got Deal'].fillna(0).astype(int)
    
    _data_cache = df
    return df


def get_filter_options():
    """Get unique values for filter options"""
    df = load_data()
    
    seasons = sorted(df['Season Number'].dropna().unique().astype(int).tolist())
    
    industries = sorted(df['Industry'].dropna().unique().tolist())
    
    # Get shark names from the investment columns
    sharks = [
        'Barbara Corcoran',
        'Mark Cuban',
        'Lori Greiner',
        'Robert Herjavec',
        'Daymond John',
        'Kevin O Leary'
    ]
    
    deal_statuses = [
        {'value': 'all', 'label': 'All'},
        {'value': 'yes', 'label': 'Got Deal'},
        {'value': 'no', 'label': 'No Deal'},
    ]
    
    return {
        'seasons': seasons,
        'industries': industries,
        'sharks': sharks,
        'deal_statuses': deal_statuses,
    }


def filter_data(df, seasons=None, industries=None, sharks=None, got_deal=None):
    """Filter data based on selected criteria (supports multi-value lists)"""
    filtered = df.copy()
    
    # Multi-value season filter
    if seasons:
        int_seasons = [int(s) for s in seasons]
        filtered = filtered[filtered['Season Number'].isin(int_seasons)]
    
    # Multi-value industry filter
    if industries:
        filtered = filtered[filtered['Industry'].isin(industries)]
    
    # Multi-value shark filter (union: show rows where ANY selected shark invested)
    if sharks:
        shark_mask = pd.Series(False, index=filtered.index)
        for shark in sharks:
            shark_col = f"{shark} Investment Amount"
            if shark_col in filtered.columns:
                shark_mask = shark_mask | (filtered[shark_col].notna() & (filtered[shark_col] > 0))
        filtered = filtered[shark_mask]
    
    # Single-value deal status filter
    if got_deal and got_deal != 'all':
        if got_deal == 'yes':
            filtered = filtered[filtered['Got Deal'] == 1]
        elif got_deal == 'no':
            filtered = filtered[filtered['Got Deal'] == 0]
    
    return filtered


def get_stats(df):
    """Calculate summary statistics from the data"""
    total_pitches = len(df)
    total_deals = df['Got Deal'].sum() if 'Got Deal' in df.columns else 0
    deal_rate = (total_deals / total_pitches * 100) if total_pitches > 0 else 0
    
    total_investment = df['Total Deal Amount'].sum() if 'Total Deal Amount' in df.columns else 0
    avg_deal = df[df['Got Deal'] == 1]['Total Deal Amount'].mean() if 'Got Deal' in df.columns else 0
    
    return {
        'total_pitches': int(total_pitches),
        'total_deals': int(total_deals),
        'deal_rate': round(deal_rate, 1),
        'total_investment': total_investment if pd.notna(total_investment) else 0,
        'avg_deal': avg_deal if pd.notna(avg_deal) else 0
    }
