"""
Lecture 12 Exercise — Extend the Dashboard with a Third Page
=============================================================
Run with: streamlit run app.py

STARTER CODE: this folder contains the complete 2-page dashboard we built
together in class (app.py, utils.py, pages/01, pages/02). Do not modify
pages 1 and 2 — your job is to ADD a third page:

    pages/03_demand.py  →  "Where is guest demand strongest?"

The third level of the BBD squiggle: market summary (p1) → neighbourhood
story (p2) → demand drill-down (p3).

BBD checklist to complete before submitting:
[ ] Page title is a QUESTION, not a topic label
[ ] Colour type named in a comment next to your chart
[ ] No red/green as the only differentiator (CVD rule)
[ ] No pie charts, no packed bubble charts
[ ] Sidebar filters persist onto your new page (via sidebar_filters)
[ ] Your own widget choice persists too (session_state keep-alive + guard)
[ ] 5-second test passed (shown to a classmate for 5 sec)

Push the whole folder to week12/.
"""

import streamlit as st

# Page config + CSS — applied ONCE here; app.py runs on every page switch
st.set_page_config(page_title="London Airbnb Analytics", page_icon="🏠",
                   layout="wide", initial_sidebar_state="expanded")



# ─────────────────────────────────────────────────────────────────────────────
# Register your new page below
# ─────────────────────────────────────────────────────────────────────────────
pg = st.navigation([
    st.Page("pages/01_market.py",
            title="What does a night in London cost?",   icon="🏠"),
    st.Page("pages/02_drilldown.py",
            title="Which neighbourhoods drive the premium?", icon="📍"),
    st.Page("pages/03_demand.py",
            title="Where is guest demand strongest?", icon="📈"),
])
pg.run()
