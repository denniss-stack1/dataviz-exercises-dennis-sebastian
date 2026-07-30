# pages/02_drilldown.py — drill-down page 
import streamlit as st
import pandas as pd
import plotly.express as px
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils import load_data, sidebar_filters

df, p95 = load_data()
filtered = sidebar_filters(df, p95)  # SAME sidebar — choices carried over from page 1

# ─────────────────────────────────────────────────────────────────────────────
# question title + persisted drill-down selectbox
# ─────────────────────────────────────────────────────────────────────────────
st.title('Which neighbourhoods drive the premium?')
st.caption('From the market summary to one neighbourhood story')

# initialise once, then keep alive — same trick as the filters
if 'sel_hood' not in st.session_state:
    st.session_state.sel_hood = sorted(filtered['neighbourhood'].unique())[0]
st.session_state.sel_hood = st.session_state.sel_hood     # keep alive across pages

hoods_avail = sorted(filtered['neighbourhood'].unique())
if st.session_state.sel_hood not in hoods_avail:          # guard: filters may have
    st.session_state.sel_hood = hoods_avail[0]            # removed the saved choice

st.selectbox('Drill into a neighbourhood', hoods_avail, key='sel_hood')
hood = st.session_state.sel_hood
hood_df = filtered[filtered['neighbourhood'] == hood]

k1, k2, k3 = st.columns(3)
k1.metric('Listings', f'{len(hood_df):,}')
k2.metric('Median Price', f"£{hood_df['price'].median():.0f}/night",
          f"£{hood_df['price'].median()-filtered['price'].median():+.0f} "
          'vs filtered market')
k3.metric('Most common room type', hood_df['room_type'].mode()[0])

st.divider()

# ─────────────────────────────────────────────────────────────────────────────
# one comparison chart — chosen neighbourhood vs the filtered market
# ─────────────────────────────────────────────────────────────────────────────
# highlight column → declarative colour mapping
plot_df = filtered.copy()
plot_df['highlight'] = plot_df['neighbourhood'].apply(
    lambda n: hood if n == hood else 'Rest of market')

# Color: blue for the chosen neighbourhood, grey for everything else
# histnorm='percent' so a small neighbourhood is comparable to the whole market
fig = px.histogram(plot_df, x='price', color='highlight',
                   barmode='overlay', histnorm='percent', nbins=40,
                   color_discrete_map={hood: '#2E75B6', 'Rest of market': '#AAAAAA'},
                   labels={'price': 'Nightly Price (£)', 'highlight': ''},
                   title=f'{hood} vs the filtered market')
fig.update_traces(marker_line_width=0)
fig.update_layout(plot_bgcolor='white', paper_bgcolor='white',
                  font=dict(family='Arial', size=12),
                  yaxis=dict(gridcolor='#EEEEEE', title='% of listings'),
                  xaxis=dict(showgrid=False),
                  legend=dict(orientation='h', y=1.08))
st.plotly_chart(fig, width='stretch')

# TEST: pick a neighbourhood, switch to page 1, change a filter,
# come back — both the filters AND the selection must be where you left them.
