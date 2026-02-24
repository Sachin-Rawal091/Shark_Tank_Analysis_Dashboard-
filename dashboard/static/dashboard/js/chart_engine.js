(function() {
    'use strict';

    // ── Dark Theme Palette ─────────────────────────────────────────────
    const COLORS   = ['#6366f1','#8b5cf6','#06b6d4','#10b981','#f59e0b','#ef4444','#ec4899','#14b8a6','#a855f7','#3b82f6'];
    const BG       = '#1a1a2e';
    const PLOT_BG  = '#2d2d3f';
    const GRID     = '#3d3d5f';
    const TEXT     = '#e2e8f0';
    const FONT     = 'Inter, sans-serif';

    function base(title, extra) {
        return Object.assign({
            title:  { text: title, font: { size: 16, color: TEXT, family: FONT } },
            paper_bgcolor: BG, plot_bgcolor: PLOT_BG,
            font:   { color: TEXT, family: FONT, size: 12 },
            margin: { l: 60, r: 30, t: 55, b: 50 },
            height: 400,
            hovermode: 'closest',
            hoverlabel: { bgcolor: '#252540', font: { color: TEXT, size: 12 }, bordercolor: '#6366f1' },
            legend: { orientation: 'h', yanchor: 'bottom', y: 1.02, xanchor: 'center', x: 0.5, font: { size: 11 } },
        }, extra || {});
    }

    function ax(extra) {
        return Object.assign({ gridcolor: GRID, linecolor: TEXT, zerolinecolor: GRID, tickfont: { size: 11 } }, extra || {});
    }

    // ── ChartEngine: hint → Plotly {data, layout} ──────────────────────

    const ChartEngine = {

        line(block) {
            const traces = block.datasets.map((ds, i) => ({
                x: block.labels, y: ds.values, name: ds.name,
                type: 'scatter', mode: 'lines+markers',
                line: { color: COLORS[i % COLORS.length], width: 3, shape: 'spline' },
                marker: { size: 7 },
                hovertemplate: '<b>%{x}</b><br>' + ds.name + ': %{y:,.0f}<extra></extra>',
            }));
            return { data: traces, layout: base(block.title, { xaxis: ax(), yaxis: ax() }) };
        },

        area(block) {
            const traces = block.datasets.map((ds, i) => ({
                x: block.labels, y: ds.values, name: ds.name,
                type: 'scatter', mode: 'lines', fill: 'tozeroy',
                line: { color: COLORS[i % COLORS.length], width: 2, shape: 'spline' },
                hovertemplate: '<b>%{x}</b><br>' + ds.name + ': %{y:,.0f}<extra></extra>',
            }));
            return { data: traces, layout: base(block.title, { xaxis: ax(), yaxis: ax() }) };
        },

        multi_line(block) {
            const traces = block.datasets.map((ds, i) => ({
                x: block.labels, y: ds.values, name: ds.name,
                type: 'scatter', mode: 'lines+markers',
                line: { color: COLORS[i % COLORS.length], width: 3 },
                marker: { size: 6 },
                hovertemplate: '<b>%{x}</b><br>' + ds.name + ': %{y:,.0f}<extra></extra>',
            }));
            return { data: traces, layout: base(block.title, { xaxis: ax(), yaxis: ax() }) };
        },

        stacked_area(block) {
            const traces = block.datasets.map((ds, i) => ({
                x: block.labels, y: ds.values, name: ds.name,
                type: 'scatter', mode: 'lines',
                fill: i === 0 ? 'tozeroy' : 'tonexty',
                line: { color: COLORS[i % COLORS.length], width: 1 },
                hovertemplate: '<b>%{x}</b><br>' + ds.name + ': %{y:,.0f}<extra></extra>',
            }));
            return { data: traces, layout: base(block.title, { xaxis: ax(), yaxis: ax() }) };
        },

        bar(block) {
            const traces = block.datasets.map((ds, i) => ({
                x: block.labels, y: ds.values, name: ds.name,
                type: 'bar',
                marker: { color: COLORS[i % COLORS.length], opacity: 0.9 },
                hovertemplate: '<b>%{x}</b><br>' + ds.name + ': %{y:,.0f}<extra></extra>',
            }));
            return { data: traces, layout: base(block.title, { barmode: 'group', bargap: 0.3, xaxis: ax(), yaxis: ax({ title: 'Amount' }) }) };
        },

        grouped_bar(block) {
            const traces = block.datasets.map((ds, i) => ({
                x: block.labels, y: ds.values, name: ds.name,
                type: 'bar',
                marker: { color: COLORS[i % COLORS.length], opacity: 0.9 },
                hovertemplate: '<b>%{x}</b><br>' + ds.name + ': %{y:,.0f}<extra></extra>',
            }));
            return { data: traces, layout: base(block.title, { barmode: 'group', bargap: 0.2, xaxis: ax({ tickangle: -30 }), yaxis: ax() }) };
        },

        horizontal_bar(block) {
            const ds = block.datasets[0];
            const trace = {
                y: block.labels, x: ds.values, name: ds.name,
                type: 'bar', orientation: 'h',
                marker: { color: COLORS.slice(0, block.labels.length).reverse() },
                hovertemplate: '<b>%{y}</b><br>$%{x:,.0f}<extra></extra>',
            };
            return { data: [trace], layout: base(block.title, {
                xaxis: ax({ title: 'Amount ($)' }), yaxis: ax({ automargin: true }),
                height: Math.max(400, block.labels.length * 45),
                margin: { l: 150, r: 30, t: 55, b: 50 },
            })};
        },

        pie(block) {
            const ds = block.datasets[0];
            return {
                data: [{
                    labels: block.labels, values: ds.values,
                    type: 'pie', hole: 0,
                    marker: { colors: COLORS.slice(0, block.labels.length) },
                    textinfo: 'label+percent', textposition: 'outside',
                    textfont: { color: TEXT, size: 12 },
                    hovertemplate: '<b>%{label}</b><br>%{value:,.0f} (%{percent})<extra></extra>',
                }],
                layout: base(block.title, {
                    showlegend: true,
                    legend: { orientation: 'h', y: -0.15, x: 0.5, xanchor: 'center', font: { size: 10 } },
                }),
            };
        },

        donut(block) {
            const ds = block.datasets[0];
            return {
                data: [{
                    labels: block.labels, values: ds.values,
                    type: 'pie', hole: 0.5,
                    marker: { colors: COLORS.slice(0, block.labels.length) },
                    textinfo: 'label+percent', textposition: 'outside',
                    textfont: { color: TEXT, size: 12 },
                    hovertemplate: '<b>%{label}</b><br>%{value:,.0f} (%{percent})<extra></extra>',
                }],
                layout: base(block.title, {
                    showlegend: true,
                    legend: { orientation: 'h', y: -0.15, x: 0.5, xanchor: 'center', font: { size: 10 } },
                }),
            };
        },

        scatter(block) {
            const ds = block.datasets[0];
            const traces = [{
                x: block.labels, y: ds.values, mode: 'markers', type: 'scatter',
                marker: { color: COLORS[0], size: 9, opacity: 0.7, line: { width: 1, color: '#e2e8f0' } },
                hovertemplate: 'Ask: $%{x:,.0f}<br>Deal: $%{y:,.0f}<extra></extra>',
                name: ds.name,
            }];
            // Add trendline if flagged
            if (block.trendline && block.labels.length >= 8) {
                const xArr = block.labels.map(Number);
                const yArr = ds.values.map(Number);
                const n = xArr.length;
                const sumX = xArr.reduce((a,b)=>a+b,0), sumY = yArr.reduce((a,b)=>a+b,0);
                const sumXY = xArr.reduce((a,v,i)=>a+v*yArr[i],0);
                const sumX2 = xArr.reduce((a,v)=>a+v*v,0);
                const slope = (n*sumXY - sumX*sumY) / (n*sumX2 - sumX*sumX);
                const intercept = (sumY - slope*sumX) / n;
                const xSorted = [...xArr].sort((a,b)=>a-b);
                traces.push({
                    x: [xSorted[0], xSorted[xSorted.length-1]],
                    y: [slope*xSorted[0]+intercept, slope*xSorted[xSorted.length-1]+intercept],
                    mode: 'lines', type: 'scatter',
                    line: { color: '#ef4444', width: 2, dash: 'dash' },
                    name: 'Trend', showlegend: true,
                });
            }
            return { data: traces, layout: base(block.title, {
                xaxis: ax({ title: 'Original Ask ($)' }), yaxis: ax({ title: 'Deal Amount ($)' }),
            })};
        },

        stacked_bar(block) {
            const traces = block.datasets.map((ds, i) => ({
                x: block.labels, y: ds.values, name: ds.name,
                type: 'bar',
                marker: { color: COLORS[i % COLORS.length] },
                hovertemplate: '<b>%{x}</b><br>' + ds.name + ': %{y:,.0f}<extra></extra>',
            }));
            return { data: traces, layout: base(block.title, {
                barmode: 'stack', bargap: 0.15,
                xaxis: ax({ dtick: 1 }), yaxis: ax({ title: 'Count' }),
            })};
        },

        heatmap(block) {
            const ds = block.datasets[0];
            // ds.values is a 2D array: rows = sharks (y), cells = industries (x)
            return {
                data: [{
                    z: ds.values,
                    x: block.labels,
                    y: block.y_labels || [],
                    type: 'heatmap',
                    colorscale: [[0,'#1a1a2e'],[0.5,'#6366f1'],[1,'#f59e0b']],
                    hovertemplate: '%{y} × %{x}<br>$%{z:,.0f}<extra></extra>',
                    showscale: true,
                    colorbar: { tickfont: { color: TEXT }, title: { text: '$', font: { color: TEXT } } },
                }],
                layout: base(block.title, {
                    xaxis: ax({ tickangle: -35, automargin: true }),
                    yaxis: ax({ automargin: true }),
                    height: 450,
                    margin: { l: 100, r: 60, t: 55, b: 100 },
                }),
            };
        },
    };

    // Expose to window so other scripts can use it
    window.ChartEngine = ChartEngine;
    
    window.renderDynamicCharts = function(chartData, containerId) {
        if (typeof Plotly === 'undefined') { console.error('Plotly not loaded'); return; }

        const container = document.getElementById(containerId);

        // 1. Purge all existing Plotly instances
        container.querySelectorAll('[id^="plotly-"]').forEach(div => {
            try { Plotly.purge(div); } catch(e) {}
        });

        // 2. Destroy all DOM
        container.innerHTML = '';

        if (!Array.isArray(chartData) || chartData.length === 0) {
            container.innerHTML = '<p style="text-align:center;color:#94a3b8;padding:3rem;">No chart data available for the current filters.</p>';
            return;
        }

        // 3. Adaptive grid container (Rule 10)
        const grid = document.createElement('div');
        const count = chartData.length;
        if (count <= 2)      grid.className = 'charts-adaptive-grid grid-2col';
        else if (count <= 4) grid.className = 'charts-adaptive-grid grid-2x2';
        else                 grid.className = 'charts-adaptive-grid grid-auto';
        container.appendChild(grid);

        // 4. Build each chart
        chartData.forEach((block, index) => {
            const builder = window.ChartEngine[block.hint];
            if (!builder) { console.warn('Unknown hint:', block.hint); return; }

            const { data: traces, layout } = builder(block);
            const isWide = block.wide === true;

            const card = document.createElement('div');
            card.className = 'chart-card' + (isWide ? ' chart-card-wide' : '');
            card.id = 'wrap-' + block.id;

            const chartDiv = document.createElement('div');
            chartDiv.id = 'plotly-' + block.id + '-' + Date.now();
            chartDiv.style.width = '100%';
            chartDiv.style.minHeight = '380px';

            card.appendChild(chartDiv);
            grid.appendChild(card);

            Plotly.newPlot(chartDiv, traces, layout, {
                displayModeBar: false,
                responsive: true
            });
        });
    };

})();
