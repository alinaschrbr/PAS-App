import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO

st.set_page_config(page_title="Auftragsverteilung", layout="wide")
st.title("🤖 Intelligente Auftragsverteilung")

# Datei-Uploads
auftrag_file = st.file_uploader("📥 Auftragsliste hochladen (.xlsx)", type=["xlsx"])
aufwand_file = st.file_uploader("📥 Aufwandsliste hochladen (.xlsx)", type=["xlsx"])
pipeline_file = st.file_uploader("📥 Pipeline je Arbeitsplatz (.xlsx)", type=["xlsx"])

if not (auftrag_file and aufwand_file and pipeline_file):
    st.info("⬆️ Bitte lade alle drei Dateien hoch, um fortzufahren.")

if auftrag_file and aufwand_file and pipeline_file:
    # Einlesen
    df_auftraege = pd.read_excel(auftrag_file, engine="openpyxl")
    df_aufwand = pd.read_excel(aufwand_file, engine="openpyxl")
    df_pipeline = pd.read_excel(pipeline_file, engine="openpyxl")

    # Aufräumen
    df_auftraege.columns = df_auftraege.columns.str.strip()
    df_aufwand.columns = df_aufwand.columns.str.strip()
    df_pipeline.columns = df_pipeline.columns.str.strip()

    # Merge + Dringlichkeit
    df = pd.merge(df_auftraege, df_aufwand, on="Sachnummer", how="left")
    df["F2_Datum"] = pd.to_datetime(df["F2_Datum"])
    heute = pd.to_datetime(datetime.today().date())
    df["Dringlichkeit_Tage"] = (df["F2_Datum"] - heute).dt.days
    df = df.sort_values(by="Dringlichkeit_Tage")

    # Pipeline vorbereiten
    pipeline = dict(zip(df_pipeline["Arbeitsplatz"], df_pipeline["Aktuelle_Minuten"]))
    zuweisungen = []

    # Verteilung
    for _, auftrag in df.iterrows():
        moegliche_plaetze = pipeline.items()
        arbeitsplatz = min(moegliche_plaetze, key=lambda x: x[1])[0]
        zuweisungen.append(arbeitsplatz)
        pipeline[arbeitsplatz] += auftrag["Aufwand_Min"]

    df["Zugewiesen_an"] = zuweisungen
    df_neu = pd.DataFrame(list(pipeline.items()), columns=["Arbeitsplatz", "Neue_Gesamtlast_Minuten"])

    # Tabelle anzeigen
    st.subheader("📊 Verteilte Aufträge")
    st.dataframe(df, use_container_width=True)

    st.subheader("🛠️ Neue Pipeline nach Zuweisung")
    st.dataframe(df_neu, use_container_width=True)

    # 📈 Visualisierung
    st.subheader("📊 Visualisierung: Auslastung der Arbeitsplätze")
    chart_data = df_neu.set_index("Arbeitsplatz")
    st.bar_chart(chart_data)

    # 🧾 Excel Export
    st.subheader("📤 Export als Excel-Datei")

    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Zuweisungen", index=False)
        df_neu.to_excel(writer, sheet_name="Pipeline", index=False)
    output.seek(0)

    st.download_button(
        label="⬇️ Ergebnis herunterladen",
        data=output,
        file_name="verteilte_auftraege.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
