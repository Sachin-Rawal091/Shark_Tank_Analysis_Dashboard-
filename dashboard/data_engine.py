"""
Visualization Strategy Engine — context-aware chart data builder.

Implements the 12-rule strategy:
  1. Filter depth detection (deep_dive / comparison / overview)
  2. Dataset size handling
  3. Distribution detection
  4. Time-series detection
  5. Correlation detection
  6. Ranking detection
  7. Multi-dimensional data
  8. Smart chart suggestions (8A–8F)
  9. Chart limiter (max 5)
 10. Adaptive layout hints
 11. Insight engine
 12. Strict rendering (frontend responsibility)
"""
import pandas as pd
import numpy as np

SHARKS = [
    'Barbara Corcoran',
    'Mark Cuban',
    'Lori Greiner',
    'Robert Herjavec',
    'Daymond John',
    'Kevin O Leary',
]

SHARK_LAST = {s: s.split()[-1] for s in SHARKS}  # short labels

# ── Helpers ──────────────────────────────────────────────────────────────

def _safe(val):
    if isinstance(val, (np.integer,)):
        return int(val)
    if isinstance(val, (np.floating,)):
        return round(float(val), 2)
    if isinstance(val, float) and (pd.isna(val) or np.isinf(val)):
        return 0
    return val

def _sl(series):
    """Safe list — convert series/array to JSON-safe Python list."""
    return [_safe(v) for v in series]

# ── Mode detection (Rule 1) ─────────────────────────────────────────────

def _detect_mode(filters):
    """Return ('deep_dive', category) | ('comparison', category) | ('overview', None)."""
    cats = {
        'seasons':    filters.get('seasons', []) or [],
        'industries': filters.get('industries', []) or [],
        'sharks':     filters.get('sharks', []) or [],
    }
    # Priority: deep dive if exactly 1 in any category
    for cat, vals in cats.items():
        if len(vals) == 1:
            return 'deep_dive', cat
    # Comparison if 2+ in any category
    for cat, vals in cats.items():
        if len(vals) >= 2:
            return 'comparison', cat
    # Deal-only filter still counts as overview with possible size adjustment
    return 'overview', None


# ═══════════════════════════════════════════════════════════════════════
#  CHART BLOCK BUILDERS
#  Each returns a dict with: id, title, hint, labels, datasets, wide
# ═══════════════════════════════════════════════════════════════════════

# ── Trend / Time-Series ──────────────────────────────────────────────

def _pitches_deals_trend(df):
    """Pitches vs Deals per season → line."""
    grp = df.groupby('Season Number').agg(
        pitches=('Got Deal', 'count'),
        deals=('Got Deal', 'sum'),
    ).reset_index().sort_values('Season Number')
    if grp.empty:
        return None
    return {
        'id': 'pitches_deals_trend', 'title': 'Pitches vs Deals by Season',
        'hint': 'line', 'wide': True,
        'labels': _sl(grp['Season Number']),
        'datasets': [
            {'name': 'Total Pitches', 'values': _sl(grp['pitches'])},
            {'name': 'Deals Made',    'values': _sl(grp['deals'])},
        ],
    }

def _investment_trend_area(df):
    """Total investment per season → area."""
    deals = df[df['Got Deal'] == 1]
    if deals.empty or 'Total Deal Amount' not in deals.columns:
        return None
    grp = deals.groupby('Season Number')['Total Deal Amount'].sum().reset_index().sort_values('Season Number')
    if len(grp) < 2:
        return None
    return {
        'id': 'investment_growth', 'title': 'Investment Growth by Season',
        'hint': 'area', 'wide': True,
        'labels': _sl(grp['Season Number']),
        'datasets': [{'name': 'Total Investment ($)', 'values': _sl(grp['Total Deal Amount'])}],
    }

