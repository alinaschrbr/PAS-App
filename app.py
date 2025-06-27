import os
import pandas as pd
import streamlit as st

st.set_page_config(page_title="📦 Intelligente Auftragsverteilung", layout="wide")
st.title("📦 Neue Version: Intelligente Auftragsverteilung")

# === Lokale oder Cloud-Umgebung erkennen ===
ONEDRIVE_PATH = r"C:\Users\Alina.Schreiber\OneDrive - DP World\Desktop\PAS-App"
local_mode = os.path.exists(ONEDRIVE_PATH)

# === Dateien laden ===
if local_mode:
    st.success("✅ Lokaler Modus erkannt – Dateien werden automatisch geladen")
    df_auftraege = pd.read_excel(os.path.join(ONEDRIVE_PATH, "auftraege.xlsx"))
    df_aufwand = pd.read_excel(os.path.join(ONEDRIVE_PATH, "arbeitsaufwand.xlsx"))
    df_pipeline = pd.read_excel(os.path.join(ONEDRIVE_PATH, "pipeline.xlsx"))
else:
    st.warning("🌐 Cloud-Modus – bitte lade die Dateien hoch")

    auftraege_file = st.file_uploader("📄 Lade die Auftragsliste hoch (.xlsx)", type="xlsx")
    aufwand_file = st.file_uploader("📄 Lade die Aufwandsliste hoch (.xlsx)", type="xlsx")
    pipeline_file = st.file_uploader("📄 Lade die Pipeline hoch (.xlsx)", type="xlsx")

    if auftraege_file and aufwand_file and pipeline_file:
        df_auftraege = pd.read_excel(auftraege_file)
        df_aufwand = pd.read_excel(aufwand_file)
        df_pipeline = pd.read_excel(pipeline_file)
    else:
        st.info("Bitte lade alle drei Dateien hoch, um fortzufahren.")
        st.stop()

# === Datenprüfung ===
st.subheader("📊 Vorschau: Einzelne Aufträge")
st.dataframe(df_auftraege.head())

# === Beispielhafte Logik für Zuweisung (vereinfachte Version) ===
# Verknüpfen von Aufwand-Daten mit Aufträgen (nach Artikelnummer o.ä.)
if "Artikelnummer" in df_auftraege.columns and "Artikelnummer" in df_aufwand.columns:
    df = pd.merge(df_auftraege, df_aufwand, on="Artikelnummer", how="left")
else:
    st.error("Fehlende Spalte 'Artikelnummer' in einer der Dateien.")
    st.stop()

# Beispiel-Zuweisung: Nur als Platzhalter
if "Arbeitsplatz" not in df.columns:
    df["Arbeitsplatz"] = df_pipeline["Arbeitsplatz"].sample(n=len(df), replace=True).values

# Ergebnis anzeigen
st.subheader("📋 Ergebnis: Verteilte Aufträge")
st.dataframe(df.head())
