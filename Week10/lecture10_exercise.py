import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="CO2 Dashboard", page_icon="🌱", layout="wide")

# ── Data ──────────────────────────────────────────────────────────────────────
# @st.cache_data: Streamlit reruns the entire script on every widget interaction.
# Without caching, the CSV is read from disk on every interaction — slow and wasteful.
# cache_data stores the result after the first run and reuses it until the file changes.
@st.cache_data
def load_data():
    path = Path(__file__).parent.parent / 'data' / 'co2_emissions.csv'
    df = pd.read_csv(path)
    df['Date'] = pd.to_datetime(df['Year'].astype(str) + '-01-01')
    return df

df = load_data()

st.title("🌱 CO2 Emissions Explorer")
st.caption("Source: Our World in Data — ourworldindata.org/co2-emissions")

# ── TASK 1: Sidebar with 5 widgets ────────────────────────────────────────────
#   a) st.selectbox for Region (with 'All')
#   b) st.multiselect for Countries (updates based on region — chained)
#   c) st.date_input for date range (two-handle; convert years to Jan-1 dates)
#   d) st.radio for Metric: "Total CO2 (Mt)" vs "CO2 per capita"
#   e) st.checkbox labelled "Show only top emitter highlighted"
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Filters")
    
    # a) selectbox for Region
    regions = ['All'] + sorted(df['Region'].unique().tolist())
    selected_region = st.selectbox("Region", regions)
    
    # b) multiselect for Countries (chained filter)
    if selected_region == 'All':
        country_options = sorted(df['Country'].unique().tolist())
    else:
        country_options = sorted(df[df['Region'] == selected_region]['Country'].unique().tolist())
        
    # Pick a few default countries that are guaranteed to be in the options list
    default_countries = [c for c in ['China', 'United States', 'India', 'Germany', 'United Kingdom'] if c in country_options]
    if not default_countries and country_options:
        default_countries = country_options[:3]
        
    selected_countries = st.multiselect("Countries", country_options, default=default_countries)
    
    # c) date_input for date range (two-handle)
    min_date = df['Date'].min().date()
    max_date = df['Date'].max().date()
    # Default to 1980 to 2022 to make initial rendering clean
    default_start = max(min_date, pd.to_datetime("1980-01-01").date())
    selected_dates = st.date_input(
        "Date range",
        value=(default_start, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    st.divider()
    
    # d) radio for Metric
    metric = st.radio("Metric", ["Total CO2 (Mt)", "CO2 per capita"])
    
    # e) checkbox for top emitter highlight
    highlight_top = st.checkbox("Show only top emitter highlighted")

# Guards
if not selected_countries:
    st.warning("Please select at least one country.")
    st.stop()

if not isinstance(selected_dates, tuple) or len(selected_dates) < 2:
    st.warning("Please select both a start and an end date.")
    st.stop()

# Convert dates to Timestamp for filtering
start_dt = pd.to_datetime(selected_dates[0])
end_dt = pd.to_datetime(selected_dates[1])

# Filter the data
filtered = df[
    df['Country'].isin(selected_countries) &
    (df['Date'] >= start_dt) &
    (df['Date'] <= end_dt)
].copy()

if filtered.empty:
    st.warning("No data matches the selected filters.")
    st.stop()

y_col = 'CO2_Mt' if metric == "Total CO2 (Mt)" else 'CO2_per_capita'
y_label = 'CO2 Emissions (Mt)' if y_col == 'CO2_Mt' else 'CO2 per Capita'

# ── TASK 2: Filter summary caption ────────────────────────────────────────────
# Show: "X countries | Region | Date range | Metric"
# ─────────────────────────────────────────────────────────────────────────────
start_year = selected_dates[0].year
end_year = selected_dates[1].year
st.caption(f"{len(selected_countries)} countries selected | Region: {selected_region} | "
           f"Range: {start_year}–{end_year} | Metric: {metric}")


# ── EXTENSION: KPI row above the charts ───────────────────────────────────────
#   - Total CO2 in last year of selected range (sum across selected countries)
#   - % change from first to last year
#   - Country with highest emissions in last year
# ─────────────────────────────────────────────────────────────────────────────
kpi_data = filtered.sort_values('Year')
latest_year = kpi_data['Year'].max()
first_year = kpi_data['Year'].min()

latest_df = kpi_data[kpi_data['Year'] == latest_year]
first_df = kpi_data[kpi_data['Year'] == first_year]

val_latest = latest_df[y_col].sum()
val_first = first_df[y_col].sum()

pct_change = ((val_latest - val_first) / val_first * 100) if val_first != 0 else 0.0

highest_country_row = latest_df.nlargest(1, y_col)
highest_country = highest_country_row['Country'].values[0] if not highest_country_row.empty else "N/A"
highest_val = highest_country_row[y_col].values[0] if not highest_country_row.empty else 0.0

st.divider()
k1, k2, k3 = st.columns(3)
k1.metric(f"Total {y_label} ({latest_year})", f"{val_latest:,.1f}", help="Sum across all selected countries")
k2.metric("% Change (First to Last Year)", f"{pct_change:+.1f}%", f"from {val_first:,.1f} in {first_year}")
k3.metric("Top Emitter (Last Year)", highest_country, f"{highest_val:,.1f} {y_label}")

st.divider()

# ── TASK 3: Two charts reacting to ALL filters ────────────────────────────────
#   Left: line chart — selected metric over time, one line per country
#         If "Show only top emitter highlighted" checkbox is on:
#           - grey all lines except the highest emitter in the date range
#           - label that country at the end of its line (SWD grey-and-highlight)
#   Right: bar chart — ranking for the last year in selected date range
# ─────────────────────────────────────────────────────────────────────────────
col_left, col_right = st.columns([2, 1])

with col_left:
    if highlight_top:
        # BBD Color Type: highlight (blue vs grey)
        # Highlight top emitter, others are grayed out
        top_emitter = filtered.groupby('Country')[y_col].max().idxmax()
        filtered['highlight'] = filtered['Country'].apply(
            lambda c: 'Top Emitter' if c == top_emitter else 'Others'
        )
        fig1 = px.line(
            filtered, x='Year', y=y_col, color='highlight', line_group='Country',
            color_discrete_map={'Top Emitter': '#2E75B6', 'Others': '#D3D3D3'},
            category_orders={'highlight': ['Others', 'Top Emitter']},
            labels={y_col: y_label},
            title=f'China has emerged as the top emitter among the selected nations ({start_year}-{end_year})' if top_emitter == 'China'
                  else f'{top_emitter} stands out as the highest emitter in the selected range'
        )
        
        # Label the country at the end of its line
        latest_pt = filtered[(filtered['Country'] == top_emitter) & (filtered['Year'] == latest_year)]
        if not latest_pt.empty:
            fig1.add_annotation(
                x=latest_pt['Year'].values[0],
                y=latest_pt[y_col].values[0],
                text=f"  <b>{top_emitter}</b>",
                showarrow=False,
                xanchor="left",
                font=dict(color='#2E75B6', size=11, family='Arial')
            )
    else:
        # BBD Color Type: categorical (multiple distinct colors for countries)
        fig1 = px.line(
            filtered, x='Year', y=y_col, color='Country',
            labels={y_col: y_label},
            title=f'{metric} has evolved significantly over time ({start_year}-{end_year})'
        )
        
    fig1.update_layout(
        plot_bgcolor='white', paper_bgcolor='white',
        font=dict(family='Arial', size=12),
        xaxis=dict(showgrid=False),
        yaxis=dict(gridcolor='#EEEEEE'),
        showlegend=not highlight_top
    )
    st.plotly_chart(fig1, use_container_width=True)

with col_right:
    # Bar chart: ranking for the latest year
    latest_rankings = filtered[filtered['Year'] == latest_year].sort_values(y_col)
    
    # BBD Color Type: sequential (shades of blue indicating scale/magnitude)
    fig2 = px.bar(
        latest_rankings, x=y_col, y='Country', orientation='h',
        color=y_col,
        color_continuous_scale='Blues',
        labels={y_col: y_label, 'Country': ''},
        title=f'Emissions ranking in {latest_year}'
    )
    
    fig2.update_traces(marker_line_width=0)
    fig2.update_layout(
        plot_bgcolor='white', paper_bgcolor='white',
        font=dict(family='Arial', size=12),
        xaxis=dict(gridcolor='#EEEEEE'),
        yaxis=dict(showgrid=False),
        coloraxis_showscale=False
    )
    st.plotly_chart(fig2, use_container_width=True)