def _investment_by_episode_line(df, season):
    """Investment trend by episode within one season → line (Rule 8A)."""
    deals = df[(df['Got Deal'] == 1)]
    if deals.empty or 'Episode Number' not in deals.columns:
        return None
    grp = deals.groupby('Episode Number')['Total Deal Amount'].sum().reset_index().sort_values('Episode Number')
    if len(grp) < 2:
        return None
    return {
        'id': 'episode_investment', 'title': f'Investment Trend — Season {season}',
        'hint': 'line', 'wide': True,
        'labels': _sl(grp['Episode Number']),
        'datasets': [{'name': 'Deal Amount ($)', 'values': _sl(grp['Total Deal Amount'])}],
    }

def _shark_season_trend_line(df, shark_name):
    """Single shark investment across seasons → line (Rule 8C)."""
    col = f'{shark_name} Investment Amount'
    if col not in df.columns:
        return None
    grp = df.groupby('Season Number')[col].sum().reset_index().sort_values('Season Number')
    grp = grp[grp[col] > 0]
    if len(grp) < 2:
        return None
    return {
        'id': 'shark_season_trend', 'title': f'{shark_name} — Investment by Season',
        'hint': 'line', 'wide': True,
        'labels': _sl(grp['Season Number']),
        'datasets': [{'name': 'Investment ($)', 'values': _sl(grp[col])}],
    }

def _industry_growth_area(df, industry):
    """Single industry growth across seasons → area (Rule 8B)."""
    deals = df[df['Got Deal'] == 1]
    if deals.empty:
        return None
    grp = deals.groupby('Season Number')['Total Deal Amount'].sum().reset_index().sort_values('Season Number')
    if len(grp) < 2:
        return None
    return {
        'id': 'industry_growth', 'title': f'{industry} — Funding by Season',
        'hint': 'area', 'wide': True,
        'labels': _sl(grp['Season Number']),
        'datasets': [{'name': 'Total Funding ($)', 'values': _sl(grp['Total Deal Amount'])}],
    }

# ── Multi-line / Stacked Area (Comparison mode) ─────────────────────

def _multi_season_trend(df, seasons):
    """Multi-line: compare pitches across selected seasons → multi_line (Rule 8D)."""
    grp = df.groupby('Season Number').agg(
        pitches=('Got Deal', 'count'),
        deals=('Got Deal', 'sum'),
    ).reset_index().sort_values('Season Number')
    if grp.empty:
        return None
    return {
        'id': 'multi_season_trend', 'title': 'Season Comparison — Pitches vs Deals',
        'hint': 'multi_line', 'wide': True,
        'labels': _sl(grp['Season Number']),
        'datasets': [
            {'name': 'Pitches', 'values': _sl(grp['pitches'])},
            {'name': 'Deals',   'values': _sl(grp['deals'])},
        ],
    }

def _stacked_area_growth(df, label):
    """Stacked area: investment growth → stacked_area (Rules 8D/8F)."""
    deals = df[df['Got Deal'] == 1]
    if deals.empty:
        return None
    grp = deals.groupby('Season Number')['Total Deal Amount'].agg(['sum', 'mean']).reset_index()
    grp.columns = ['Season', 'Total', 'Average']
    grp = grp.sort_values('Season')
    if len(grp) < 2:
        return None
    return {
        'id': 'stacked_area_growth', 'title': f'{label} — Investment Growth',
        'hint': 'stacked_area', 'wide': True,
        'labels': _sl(grp['Season']),
        'datasets': [
            {'name': 'Total ($)',   'values': _sl(grp['Total'])},
            {'name': 'Average ($)', 'values': _sl(grp['Average'])},
        ],
    }

# ── Distribution ─────────────────────────────────────────────────────

def _deal_distribution(df, chart_type='donut'):
    """Deal vs No-Deal → pie or donut (Rule 3: only if segments ≥ 3? here it's always 2 but it's the core metric)."""
    got = int(df['Got Deal'].sum())
    no = int(len(df) - got)
    if got == 0 and no == 0:
        return None
    return {
        'id': 'deal_distribution', 'title': 'Deal Success Rate',
        'hint': chart_type, 'wide': False,
        'labels': ['Got Deal', 'No Deal'],
        'datasets': [{'name': 'Count', 'values': [got, no]}],
    }

