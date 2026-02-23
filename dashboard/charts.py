"""
Interactive chart generation using Plotly
"""
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

# Dark theme configuration for Plotly
PLOTLY_TEMPLATE = {
    'layout': {
        'paper_bgcolor': '#1a1a2e',
        'plot_bgcolor': '#2d2d3f',
        'font': {'color': '#e2e8f0', 'family': 'Inter, sans-serif'},
        'xaxis': {
            'gridcolor': '#3d3d5f',
            'linecolor': '#e2e8f0',
            'zerolinecolor': '#3d3d5f'
        },
        'yaxis': {
            'gridcolor': '#3d3d5f',
            'linecolor': '#e2e8f0',
            'zerolinecolor': '#3d3d5f'
        },
        'hovermode': 'closest',
        'hoverlabel': {
            'bgcolor': '#252540',
            'font': {'color': '#e2e8f0', 'size': 13},
            'bordercolor': '#6366f1'
        }
    }
}

# Color palette
COLORS = {
    'primary': '#6366f1',
    'secondary': '#8b5cf6',
    'accent': '#06b6d4',
    'success': '#10b981',
    'warning': '#f59e0b',
    'danger': '#ef4444'
}

COLOR_SEQUENCE = ['#6366f1', '#8b5cf6', '#06b6d4', '#10b981', '#f59e0b', '#ef4444', '#ec4899', '#14b8a6']


def deals_by_season_chart(df, return_fig=False):
    """Create interactive bar chart of deals by season"""
    if df.empty:
        fig = go.Figure()
        fig.update_layout(
            title='Pitches vs Deals by Season',
            annotations=[dict(text='No data available', x=0.5, y=0.5, showarrow=False, font=dict(color='#e2e8f0'))],
            **PLOTLY_TEMPLATE['layout'],
            height=450
        )
        if return_fig:
            return fig
        return fig.to_html(full_html=False, include_plotlyjs=False, div_id='chart-deals-season', config={'displayModeBar': False, 'responsive': True})

    season_data = df.groupby('Season Number').agg({
        'Got Deal': ['count', 'sum']
    }).reset_index()
    season_data.columns = ['Season', 'Total Pitches', 'Deals Made']
    season_data = season_data.sort_values('Season')  # Ensure sorted
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=season_data['Season'],
        y=season_data['Total Pitches'],
        name='Total Pitches',
        marker_color=COLORS['primary'],
        hovertemplate='<b>Season %{x}</b><br>Total Pitches: %{y}<extra></extra>'
    ))
    
    fig.add_trace(go.Bar(
        x=season_data['Season'],
        y=season_data['Deals Made'],
        name='Deals Made',
        marker_color=COLORS['success'],
        hovertemplate='<b>Season %{x}</b><br>Deals Made: %{y}<extra></extra>'
    ))
    
    # Get actual min/max seasons from data
    min_season = int(season_data['Season'].min())
    max_season = int(season_data['Season'].max())
    
    fig.update_layout(
        title=dict(
            text='Pitches vs Deals by Season',
            font=dict(size=18)
        ),
        xaxis_title='Season',
        yaxis_title='Count',
        barmode='group',
        bargap=0.15,
        bargroupgap=0.05,
        paper_bgcolor='#1a1a2e',
        plot_bgcolor='#2d2d3f',
        font=dict(color='#e2e8f0', family='Inter, sans-serif'),
        height=450,
        margin=dict(l=60, r=40, t=80, b=60),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='center',
            x=0.5,
            font=dict(size=12)
        ),
        hovermode='closest',
        hoverlabel=dict(
            bgcolor='#252540',
            font=dict(color='#e2e8f0', size=13),
            bordercolor='#6366f1'
        )
    )
    
    fig.update_xaxes(
        tickmode='linear',
        tick0=min_season,
        dtick=1,
        range=[min_season - 0.5, max_season + 0.5],
        tickfont=dict(size=10),
        gridcolor='#3d3d5f',
        linecolor='#e2e8f0',
        zerolinecolor='#3d3d5f'
    )
    
    fig.update_yaxes(
        tickfont=dict(size=11),
        gridcolor='#3d3d5f',
        linecolor='#e2e8f0',
        zerolinecolor='#3d3d5f'
    )
    
    if return_fig:
        return fig
        
    return fig.to_html(full_html=False, include_plotlyjs=False, div_id='chart-deals-season', config={'displayModeBar': False, 'responsive': True})


