import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Intelligente Auftragsverteilung", layout="wide")
st.title("🚀 Neue Version: 📦 Intelligente Auftragsverteilung")

# Datei-Uploads
auftrag_file = st.file_uploader("📥 Lade die Auftragsliste hoch (.xlsx)", type=["xlsx"])
aufwand_file = st.file_uploader("📥 Lade die Aufwandsliste hoch (.xlsx)", type=["xlsx"])

# Hinweis anzeigen, wenn noch nichts hochgeladen wurde
if not auftrag_file or not aufwand_file:
    st.info("⬆️ Bitte lade beide Dateien hoch, um fortzufahren.")
    
# Wenn beide Dateien hochgeladen sind, startet die Logik
if auftrag_file and aufwand_file:
    # Einlesen der Excel-Dateien
    df_auftraege = pd.read_excel(auftrag_file, engine="openpyxl")
    df_aufwand = pd.read_excel(aufwand_file, engine="openpyxl")

    # Zusammenführen beider Tabellen über Sachnummer
    df = pd.merge(df_auftraege, df_aufwand, on="Sachnummer", how="left")
    
    st.write("🔍 Spaltenübersicht:", df.columns.tolist())

    # F2-Datum in datetime konvertieren und Dringlichkeit berechnen
    df["F2_Datum"] = pd.to_datetime(df["F2_Datum"])
    heute = pd.to_datetime(datetime.today().date())
    df["Dringlichkeit_Tage"] = (df["F2_Datum"] - heute).dt.days

    # Beispiel-Schleife: Ausgabe jeder Zeile in Kurzform
    st.subheader("📋 Vorschau: Einzelne Aufträge")
    for _, auftrag in df.iterrows():
        st.markdown(
            f"- **Sachnummer:** {auftrag['Sachnummer']}, "
            f"**Aufwand:** {auftrag['Aufwand_Min']} min, "
            f"**F2:** {auftrag['F2_Datum'].date()}, "
            f"**Dringlichkeit:** {auftrag['Dringlichkeit_Tage']} Tage"
        )

    # Gesamttabelle anzeigen
    st.subheader("📊 Gesamttabelle")
    st.dataframe(df, use_container_width=True)