def _industry_distribution(df):
    """Top industries by count → donut (Rule 3: use h-bar if too many)."""
    counts = df['Industry'].value_counts().head(10)
    if len(counts) < 3:
        # Rule 2A/3: too few segments → horizontal bar instead
        if counts.empty:
            return None
        return {
            'id': 'industry_dist', 'title': 'Industries by Pitch Count',
            'hint': 'horizontal_bar', 'wide': False,
            'labels': counts.index.tolist(),
            'datasets': [{'name': 'Pitches', 'values': _sl(counts.values)}],
        }
    return {
        'id': 'industry_dist', 'title': 'Top Industries by Pitch Count',
        'hint': 'donut', 'wide': False,
        'labels': counts.index.tolist(),
        'datasets': [{'name': 'Pitches', 'values': _sl(counts.values)}],
    }

# ── Comparison (Bar) ────────────────────────────────────────────────

def _shark_investment_bar(df):
    """Total investment per shark → bar (comparison)."""
    names, totals = [], []
    for shark in SHARKS:
        col = f'{shark} Investment Amount'
        if col in df.columns:
            total = df[col].sum()
            if pd.notna(total) and total > 0:
                names.append(SHARK_LAST[shark])
                totals.append(_safe(total))
    if not names:
        return None
    return {
        'id': 'shark_investment', 'title': 'Investment by Shark',
        'hint': 'bar', 'wide': False,
        'labels': names,
        'datasets': [{'name': 'Total Investment ($)', 'values': totals}],
    }

def _avg_deal_per_shark_bar(df):
    """Average deal size per shark → bar (Rule 8A)."""
    names, avgs = [], []
    for shark in SHARKS:
        col = f'{shark} Investment Amount'
        if col in df.columns:
            inv = df[col].dropna()
            inv = inv[inv > 0]
            if len(inv) > 0:
                names.append(SHARK_LAST[shark])
                avgs.append(_safe(inv.mean()))
    if not names:
        return None
    return {
        'id': 'avg_deal_shark', 'title': 'Average Deal Size per Shark',
        'hint': 'bar', 'wide': False,
        'labels': names,
        'datasets': [{'name': 'Avg Deal ($)', 'values': avgs}],
    }

def _industry_grouped_bar(df, selected):
    """Grouped bar comparing selected industries → grouped_bar (Rule 8F)."""
    deals = df[df['Got Deal'] == 1]
    if deals.empty:
        return None
    grp = deals.groupby('Industry')['Total Deal Amount'].agg(['sum', 'count']).reset_index()
    grp.columns = ['Industry', 'Total', 'Deals']
    grp = grp[grp['Industry'].isin(selected)] if selected else grp.nlargest(10, 'Total')
    if grp.empty:
        return None
    return {
        'id': 'industry_comparison', 'title': 'Industry Funding Comparison',
        'hint': 'grouped_bar', 'wide': True,
        'labels': grp['Industry'].tolist(),
        'datasets': [
            {'name': 'Total Funding ($)', 'values': _sl(grp['Total'])},
            {'name': 'Deal Count',         'values': _sl(grp['Deals'])},
        ],
    }

def _shark_grouped_bar(df, selected):
    """Grouped bar comparing selected sharks → grouped_bar (Rule 8E)."""
    names, totals, counts = [], [], []
    for shark in SHARKS:
        short = SHARK_LAST[shark]
        if selected and short not in selected and shark not in selected:
            continue
        col = f'{shark} Investment Amount'
        if col in df.columns:
            inv = df[col].dropna()
            inv = inv[inv > 0]
            if len(inv) > 0:
                names.append(short)
                totals.append(_safe(inv.sum()))
                counts.append(int(len(inv)))
    if not names:
        return None
    return {
        'id': 'shark_comparison', 'title': 'Shark Investment Comparison',
        'hint': 'grouped_bar', 'wide': True,
        'labels': names,
        'datasets': [
            {'name': 'Total Investment ($)', 'values': totals},
            {'name': 'Deal Count',           'values': counts},
        ],
    }