def deals_by_industry_chart(df, return_fig=False):
    """Create interactive horizontal bar chart of deals by industry"""
    if df.empty:
        fig = go.Figure()
        fig.update_layout(
            title='Top 10 Industries by Deals',
            annotations=[dict(text='No data available', x=0.5, y=0.5, showarrow=False, font=dict(color='#e2e8f0'))],
            **PLOTLY_TEMPLATE['layout'],
            height=450
        )
        if return_fig:
            return fig
        return fig.to_html(full_html=False, include_plotlyjs=False, div_id='chart-deals-industry', config={'displayModeBar': False, 'responsive': True})

    industry_deals = df[df['Got Deal'] == 1].groupby('Industry').size().sort_values(ascending=True).tail(10)
    
    if industry_deals.empty:
        fig = go.Figure()
        fig.update_layout(
            title='Top 10 Industries by Deals',
            annotations=[dict(text='No deals found', x=0.5, y=0.5, showarrow=False, font=dict(color='#e2e8f0'))],
            **PLOTLY_TEMPLATE['layout'],
            height=450
        )
    else:
        fig = go.Figure(go.Bar(
            x=industry_deals.values.tolist(),
            y=industry_deals.index.tolist(),
            orientation='h',
            marker_color=COLOR_SEQUENCE,
            hovertemplate='<b>%{y}</b><br>Deals: %{x}<extra></extra>'
        ))
    
    fig.update_layout(
        title='Top 10 Industries by Deals',
        xaxis_title='Number of Deals',
        yaxis_title='',
        **PLOTLY_TEMPLATE['layout'],
        height=450,
        margin=dict(l=150, r=50, t=60, b=50)
    )
    
    if return_fig:
        return fig
        
    return fig.to_html(full_html=False, include_plotlyjs=False, div_id='chart-deals-industry', config={'displayModeBar': False, 'responsive': True})


def investment_by_shark_chart(df, return_fig=False):
    """Create interactive bar chart of total investment by shark"""
    if df.empty:
        fig = go.Figure()
        fig.update_layout(
            title='Total Investment by Shark',
            annotations=[dict(text='No data available', x=0.5, y=0.5, showarrow=False, font=dict(color='#e2e8f0'))],
            **PLOTLY_TEMPLATE['layout'],
            height=400
        )
        if return_fig:
            return fig
        return fig.to_html(full_html=False, include_plotlyjs=False, div_id='chart-investment-shark', config={'displayModeBar': False, 'responsive': True})

    sharks = {
        'Barbara Corcoran': 'Barbara Corcoran Investment Amount',
        'Mark Cuban': 'Mark Cuban Investment Amount',
        'Lori Greiner': 'Lori Greiner Investment Amount',
        'Robert Herjavec': 'Robert Herjavec Investment Amount',
        'Daymond John': 'Daymond John Investment Amount',
        'Kevin O\'Leary': 'Kevin O Leary Investment Amount'
    }
    
    investments = []
    labels = []
    for label, col in sharks.items():
        if col in df.columns:
            total = df[col].sum() / 1_000_000  # Convert to millions
            if pd.notna(total):
                investments.append(total)
                labels.append(label)
    
    fig = go.Figure(go.Bar(
        x=labels,
        y=investments,
        marker_color=COLOR_SEQUENCE[:len(labels)],
        hovertemplate='<b>%{x}</b><br>Total Investment: $%{y:.2f}M<extra></extra>'
    ))
    
    fig.update_layout(
        title='Total Investment by Shark',
        xaxis_title='',
        yaxis_title='Total Investment (Millions $)',
        **PLOTLY_TEMPLATE['layout'],
        height=400,
        margin=dict(l=50, r=50, t=60, b=50)
    )
    
    if return_fig:
        return fig
    
    return fig.to_html(full_html=False, include_plotlyjs=False, div_id='chart-investment-shark', config={'displayModeBar': False, 'responsive': True})


