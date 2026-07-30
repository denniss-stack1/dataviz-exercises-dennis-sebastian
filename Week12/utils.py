# utils.py — shared by every page
import pandas as pd
import streamlit as st
from pathlib import Path

# ─────────────────────────────────────────────────────────────────────────────
# cached loader — cap at 95th percentile INSIDE the loader so the
# expensive work is done once and shared by all pages (same function =
# same cache entry everywhere)
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    path = Path(__file__).parent.parent / 'data' / 'airbnb_london.csv'
    df = pd.read_csv(path)
    p95 = df['price'].quantile(0.95)
    return df[df['price'] <= p95].copy(), p95   # .copy() → no SettingWithCopyWarning


# ─────────────────────────────────────────────────────────────────────────────
# initialise filter keys once + keep them alive on every run.
# Streamlit deletes widget keys not rendered in the current run — without the
# re-assignment, filters would reset on every page switch.
# ─────────────────────────────────────────────────────────────────────────────
def init_filters(df):
    defaults = {
        'flt_rooms': list(df['room_type'].unique()),
        'flt_hoods': sorted(df['neighbourhood'].unique()),
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value                  # initialise using the default
        else:
            st.session_state[key] = st.session_state[key]  # keep alive across pages
    # slider owns its own initialisation — only keep it alive here
    if 'flt_price' in st.session_state:
        st.session_state['flt_price'] = st.session_state['flt_price']


# ─────────────────────────────────────────────────────────────────────────────
# shared sidebar — called at the top of BOTH pages.
# Widgets use key= ONLY (no default=/value=): values come from session_state,
# passing both would trigger Streamlit's double-set warning.
# ─────────────────────────────────────────────────────────────────────────────
def sidebar_filters(df, p95):
    init_filters(df)
    with st.sidebar:
        st.header('🔎 Filters')
        st.multiselect('Room type', df['room_type'].unique(), key='flt_rooms')
        st.multiselect('Neighbourhood', sorted(df['neighbourhood'].unique()),
                       key='flt_hoods')
        min_p, max_p = int(df['price'].min()), int(df['price'].max())+1
        st.slider('Price (£/night)', min_p, max_p,
                  value=(min_p, max_p), key='flt_price')
        st.divider()
        # BBD: tell users about data decisions made on their behalf
        st.caption(f'Prices capped at 95th percentile (£{p95:.0f}) '
                   'to remove extreme outliers.')

    filtered = df[
        df['room_type'].isin(st.session_state.flt_rooms) &
        df['neighbourhood'].isin(st.session_state.flt_hoods) &
        df['price'].between(*st.session_state.flt_price)
    ]
    if filtered.empty:
        st.warning('No listings match current filters.')
        st.stop()
    return filtered