def _season_investment_grouped_bar(df):
    """Grouped bar: investment comparison across seasons → grouped_bar (Rule 8D)."""
    deals = df[df['Got Deal'] == 1]
    if deals.empty:
        return None
    grp = deals.groupby('Season Number')['Total Deal Amount'].agg(['sum', 'mean']).reset_index()
    grp.columns = ['Season', 'Total', 'Average']
    grp = grp.sort_values('Season')
    if grp.empty:
        return None
    return {
        'id': 'season_investment_compare', 'title': 'Season Investment Comparison',
        'hint': 'grouped_bar', 'wide': True,
        'labels': [f'S{int(s)}' for s in grp['Season']],
        'datasets': [
            {'name': 'Total ($)', 'values': _sl(grp['Total'])},
            {'name': 'Avg Deal ($)', 'values': _sl(grp['Average'])},
        ],
    }

def _season_funding_bar(df):
    """Season-wise funding bar (Rule 8B)."""
    deals = df[df['Got Deal'] == 1]
    if deals.empty:
        return None
    grp = deals.groupby('Season Number')['Total Deal Amount'].sum().reset_index().sort_values('Season Number')
    if grp.empty:
        return None
    return {
        'id': 'season_funding', 'title': 'Funding by Season',
        'hint': 'bar', 'wide': False,
        'labels': [f'S{int(s)}' for s in grp['Season Number']],
        'datasets': [{'name': 'Total Funding ($)', 'values': _sl(grp['Total Deal Amount'])}],
    }

def _shark_industry_bar(df, shark_name):
    """Single shark's industry breakdown → bar (Rule 8C)."""
    col = f'{shark_name} Investment Amount'
    if col not in df.columns:
        return None
    inv = df[df[col] > 0].groupby('Industry')[col].sum().nlargest(8)
    if inv.empty:
        return None
    return {
        'id': 'shark_industry', 'title': f'{shark_name} — by Industry',
        'hint': 'bar', 'wide': False,
        'labels': inv.index.tolist(),
        'datasets': [{'name': 'Investment ($)', 'values': _sl(inv.values)}],
    }

# ── Ranking (Horizontal Bar) ────────────────────────────────────────

def _top_industries_ranking(df):
    """Top 10 industries by funding → horizontal bar (Rule 6)."""
    deals = df[df['Got Deal'] == 1]
    if deals.empty:
        return None
    grp = deals.groupby('Industry')['Total Deal Amount'].sum().nlargest(10).sort_values()
    if grp.empty:
        return None
    return {
        'id': 'top_industries', 'title': 'Top Industries by Funding',
        'hint': 'horizontal_bar', 'wide': True,
        'labels': grp.index.tolist(),
        'datasets': [{'name': 'Total Funding ($)', 'values': _sl(grp.values)}],
    }

def _shark_ranking(df):
    """Sharks ranked by total investment → horizontal bar (Rule 8A)."""
    names, totals = [], []
    for shark in SHARKS:
        col = f'{shark} Investment Amount'
        if col in df.columns:
            t = df[col].sum()
            if pd.notna(t) and t > 0:
                names.append(SHARK_LAST[shark])
                totals.append(_safe(t))
    if not names:
        return None
    # Sort ascending for h-bar
    paired = sorted(zip(names, totals), key=lambda x: x[1])
    names, totals = zip(*paired)
    return {
        'id': 'shark_ranking', 'title': 'Shark Investment Ranking',
        'hint': 'horizontal_bar', 'wide': True,
        'labels': list(names),
        'datasets': [{'name': 'Total ($)', 'values': list(totals)}],
    }

def _top_sharks_for_industry(df):
    """Top sharks by investment in this industry → horizontal bar (Rule 8B)."""
    names, totals = [], []
    for shark in SHARKS:
        col = f'{shark} Investment Amount'
        if col in df.columns:
            t = df[col].sum()
            if pd.notna(t) and t > 0:
                names.append(SHARK_LAST[shark])
                totals.append(_safe(t))
    if not names:
        return None
    paired = sorted(zip(names, totals), key=lambda x: x[1])
    names, totals = zip(*paired)
    return {
        'id': 'top_sharks_industry', 'title': 'Top Sharks in this Industry',
        'hint': 'horizontal_bar', 'wide': False,
        'labels': list(names),
        'datasets': [{'name': 'Investment ($)', 'values': list(totals)}],
    }