def deal_success_rate_chart(df, return_fig=False):
    """Create interactive pie chart of deal success rate"""
    if df.empty:
        fig = go.Figure()
        fig.update_layout(
            title='Deal Success Rate',
            annotations=[dict(text='No data available', x=0.5, y=0.5, showarrow=False, font=dict(color='#e2e8f0'))],
            **PLOTLY_TEMPLATE['layout'],
            height=400
        )
        if return_fig:
            return fig
        return fig.to_html(full_html=False, include_plotlyjs=False, div_id='chart-success-rate', config={'displayModeBar': False, 'responsive': True})

    deals = df['Got Deal'].sum()
    no_deals = len(df) - deals
    
    fig = go.Figure(go.Pie(
        labels=['Got Deal', 'No Deal'],
        values=[deals, no_deals],
        marker_colors=[COLORS['success'], COLORS['danger']],
        hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>',
        textinfo='label+percent',
        textfont_size=14,
        hole=0.3
    ))
    
    fig.update_layout(
        title='Deal Success Rate',
        **PLOTLY_TEMPLATE['layout'],
        height=400,
        margin=dict(l=50, r=50, t=60, b=50)
    )
    
    if return_fig:
        return fig
        
    return fig.to_html(full_html=False, include_plotlyjs=False, div_id='chart-success-rate', config={'displayModeBar': False, 'responsive': True})


def top_industries_investment_chart(df, return_fig=False):
    """Create interactive bar chart of top industries by investment amount"""
    if df.empty:
        fig = go.Figure()
        fig.update_layout(
            title='Top 10 Industries by Investment',
            annotations=[dict(text='No data available', x=0.5, y=0.5, showarrow=False, font=dict(color='#e2e8f0'))],
            **PLOTLY_TEMPLATE['layout'],
            height=450
        )
        if return_fig:
            return fig
        return fig.to_html(full_html=False, include_plotlyjs=False, div_id='chart-top-industries', config={'displayModeBar': False, 'responsive': True})

    deals_df = df[df['Got Deal'] == 1].copy()
    
    if deals_df.empty:
         fig = go.Figure()
         fig.update_layout(
            title='Top 10 Industries by Investment',
            annotations=[dict(text='No investment data', x=0.5, y=0.5, showarrow=False, font=dict(color='#e2e8f0'))],
            **PLOTLY_TEMPLATE['layout'],
            height=450
        )
    else:
        industry_investment = deals_df.groupby('Industry')['Total Deal Amount'].sum().sort_values(ascending=True).tail(10)
        industry_investment = industry_investment / 1_000_000  # Convert to millions
        
        fig = go.Figure(go.Bar(
            x=industry_investment.values.tolist(),
            y=industry_investment.index.tolist(),
            orientation='h',
            marker_color=COLOR_SEQUENCE,
            hovertemplate='<b>%{y}</b><br>Total Investment: $%{x:.2f}M<extra></extra>'
        ))
    
    fig.update_layout(
        title='Top 10 Industries by Investment',
        xaxis_title='Total Investment (Millions $)',
        yaxis_title='',
        **PLOTLY_TEMPLATE['layout'],
        height=450,
        margin=dict(l=150, r=50, t=60, b=50)
    )
    
    if return_fig:
        return fig
        
    return fig.to_html(full_html=False, include_plotlyjs=False, div_id='chart-top-industries', config={'displayModeBar': False, 'responsive': True})


