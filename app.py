import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Auftragsverteilung", layout="wide")
st.title("🤖 Intelligente Auftragsverteilung")

# Datei-Uploads
auftrag_file = st.file_uploader("📥 Auftragsliste hochladen (.xlsx)", type=["xlsx"])
aufwand_file = st.file_uploader("📥 Aufwandsliste hochladen (.xlsx)", type=["xlsx"])
pipeline_file = st.file_uploader("📥 Pipeline je Arbeitsplatz (.xlsx)", type=["xlsx"])

if not (auftrag_file and aufwand_file and pipeline_file):
    st.info("⬆️ Bitte lade alle drei Dateien hoch, um fortzufahren.")

if auftrag_file and aufwand_file and pipeline_file:
    # Excel-Dateien einlesen
    df_auftraege = pd.read_excel(auftrag_file, engine="openpyxl")
    df_aufwand = pd.read_excel(aufwand_file, engine="openpyxl")
    df_pipeline = pd.read_excel(pipeline_file, engine="openpyxl")

    # Aufräumen: Spaltennamen glätten (optional, verhindert Fehler durch Leerzeichen etc.)
    df_auftraege.columns = df_auftraege.columns.str.strip()
    df_aufwand.columns = df_aufwand.columns.str.strip()
    df_pipeline.columns = df_pipeline.columns.str.strip()

    # Merge von Aufträgen mit Aufwand
    df = pd.merge(df_auftraege, df_aufwand, on="Sachnummer", how="left")

    # Dringlichkeit berechnen
    df["F2_Datum"] = pd.to_datetime(df["F2_Datum"])
    heute = pd.to_datetime(datetime.today().date())
    df["Dringlichkeit_Tage"] = (df["F2_Datum"] - heute).dt.days

    # Nach Dringlichkeit sortieren
    df = df.sort_values(by="Dringlichkeit_Tage")

    # Dictionary für aktuelle Pipeline
    pipeline = dict(zip(df_pipeline["Arbeitsplatz"], df_pipeline["Aktuelle_Minuten"]))

    # Neue Spalte zur Zuweisung vorbereiten
    zuweisungen = []

    # Verteilung der Aufträge
    for _, auftrag in df.iterrows():
        # Finde den Arbeitsplatz mit der geringsten Last
        arbeitsplatz = min(pipeline, key=pipeline.get)
        
        # Zuweisung speichern
        zuweisungen.append(arbeitsplatz)
        
        # Minutenlast erhöhen
        aufwand = auftrag["Aufwand_Min"]
        pipeline[arbeitsplatz] += aufwand

    # Spalte hinzufügen
    df["Zugewiesen_an"] = zuweisungen

    # Ergebnis anzeigen
    st.subheader("📊 Verteilte Aufträge")
    st.dataframe(df, use_container_width=True)

    # Aktuelle Pipeline nach Verteilung anzeigen
    st.subheader("🛠️ Neue Pipeline nach Zuweisung")
    df_neu = pd.DataFrame(list(pipeline.items()), columns=["Arbeitsplatz", "Neue_Gesamtlast_Minuten"])
    st.dataframe(df_neu, use_container_width=True)