# ── Correlation (Scatter) ───────────────────────────────────────────

def _ask_vs_deal_scatter(df):
    """Ask vs Deal amount → scatter (Rule 5: skip if < 5 points)."""
    deals = df[(df['Got Deal'] == 1)][['Original Ask Amount', 'Total Deal Amount']].dropna()
    if len(deals) < 5:   # Rule 2A
        return None
    return {
        'id': 'ask_vs_deal', 'title': 'Ask Amount vs Deal Amount',
        'hint': 'scatter', 'wide': False,
        'labels': _sl(deals['Original Ask Amount']),
        'datasets': [{'name': 'Deal Amount ($)', 'values': _sl(deals['Total Deal Amount'])}],
        'trendline': len(deals) >= 8,  # Rule 5
    }

# ── Stacked Bar ──────────────────────────────────────────────────────

def _season_deal_stacked(df):
    """Deal/No-Deal per season → stacked bar."""
    grp = df.groupby('Season Number')['Got Deal'].value_counts().unstack(fill_value=0).sort_index()
    for c in [0, 1]:
        if c not in grp.columns:
            grp[c] = 0
    return {
        'id': 'season_deal_stack', 'title': 'Deal Breakdown by Season',
        'hint': 'stacked_bar', 'wide': True,
        'labels': _sl(grp.index),
        'datasets': [
            {'name': 'Got Deal', 'values': _sl(grp[1])},
            {'name': 'No Deal',  'values': _sl(grp[0])},
        ],
    }

def _shark_season_stacked(df, shark_name):
    """Single shark participation by season → stacked bar (Rule 8C)."""
    col = f'{shark_name} Investment Amount'
    pcol = f'{shark_name} Present'
    if col not in df.columns or pcol not in df.columns:
        return None
    present = df[df[pcol] == 1].groupby('Season Number').agg(
        invested=(col, lambda x: (x > 0).sum()),
        present=(col, 'count'),
    ).reset_index().sort_values('Season Number')
    if present.empty:
        return None
    present['passed'] = present['present'] - present['invested']
    return {
        'id': 'shark_season_stack', 'title': f'{shark_name} — Season Activity',
        'hint': 'stacked_bar', 'wide': True,
        'labels': _sl(present['Season Number']),
        'datasets': [
            {'name': 'Invested', 'values': _sl(present['invested'])},
            {'name': 'Passed',   'values': _sl(present['passed'])},
        ],
    }

# ── Heatmap (Rule 7) ────────────────────────────────────────────────

def _shark_industry_heatmap(df, selected_sharks=None):
    """Shark × Industry investment heatmap (Rule 8E)."""
    sharks_to_use = selected_sharks if selected_sharks else [SHARK_LAST[s] for s in SHARKS]
    z, y_labels = [], []
    for shark in SHARKS:
        short = SHARK_LAST[shark]
        if short not in sharks_to_use and shark not in (selected_sharks or []):
            continue
        col = f'{shark} Investment Amount'
        if col not in df.columns:
            continue
        inv = df[df[col] > 0].groupby('Industry')[col].sum()
        if inv.empty:
            continue
        y_labels.append(short)
        z.append(inv)

    if not z:
        return None

    # Build matrix — top 8 industries by total
    all_industries = pd.concat(z, axis=1).fillna(0)
    all_industries.columns = y_labels
    top_ind = all_industries.sum(axis=1).nlargest(8).index.tolist()
    matrix = all_industries.loc[all_industries.index.isin(top_ind)]

    if matrix.empty:
        return None

    return {
        'id': 'shark_industry_heat', 'title': 'Shark × Industry Heatmap',
        'hint': 'heatmap', 'wide': True,
        'labels': matrix.index.tolist(),       # x = industries
        'y_labels': y_labels,                   # y = sharks
        'datasets': [{'name': 'Investment ($)', 'values': [_sl(matrix[col]) for col in matrix.columns]}],
    }