def avg_deal_by_season_chart(df, return_fig=False):
    """Create interactive line chart of average deal amount by season"""
    if df.empty:
        fig = go.Figure()
        fig.update_layout(
            title='Average Deal Amount by Season',
            annotations=[dict(text='No data available', x=0.5, y=0.5, showarrow=False, font=dict(color='#e2e8f0'))],
            **PLOTLY_TEMPLATE['layout'],
            height=400
        )
        if return_fig:
            return fig
        return fig.to_html(full_html=False, include_plotlyjs=False, div_id='chart-avg-deal', config={'displayModeBar': False, 'responsive': True})

    deals_df = df[df['Got Deal'] == 1]
    
    if deals_df.empty:
        fig = go.Figure()
        fig.update_layout(
            title='Average Deal Amount by Season',
            annotations=[dict(text='No deals found', x=0.5, y=0.5, showarrow=False, font=dict(color='#e2e8f0'))],
            **PLOTLY_TEMPLATE['layout'],
            height=400
        )
    else:
        avg_by_season = deals_df.groupby('Season Number')['Total Deal Amount'].mean() / 1000  # Convert to thousands
        
        fig = go.Figure(go.Scatter(
            x=avg_by_season.index.tolist(),
            y=avg_by_season.values.tolist(),
            mode='lines+markers',
            line=dict(color=COLORS['accent'], width=3),
            marker=dict(size=10, color=COLORS['primary']),
            fill='tozeroy',
            fillcolor='rgba(6, 182, 212, 0.2)',
            hovertemplate='<b>Season %{x}</b><br>Avg Deal: $%{y:.2f}K<extra></extra>'
        ))
    
    fig.update_layout(
        title='Average Deal Amount by Season',
        xaxis_title='Season',
        yaxis_title='Average Deal Amount (Thousands $)',
        **PLOTLY_TEMPLATE['layout'],
        height=400,
        margin=dict(l=50, r=50, t=60, b=50)
    )
    
    if return_fig:
        return fig
        
    return fig.to_html(full_html=False, include_plotlyjs=False, div_id='chart-avg-deal', config={'displayModeBar': False, 'responsive': True})


def valuation_comparison_chart(df, return_fig=False):
    """Create interactive line chart comparing original vs deal valuation by season"""
    if df.empty:
        fig = go.Figure()
        fig.update_layout(
            title='Valuation Comparison Trend',
            annotations=[dict(text='No data available', x=0.5, y=0.5, showarrow=False, font=dict(color='#e2e8f0'))],
            **PLOTLY_TEMPLATE['layout'],
            height=400
        )
        if return_fig:
            return fig
        return fig.to_html(full_html=False, include_plotlyjs=False, div_id='chart-valuation-comparison', config={'displayModeBar': False, 'responsive': True})

    deals_df = df[df['Got Deal'] == 1].copy()
    
    fig = go.Figure()
    
    if not deals_df.empty:
        valuation_by_season = deals_df.groupby('Season Number').agg({
            'Valuation Requested': 'mean',
            'Deal Valuation': 'mean'
        }).reset_index()
        valuation_by_season = valuation_by_season.sort_values('Season Number')
        
        fig.add_trace(go.Scatter(
            x=valuation_by_season['Season Number'].tolist(),
            y=(valuation_by_season['Valuation Requested'] / 1_000_000).tolist(),
            mode='lines+markers',
            name='Requested Valuation',
            line=dict(color=COLORS['primary'], width=3),
            marker=dict(size=10),
            hovertemplate='<b>Season %{x}</b><br>Requested: $%{y:.2f}M<extra></extra>'
        ))
        
        fig.add_trace(go.Scatter(
            x=valuation_by_season['Season Number'].tolist(),
            y=(valuation_by_season['Deal Valuation'] / 1_000_000).tolist(),
            mode='lines+markers',
            name='Deal Valuation',
            line=dict(color=COLORS['success'], width=3),
            marker=dict(size=10),
            hovertemplate='<b>Season %{x}</b><br>Deal: $%{y:.2f}M<extra></extra>'
        ))
    else:
         fig.update_layout(annotations=[dict(text='No deal data available', x=0.5, y=0.5, showarrow=False, font=dict(color='#e2e8f0'))])
    
    fig.update_layout(
        title='Valuation Comparison Trend',
        xaxis_title='Season',
        yaxis_title='Valuation (Millions $)',
        **PLOTLY_TEMPLATE['layout'],
        height=400,
        margin=dict(l=60, r=40, t=60, b=50),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='center', x=0.5)
    )
    
    if return_fig:
        return fig
        
    return fig.to_html(full_html=False, include_plotlyjs=False, div_id='chart-valuation-comparison', config={'displayModeBar': False, 'responsive': True})


