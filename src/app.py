import streamlit as st

st.set_page_config(
    layout="wide",
    page_title="Soccerwise Tracker",
    page_icon="🦉",
)

golden_boot = st.Page(
    "standings.py",
    title="Golden Boot",
    icon="👟",
)
about = st.Page("about.py", title="About the Golden Boot", icon="ℹ️")
over_under = st.Page("over_under.py", title="Over/Under", icon="📈")

pg = st.navigation([golden_boot, over_under, about])
pg.run()