def _shark_season_stacked_bar_multi(df, selected_sharks):
    """Multiple sharks: season-wise stacked bar (Rule 8E)."""
    datasets = []
    all_seasons = sorted(df['Season Number'].unique())
    for shark in SHARKS:
        short = SHARK_LAST[shark]
        if short not in (selected_sharks or []) and shark not in (selected_sharks or []):
            continue
        col = f'{shark} Investment Amount'
        if col not in df.columns:
            continue
        grp = df.groupby('Season Number')[col].sum().reindex(all_seasons, fill_value=0)
        if grp.sum() > 0:
            datasets.append({'name': short, 'values': _sl(grp.values)})
    if not datasets:
        return None
    return {
        'id': 'shark_season_dist', 'title': 'Shark Investment by Season',
        'hint': 'stacked_bar', 'wide': True,
        'labels': _sl(all_seasons),
        'datasets': datasets,
    }


# ═══════════════════════════════════════════════════════════════════════
#  INSIGHT ENGINE (Rule 11)
# ═══════════════════════════════════════════════════════════════════════

def _generate_insights(df, mode, category, filters):
    """Generate 2-3 data-driven textual insights."""
    insights = []
    n = len(df)
    if n == 0:
        return ['No data matches the current filters.']

    deals = df[df['Got Deal'] == 1]
    deal_rate = round(len(deals) / n * 100, 1) if n else 0

    # Best season
    if 'Season Number' in df.columns and len(df['Season Number'].unique()) > 1:
        best_season = deals.groupby('Season Number')['Total Deal Amount'].sum().idxmax() if not deals.empty else None
        if best_season is not None:
            total = _safe(deals.groupby('Season Number')['Total Deal Amount'].sum().max())
            insights.append(f'Season {int(best_season)} attracted the highest total investment of ${total:,.0f}.')

    # Top shark
    shark_totals = {}
    for shark in SHARKS:
        col = f'{shark} Investment Amount'
        if col in df.columns:
            t = df[col].sum()
            if pd.notna(t) and t > 0:
                shark_totals[SHARK_LAST[shark]] = t
    if shark_totals:
        top_shark = max(shark_totals, key=shark_totals.get)
        insights.append(f'{top_shark} leads with ${_safe(shark_totals[top_shark]):,.0f} in total investment.')

    # Deal rate
    insights.append(f'Overall deal success rate: {deal_rate}% ({len(deals)} of {n} pitches).')

    # Top industry
    if 'Industry' in df.columns and not deals.empty:
        top_ind = deals.groupby('Industry')['Total Deal Amount'].sum().idxmax()
        top_val = _safe(deals.groupby('Industry')['Total Deal Amount'].sum().max())
        insights.append(f'{top_ind} is the top-funded industry with ${top_val:,.0f}.')

    return insights[:3]   # Max 3


# ═══════════════════════════════════════════════════════════════════════
#  SMART CHART SUGGESTION STRATEGIES (Rule 8A–8F + overview)
# ═══════════════════════════════════════════════════════════════════════

def _strategy_single_season(df, filters):
    """Rule 8A: single season selected."""
    season = filters['seasons'][0]
    builders = [
        lambda: _investment_by_episode_line(df, season),
        lambda: _shark_ranking(df),
        lambda: _industry_distribution(df),
        lambda: _avg_deal_per_shark_bar(df),
        lambda: _ask_vs_deal_scatter(df),
    ]
    return _run_builders(builders)

def _strategy_single_industry(df, filters):
    """Rule 8B: single industry selected."""
    industry = filters['industries'][0]
    builders = [
        lambda: _industry_growth_area(df, industry),
        lambda: _top_sharks_for_industry(df),
        lambda: _ask_vs_deal_scatter(df),
        lambda: _season_funding_bar(df),
        lambda: _deal_distribution(df, 'pie'),
    ]
    return _run_builders(builders)

