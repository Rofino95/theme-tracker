import os
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Aktien Detail", layout="wide")

st.title("Aktien-Detailseite")

if not os.path.exists("theme_scores.csv"):
    st.warning("theme_scores.csv wurde nicht gefunden.")
    st.stop()

df = pd.read_csv("theme_scores.csv")

st.write("Datei erfolgreich geladen.")
st.dataframe(df.head())