def equity_trend_chart(df, return_fig=False):
    """Create interactive line chart comparing original vs deal equity by season"""
    if df.empty:
        fig = go.Figure()
        fig.update_layout(
            title='Original vs Deal Equity Trend',
            annotations=[dict(text='No data available', x=0.5, y=0.5, showarrow=False, font=dict(color='#e2e8f0'))],
            **PLOTLY_TEMPLATE['layout'],
            height=400
        )
        if return_fig:
            return fig
        return fig.to_html(full_html=False, include_plotlyjs=False, div_id='chart-equity-trend', config={'displayModeBar': False, 'responsive': True})

    deals_df = df[df['Got Deal'] == 1].copy()
    
    fig = go.Figure()
    
    if not deals_df.empty:
        equity_by_season = deals_df.groupby('Season Number').agg({
            'Original Offered Equity': 'mean',
            'Total Deal Equity': 'mean'
        }).reset_index()
        equity_by_season = equity_by_season.sort_values('Season Number')
        
        fig.add_trace(go.Scatter(
            x=equity_by_season['Season Number'].tolist(),
            y=equity_by_season['Original Offered Equity'].tolist(),
            mode='lines+markers',
            name='Original Equity Offered',
            line=dict(color=COLORS['warning'], width=3),
            marker=dict(size=10),
            fill='tozeroy',
            fillcolor='rgba(245, 158, 11, 0.1)',
            hovertemplate='<b>Season %{x}</b><br>Offered: %{y:.1f}%<extra></extra>'
        ))
        
        fig.add_trace(go.Scatter(
            x=equity_by_season['Season Number'].tolist(),
            y=equity_by_season['Total Deal Equity'].tolist(),
            mode='lines+markers',
            name='Deal Equity',
            line=dict(color=COLORS['accent'], width=3),
            marker=dict(size=10),
            fill='tozeroy',
            fillcolor='rgba(6, 182, 212, 0.1)',
            hovertemplate='<b>Season %{x}</b><br>Deal: %{y:.1f}%<extra></extra>'
        ))
    else:
        fig.update_layout(annotations=[dict(text='No deal data available', x=0.5, y=0.5, showarrow=False, font=dict(color='#e2e8f0'))])
    
    fig.update_layout(
        title='Original vs Deal Equity Trend',
        xaxis_title='Season',
        yaxis_title='Equity (%)',
        **PLOTLY_TEMPLATE['layout'],
        height=400,
        margin=dict(l=60, r=40, t=60, b=50),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='center', x=0.5)
    )
    
    if return_fig:
        return fig
        
    return fig.to_html(full_html=False, include_plotlyjs=False, div_id='chart-equity-trend', config={'displayModeBar': False, 'responsive': True})


