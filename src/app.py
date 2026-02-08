import streamlit as st

st.set_page_config(
    layout="wide",
    page_title="Soccerwise Tracker",
    page_icon="🦉",
)

tracker = st.Page(
    "standings.py",
    title="Golden Boot",
    icon="👟",
)
about = st.Page("about.py", title="About the Golden Boot", icon="ℹ️")
over_under = st.Page("over_under.py", title="Over/Under", icon="📈")

pg = st.navigation([tracker, about, over_under])
pg.run()
