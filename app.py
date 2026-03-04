import streamlit as st
import pandas as pd

# Seiteneinstellungen
st.set_page_config(page_title="Treasury Optimizer 2026", layout="wide")

# Titel und Einleitung
st.title("🚀 Strategische FX-Optimierung für Stripe-Zahlungsströme")
st.markdown("""
Diese App analysiert das Einsparpotenzial durch den Wechsel von automatischer Stripe-Konvertierung 
auf ein Multi-Währungs-Setup für unsere GmbH.
""")

# --- SEKTION 1: ROI RECHNER ---
st.header("1. Interaktiver ROI-Rechner")
col1, col2 = st.columns(2)

with col1:
    st.subheader("Input: Monatliche Volumina")
    usd_volume = st.slider("Monatliches USD Volumen ($)", 0, 200000, 50000, step=5000)
    gbp_volume = st.slider("Monatliches GBP Volumen (£)", 0, 100000, 20000, step=2000)
    fx_fee_standard = st.number_input("Aktuelle Stripe FX-Gebühr (in %)", value=2.5, step=0.1)

# Berechnungen
total_volume_eur = (usd_volume * 0.92) + (gbp_volume * 1.17) # Grobe Kurse 2026
annual_loss = (usd_volume + gbp_volume) * (fx_fee_standard / 100) * 12

with col2:
    st.subheader("Dein Einsparpotenzial")
    st.metric(label="Jährlicher Verlust durch Konvertierung", value=f"{annual_loss:,.2f} Units")
    st.info(f"Durch ein 'Like-for-Like' Setup sparen wir ca. **{annual_loss * 0.8:,.2f} €** pro Jahr (abzüglich minimaler Auszahlungsgebühren).")

# --- SEKTION 2: ANBIETERVERGLEICH ---
st.header("2. Vergleich der Top-Lösungen (Stand 2026)")

data = {
    "Feature": ["Lokale USD/GBP Daten", "DATEV-Schnittstelle", "Monatliche Gebühr", "Cashback (Karten)", "Best Use Case"],
    "Airwallex": ["✅ Ja (Echt)", "✅ Nativ (Neu 2026)", "0€ - 49€", "1.5% (US/UK)", "Skalierende GmbH (Testsieger)"],
    "Wise Business": ["✅ Ja (Echt)", "🟡 CSV / Drittanbieter", "0€ (einmalig 50€)", "0%", "Kleine Volumina / Simpel"],
    "Revolut Business": ["✅ Ja (Partner)", "🟡 Standard-Feed", "25€ - 100€", "Variabel", "Tech-Teams / FX-Hedging"]
}
df = pd.DataFrame(data)
st.table(df)

# --- SEKTION 3: DER NEUE WORKFLOW ---
st.header("3. Ziel-Infrastruktur")
st.mermaid("""
graph LR
    A[Kunde USD/GBP] --> B[Stripe Account]
    B -->|Keine Konvertierung| C[Airwallex Wallet]
    C --> D[USD Gehalt / US Team]
    C --> E[GBP Gehalt / UK Team]
    B -->|EUR| F[Sparkasse]
""")

# --- SEKTION 4: SCHRITT-FÜR-SCHRITT PLAN ---
st.header("4. Implementierungs-Roadmap")
steps = [
    "Phase 1: Airwallex Business Account Eröffnung (KYC via GmbH-Daten)",
    "Phase 2: Aktivierung der 'Global Accounts' für USD (USA) & GBP (UK)",
    "Phase 3: Hinterlegung der neuen Daten in Stripe (Payout Settings)",
    "Phase 4: Anbindung an DATEV für die automatisierte Buchhaltung"
]
for step in steps:
    st.checkbox(step)

st.success("Bereit für die Entscheidung am Freitag!")