def shark_investment_trend_chart(df, shark_name, return_fig=False):
    """Create interactive line chart of shark's investment trend by season"""
    if df.empty:
        fig = go.Figure()
        fig.update_layout(
            title=f'{shark_name} Investment Trend' if shark_name else 'Shark Investment Trend',
            annotations=[dict(text='No data available', x=0.5, y=0.5, showarrow=False, font=dict(color='#e2e8f0'))],
            **PLOTLY_TEMPLATE['layout'],
            height=400
        )
        if return_fig:
            return fig
        return fig.to_html(full_html=False, include_plotlyjs=False, div_id='chart-shark-investment', config={'displayModeBar': False, 'responsive': True})
    
    # Handle All Sharks case
    if shark_name == 'All Sharks':
        deals_df = df[df['Got Deal'] == 1].copy()
        if not deals_df.empty and 'Total Deal Amount' in deals_df.columns:
            investment_by_season = deals_df.groupby('Season Number')['Total Deal Amount'].sum() / 1_000_000
        else:
            investment_by_season = pd.Series(dtype=float)
            
        investment_by_season = investment_by_season.sort_index()
        
        fig = go.Figure(go.Scatter(
            x=investment_by_season.index.tolist(),
            y=investment_by_season.values.tolist(),
            mode='lines+markers',
            line=dict(color=COLORS['secondary'], width=3),
            marker=dict(size=12, color=COLORS['primary']),
            fill='tozeroy',
            fillcolor='rgba(139, 92, 246, 0.2)',
            hovertemplate='<b>Season %{x}</b><br>Investment: $%{y:.2f}M<extra></extra>'
        ))
        
        fig.update_layout(
            title='All Sharks Investment Trend',
            xaxis_title='Season',
            yaxis_title='Total Investment (Millions $)',
            **PLOTLY_TEMPLATE['layout'],
            height=400,
            margin=dict(l=60, r=40, t=60, b=50)
        )
        
        if return_fig:
            return fig
        return fig.to_html(full_html=False, include_plotlyjs=False, div_id='chart-shark-investment', config={'displayModeBar': False, 'responsive': True})
    
    shark_col = f"{shark_name} Investment Amount"
    
    if shark_col not in df.columns:
        # Return empty chart
        fig = go.Figure()
        fig.update_layout(
            title=f'{shark_name} Investment Trend',
            annotations=[dict(text='No data available', x=0.5, y=0.5, showarrow=False, font=dict(color='#e2e8f0'))],
            **PLOTLY_TEMPLATE['layout'],
            height=400
        )
        if return_fig:
            return fig
        return fig.to_html(full_html=False, include_plotlyjs=False, div_id='chart-shark-investment', config={'displayModeBar': False, 'responsive': True})
    
    shark_df = df[df[shark_col].notna() & (df[shark_col] > 0)].copy()
    if shark_df.empty:
        investment_by_season = pd.Series(dtype=float)
    else:
        investment_by_season = shark_df.groupby('Season Number')[shark_col].sum() / 1_000_000
        
    investment_by_season = investment_by_season.sort_index()
    
    fig = go.Figure(go.Scatter(
        x=investment_by_season.index.tolist(),
        y=investment_by_season.values.tolist(),
        mode='lines+markers',
        line=dict(color=COLORS['secondary'], width=3),
        marker=dict(size=12, color=COLORS['primary']),
        fill='tozeroy',
        fillcolor='rgba(139, 92, 246, 0.2)',
        hovertemplate='<b>Season %{x}</b><br>Investment: $%{y:.2f}M<extra></extra>'
    ))
    
    fig.update_layout(
        title=f'{shark_name} Investment Trend',
        xaxis_title='Season',
        yaxis_title='Total Investment (Millions $)',
        **PLOTLY_TEMPLATE['layout'],
        height=400,
        margin=dict(l=60, r=40, t=60, b=50)
    )
    
    if return_fig:
        return fig
    
    return fig.to_html(full_html=False, include_plotlyjs=False, div_id='chart-shark-investment', config={'displayModeBar': False, 'responsive': True})


def top_funded_startups_chart(df, limit=10, return_fig=False):
    """Create horizontal bar chart of top funded startups"""
    if df.empty:
        fig = go.Figure()
        fig.update_layout(
            title=f'Top {limit} Funded Startups',
            annotations=[dict(text='No data available', x=0.5, y=0.5, showarrow=False, font=dict(color='#e2e8f0'))],
            **PLOTLY_TEMPLATE['layout'],
            height=450
        )
        if return_fig:
            return fig
        return fig.to_html(full_html=False, include_plotlyjs=False, div_id='chart-top-startups', config={'displayModeBar': False, 'responsive': True})

    deals_df = df[df['Got Deal'] == 1].copy()
    
    if deals_df.empty:
         fig = go.Figure()
         fig.update_layout(
            title=f'Top {limit} Funded Startups',
            annotations=[dict(text='No deal data available', x=0.5, y=0.5, showarrow=False, font=dict(color='#e2e8f0'))],
            **PLOTLY_TEMPLATE['layout'],
            height=450
        )
    else:
        top_startups = deals_df.nlargest(limit, 'Total Deal Amount')[['Startup Name', 'Total Deal Amount', 'Industry']]
        top_startups = top_startups.sort_values('Total Deal Amount', ascending=True)
        
        fig = go.Figure(go.Bar(
            x=(top_startups['Total Deal Amount'] / 1_000_000).tolist(),
            y=top_startups['Startup Name'].tolist(),
            orientation='h',
            marker_color=COLOR_SEQUENCE,
            text=[f"${v/1_000_000:.2f}M" for v in top_startups['Total Deal Amount'].tolist()],
            textposition='outside',
            hovertemplate='<b>%{y}</b><br>Investment: $%{x:.2f}M<extra></extra>'
        ))
    
    fig.update_layout(
        title=f'Top {limit} Funded Startups',
        xaxis_title='Investment Amount (Millions $)',
        yaxis_title='',
        **PLOTLY_TEMPLATE['layout'],
        height=450,
        margin=dict(l=200, r=80, t=60, b=50)
    )
    
    if return_fig:
        return fig
        
    return fig.to_html(full_html=False, include_plotlyjs=False, div_id='chart-top-startups', config={'displayModeBar': False, 'responsive': True})


