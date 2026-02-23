"""
Dashboard views for Shark Tank Analysis
"""
import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .utils import load_data, get_filter_options, filter_data, get_stats
from .charts import (
    deals_by_season_chart,
    deals_by_industry_chart,
    investment_by_shark_chart,
    deal_success_rate_chart,
    top_industries_investment_chart,
    avg_deal_by_season_chart,
    valuation_comparison_chart,
    equity_trend_chart,
    shark_investment_trend_chart,
    top_funded_startups_chart,
    industry_equity_chart,
    industry_funding_chart
)


def dashboard(request):
    """Main dashboard view — serves the initial page with filter options + charts"""
    df = load_data()
    filter_options = get_filter_options()
    
    # Initial load: no filters applied, show all data
    stats = get_stats(df)
    
    # Generate initial charts as HTML for SSR
    charts = {
        'deals_by_season': deals_by_season_chart(df),
        'deals_by_industry': deals_by_industry_chart(df),
        'investment_by_shark': investment_by_shark_chart(df),
        'deal_success_rate': deal_success_rate_chart(df),
        'top_industries': top_industries_investment_chart(df),
        'avg_deal_by_season': avg_deal_by_season_chart(df),
    }
    
    context = {
        'filter_options': filter_options,
        'stats': stats,
        'charts': charts,
    }
    
    return render(request, 'dashboard/index.html', context)


@csrf_exempt
def api_filter(request):
    """AJAX endpoint: returns filtered stats + Plotly chart JSON for dynamic updates (POST only)"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)

    df = load_data()

    # Parse JSON body from POST request
    try:
        body = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'error': 'Invalid JSON body'}, status=400)

    seasons = body.get('seasons', [])
    industries = body.get('industries', [])
    sharks = body.get('sharks', [])
    got_deal = body.get('got_deal', 'all')

    # Apply filters
    filtered_df = filter_data(
        df,
        seasons=seasons if seasons else None,
        industries=industries if industries else None,
        sharks=sharks if sharks else None,
        got_deal=got_deal,
    )

    # Calculate stats
    stats = get_stats(filtered_df)

    # Build context-aware chart data (strategy engine)
    from .data_engine import build_chart_data
    got_deal_val = got_deal
    engine_result = build_chart_data(filtered_df, {
        'seasons': seasons,
        'industries': industries,
        'sharks': sharks,
        'got_deal': got_deal_val,
    })

    return JsonResponse({
        'stats': stats,
        'chart_data': engine_result['chart_data'],
        'insights': engine_result['insights'],
        'mode': engine_result['mode'],
    })


def get_shark_stats(df, shark_name):
    """Calculate statistics specific to a shark or all sharks"""
    if shark_name == 'All Sharks':
        # Aggregate stats for all sharks
        deals_df = df[df['Got Deal'] == 1]
        total_deals = len(deals_df)
        total_pitches = len(df)
        success_rate = (total_deals / total_pitches * 100) if total_pitches > 0 else 0
        total_investment = deals_df['Total Deal Amount'].sum() if 'Total Deal Amount' in df.columns else 0
        seasons = deals_df['Season Number'].nunique()
        avg_deal_per_season = total_investment / seasons if seasons > 0 else 0
        
        return {
            'total_deals': int(total_deals),
            'success_rate': round(success_rate, 1),
            'total_investment': total_investment if total_investment else 0,
            'avg_deal_per_season': avg_deal_per_season if avg_deal_per_season else 0
        }
    
    shark_col = f"{shark_name} Investment Amount"
    
    if shark_col not in df.columns:
        return {
            'total_deals': 0,
            'success_rate': 0,
            'total_investment': 0,
            'avg_deal_per_season': 0
        }
    
    # Filter for deals where this shark invested
    shark_df = df[(df[shark_col].notna()) & (df[shark_col] > 0)]
    
    total_deals = len(shark_df)
    total_pitches = len(df)
    success_rate = (total_deals / total_pitches * 100) if total_pitches > 0 else 0
    total_investment = shark_df[shark_col].sum()
    
    # Average deal per season
    seasons_invested = shark_df['Season Number'].nunique()
    avg_deal_per_season = total_investment / seasons_invested if seasons_invested > 0 else 0
    
    return {
        'total_deals': int(total_deals),
        'success_rate': round(success_rate, 1),
        'total_investment': total_investment if total_investment else 0,
        'avg_deal_per_season': avg_deal_per_season if avg_deal_per_season else 0
    }


def shark_analysis(request, shark_name):
    """Shark analysis page view"""
    df = load_data()
    filter_options = get_filter_options()
    
    # Filter data for this shark or get all deals
    if shark_name == 'All Sharks':
        filtered_df = df[df['Got Deal'] == 1]
    else:
        shark_col = f"{shark_name} Investment Amount"
        if shark_col in df.columns:
            filtered_df = df[(df[shark_col].notna()) & (df[shark_col] > 0)]
        else:
            filtered_df = df.head(0)  # Empty dataframe
    
    # Get shark-specific stats
    stats = get_shark_stats(df, shark_name)
    
    # Generate all charts
    charts = {
        'deals_by_season': deals_by_season_chart(filtered_df),
        'valuation_comparison': valuation_comparison_chart(filtered_df),
        'equity_trend': equity_trend_chart(filtered_df),
        'shark_investment_trend': shark_investment_trend_chart(df, shark_name),
        'top_startups': top_funded_startups_chart(filtered_df),
        'industry_equity': industry_equity_chart(filtered_df),
        'industry_funding': industry_funding_chart(filtered_df),
    }
    
    context = {
        'shark_name': shark_name,
        'sharks': filter_options['sharks'],
        'stats': stats,
        'charts': charts,
    }
    
    return render(request, 'dashboard/shark_analysis.html', context)