def _strategy_single_shark(df, filters):
    """Rule 8C: single shark selected."""
    shark = filters['sharks'][0]
    builders = [
        lambda: _shark_season_trend_line(df, shark),
        lambda: _shark_industry_bar(df, shark),
        lambda: _deal_distribution(df, 'pie'),
        lambda: _shark_season_stacked(df, shark),
        lambda: _ask_vs_deal_scatter(df),
    ]
    return _run_builders(builders)

def _strategy_multi_seasons(df, filters):
    """Rule 8D: multiple seasons → comparison mode."""
    builders = [
        lambda: _multi_season_trend(df, filters['seasons']),
        lambda: _season_investment_grouped_bar(df),
        lambda: _stacked_area_growth(df, 'Selected Seasons'),
        lambda: _season_deal_stacked(df),
        lambda: _shark_investment_bar(df),
    ]
    return _run_builders(builders)

def _strategy_multi_sharks(df, filters):
    """Rule 8E: multiple sharks → comparison mode."""
    builders = [
        lambda: _shark_grouped_bar(df, filters['sharks']),
        lambda: _shark_industry_heatmap(df, filters['sharks']),
        lambda: _shark_season_stacked_bar_multi(df, filters['sharks']),
        lambda: _deal_distribution(df, 'donut'),
        lambda: _top_industries_ranking(df),
    ]
    return _run_builders(builders)

def _strategy_multi_industries(df, filters):
    """Rule 8F: multiple industries → comparison mode."""
    builders = [
        lambda: _industry_grouped_bar(df, filters['industries']),
        lambda: _stacked_area_growth(df, 'Selected Industries'),
        lambda: _top_industries_ranking(df),
        lambda: _shark_investment_bar(df),
        lambda: _deal_distribution(df, 'donut'),
    ]
    return _run_builders(builders)

def _strategy_overview(df, filters):
    """No filters → overview dashboard."""
    builders = [
        lambda: _pitches_deals_trend(df),
        lambda: _deal_distribution(df, 'donut'),
        lambda: _shark_investment_bar(df),
        lambda: _top_industries_ranking(df),
        lambda: _season_deal_stacked(df),
    ]
    return _run_builders(builders)


def _run_builders(builders, limit=5):
    """Execute builders, skip None results, enforce chart limit (Rule 9)."""
    blocks = []
    for fn in builders:
        if len(blocks) >= limit:
            break
        try:
            result = fn()
            if result is not None:
                blocks.append(result)
        except Exception as e:
            print(f'[data_engine] builder error: {e}')
    return blocks


# ═══════════════════════════════════════════════════════════════════════
#  PUBLIC API
# ═══════════════════════════════════════════════════════════════════════

def build_chart_data(df, filters):
    """
    Build context-aware chart data based on the 12-rule strategy engine.

    Args:
        df: Filtered DataFrame
        filters: dict with keys seasons, industries, sharks, got_deal

    Returns:
        dict with keys: chart_data (list), insights (list), mode (str)
    """
    if df.empty:
        return {
            'chart_data': [],
            'insights': ['No data matches the current filters.'],
            'mode': 'overview',
        }

    mode, category = _detect_mode(filters)

    # Choose strategy based on mode + category
    if mode == 'deep_dive':
        if category == 'seasons':
            charts = _strategy_single_season(df, filters)
        elif category == 'industries':
            charts = _strategy_single_industry(df, filters)
        elif category == 'sharks':
            charts = _strategy_single_shark(df, filters)
        else:
            charts = _strategy_overview(df, filters)
    elif mode == 'comparison':
        if category == 'seasons':
            charts = _strategy_multi_seasons(df, filters)
        elif category == 'sharks':
            charts = _strategy_multi_sharks(df, filters)
        elif category == 'industries':
            charts = _strategy_multi_industries(df, filters)
        else:
            charts = _strategy_overview(df, filters)
    else:
        charts = _strategy_overview(df, filters)

    insights = _generate_insights(df, mode, category, filters)

    return {
        'chart_data': charts,
        'insights': insights,
        'mode': mode,
    }