def industry_equity_chart(df, return_fig=False):
    """Create pie chart of average equity by industry"""
    if df.empty:
        fig = go.Figure()
        fig.update_layout(
            title='Industry-wise Average Equity',
            annotations=[dict(text='No data available', x=0.5, y=0.5, showarrow=False, font=dict(color='#e2e8f0'))],
            **PLOTLY_TEMPLATE['layout'],
            height=400
        )
        if return_fig:
            return fig
        return fig.to_html(full_html=False, include_plotlyjs=False, div_id='chart-industry-equity', config={'displayModeBar': False, 'responsive': True})

    deals_df = df[df['Got Deal'] == 1].copy()
    
    if deals_df.empty:
        fig = go.Figure()
        fig.update_layout(
            title='Industry-wise Average Equity',
            annotations=[dict(text='No deal data available', x=0.5, y=0.5, showarrow=False, font=dict(color='#e2e8f0'))],
            **PLOTLY_TEMPLATE['layout'],
            height=400
        )
    else:
        industry_equity = deals_df.groupby('Industry')['Total Deal Equity'].mean().sort_values(ascending=False).head(8)
        
        fig = go.Figure(go.Pie(
            labels=industry_equity.index.tolist(),
            values=industry_equity.values.tolist(),
            marker_colors=COLOR_SEQUENCE,
            hovertemplate='<b>%{label}</b><br>Avg Equity: %{value:.1f}%<br>Share: %{percent}<extra></extra>',
            textinfo='label+percent',
            textfont_size=11,
            hole=0.4
        ))
    
    fig.update_layout(
        title='Industry-wise Average Equity',
        **PLOTLY_TEMPLATE['layout'],
        height=400,
        margin=dict(l=50, r=50, t=60, b=50)
    )
    
    if return_fig:
        return fig
        
    return fig.to_html(full_html=False, include_plotlyjs=False, div_id='chart-industry-equity', config={'displayModeBar': False, 'responsive': True})


def industry_funding_chart(df, return_fig=False):
    """Create horizontal bar chart of total funding by industry"""
    if df.empty:
        fig = go.Figure()
        fig.update_layout(
            title='Industry-wise Total Funding',
            annotations=[dict(text='No data available', x=0.5, y=0.5, showarrow=False, font=dict(color='#e2e8f0'))],
            **PLOTLY_TEMPLATE['layout'],
            height=450
        )
        if return_fig:
            return fig
        return fig.to_html(full_html=False, include_plotlyjs=False, div_id='chart-industry-funding', config={'displayModeBar': False, 'responsive': True})

    deals_df = df[df['Got Deal'] == 1].copy()
    
    if deals_df.empty:
        fig = go.Figure()
        fig.update_layout(
            title='Industry-wise Total Funding',
            annotations=[dict(text='No deal data available', x=0.5, y=0.5, showarrow=False, font=dict(color='#e2e8f0'))],
            **PLOTLY_TEMPLATE['layout'],
            height=450
        )
    else:
        industry_funding = deals_df.groupby('Industry')['Total Deal Amount'].sum().sort_values(ascending=True).tail(10)
        industry_funding = industry_funding / 1_000_000
        
        fig = go.Figure(go.Bar(
            x=industry_funding.values.tolist(),
            y=industry_funding.index.tolist(),
            orientation='h',
            marker_color=COLOR_SEQUENCE,
            hovertemplate='<b>%{y}</b><br>Total Funding: $%{x:.2f}M<extra></extra>'
        ))
    
    fig.update_layout(
        title='Industry-wise Total Funding',
        xaxis_title='Total Funding (Millions $)',
        yaxis_title='',
        **PLOTLY_TEMPLATE['layout'],
        height=450,
        margin=dict(l=150, r=50, t=60, b=50)
    )
    
    if return_fig:
        return fig
        
    return fig.to_html(full_html=False, include_plotlyjs=False, div_id='chart-industry-funding', config={'displayModeBar': False, 'responsive': True})
