import streamlit as st
import pandas as pd
from datetime import datetime

st.title("Neue Version: 📦 Intelligente Auftragsverteilung")

# Datei-Uploads
auftrag_file = st.file_uploader("Lade die Auftragsliste hoch (.xlsx)", type=["xlsx"])
aufwand_file = st.file_uploader("Lade die Aufwandsliste hoch (.xlsx)", type=["xlsx"])

# ❗️Wichtig: Alles ab hier läuft nur, wenn beide Dateien hochgeladen wurden!
if auftrag_file and aufwand_file:

    # Excel-Dateien einlesen
    df_auftraege = pd.read_excel(auftrag_file, engine="openpyxl")
    df_aufwand = pd.read_excel(aufwand_file, engine="openpyxl")

    # Zusammenführen
    df = pd.merge(df_auftraege, df_aufwand, on="Sachnummer", how="left")

    # Dringlichkeit berechnen
    heute = pd.to_datetime(datetime.today().date())
    df["F2_Datum"] = pd.to_datetime(df["F2_Datum"])
    df["Dringlichkeit_Tage"] = (df["F2_Datum"] - heute).dt.days

    # 🧠 Beispiel: Schleife durch alle Aufträge
    for _, auftrag in df.iterrows():
        sachnummer = auftrag["Sachnummer"]
        aufwand = auftrag["Aufwand_Minuten"]
        f2 = auftrag["F2_Datum"]
        dringlichkeit = auftrag["Dringlichkeit_Tage"]
        # → Hier könntest du später Arbeitsplatz-Zuweisung reinpacken
        # st.write(f"{sachnummer}: {aufwand} Minuten – {dringlichkeit} Tage bis F2")

    # Ergebnis anzeigen
    st.subheader("📊 Auftragsübersicht")
    st.dataframe(df)

else:
    st.info("⬆️ Bitte lade beide Dateien hoch, um fortzufahren.")

# Vorschau
print(df)

pipeline = {
    "Platz 1": 35,  # Minuten bereits eingeplant
    "Platz 2": 40,
    "Platz 3": 20
}

gewicht_dringlichkeit = 2.0
gewicht_aufwand = 1.0
gewicht_pipeline = 1.5

zuweisungen = []

for _, auftrag in df.iterrows():
    min_wert = float("inf")
    bester_platz = None

    for platz, last in pipeline.items():
        wert = (
            auftrag["Dringlichkeit_Tage"] * gewicht_dringlichkeit +
            auftrag["Aufwand_Min"] * gewicht_aufwand +
            last * gewicht_pipeline
        )
        if wert < min_wert:
            min_wert = wert
            bester_platz = platz

    # Pipeline aktualisieren
    pipeline[bester_platz] += auftrag["Aufwand_Min"]

    # Speichern
    zuweisungen.append({
        "Auftrag": auftrag["Auftrag"],
        "Platz": bester_platz,
        "Aufwand": auftrag["Aufwand_Min"],
        "F2_Datum": auftrag["F2_Datum"],
        "Dringlichkeit": auftrag["Dringlichkeit_Tage"]
    })

# Ergebnis als DataFrame anzeigen
df_zuweisung = pd.DataFrame(zuweisungen)
print(df_zuweisung)
