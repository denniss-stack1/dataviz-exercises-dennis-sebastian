# pages/03_demand.py — YOUR new page (BBD squiggle level 3: demand story)
import streamlit as st
import plotly.express as px
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils import load_data, sidebar_filters

# ─────────────────────────────────────────────────────────────────────────────
# Load data + shared sidebar
# ─────────────────────────────────────────────────────────────────────────────
df, p95 = load_data()
filtered = sidebar_filters(df, p95)  # shared sidebar — same filters on every page

st.title("Where is guest demand strongest?")
st.caption("Analyzing reviews per month as a proxy for guest demand across room types")

# ─────────────────────────────────────────────────────────────────────────────
# A persisted widget of your own
# ─────────────────────────────────────────────────────────────────────────────
rooms_avail = list(filtered['room_type'].unique())

if 'sel_room' not in st.session_state:
    st.session_state.sel_room = rooms_avail[0]
st.session_state.sel_room = st.session_state.sel_room     # keep alive across pages

if st.session_state.sel_room not in rooms_avail:          # guard against filtered options
    st.session_state.sel_room = rooms_avail[0]

st.radio("Focus room type", rooms_avail, key='sel_room')
room = st.session_state.sel_room
room_df = filtered[filtered['room_type'] == room]

# ─────────────────────────────────────────────────────────────────────────────
# KPI row (st.columns(3)) about the focused selection
# ─────────────────────────────────────────────────────────────────────────────
k1, k2, k3 = st.columns(3)
k1.metric("Focused Listings", f"{len(room_df):,}")
k2.metric("Median Reviews/Month", f"{room_df['reviews_per_month'].median():.2f}",
          f"{room_df['reviews_per_month'].median() - filtered['reviews_per_month'].median():+.2f} vs overall")
k3.metric("Median Price", f"£{room_df['price'].median():.0f}/night",
          f"£{room_df['price'].median() - filtered['price'].median():+.0f} vs overall")

st.divider()

# ─────────────────────────────────────────────────────────────────────────────
# One chart — demand story
# Scatter plot of price vs reviews_per_month with focused room type highlighted.
# ─────────────────────────────────────────────────────────────────────────────

# BBD Color Type: highlight (blue vs grey)
# CVD friendly: no red-green combination, high contrast

plot_df = filtered.copy()
plot_df['highlight'] = plot_df['room_type'].apply(
    lambda r: room if r == room else 'Other room types')

fig = px.scatter(
    plot_df,
    x='reviews_per_month',
    y='price',
    color='highlight',
    color_discrete_map={room: '#2E75B6', 'Other room types': '#AAAAAA'},
    category_orders={'highlight': ['Other room types', room]},  # selected room drawn on top
    hover_name='name',
    hover_data={
        'reviews_per_month': ':.2f',
        'price': '£:.0f',
        'room_type': True,
        'highlight': False
    },
    labels={
        'reviews_per_month': 'Reviews per Month (Demand Proxy)',
        'price': 'Nightly Price (£)',
        'room_type': 'Room Type'
    },
    title=f'Lower-priced {room} listings attract higher guest demand'
)

fig.update_traces(marker=dict(size=8, opacity=0.75, line=dict(width=0)))
fig.update_xaxes(gridcolor='#EEEEEE')
fig.update_yaxes(gridcolor='#EEEEEE')
fig.update_layout(
    plot_bgcolor='white',
    paper_bgcolor='white',
    font=dict(family='Arial', size=12),
    legend=dict(orientation='h', y=1.08)
)

st.plotly_chart(fig, use_container_width=True)
