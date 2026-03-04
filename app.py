import streamlit as st
import pandas as pd
import altair as alt

# --- SEITENKONFIGURATION ---
st.set_page_config(
    page_title="Treasury Optimizer", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# --- KONSTANTEN & AKTUELLE WECHSELKURSE (März 2026) ---
AOV_USD = 1499
AOV_GBP = 999
FX_RATE_USD_EUR = 0.92  # 1 USD entspricht ca. 0.92 EUR
FX_RATE_GBP_EUR = 1.17  # 1 GBP entspricht ca. 1.17 EUR

# --- HEADER ---
st.title(":material/account_balance: Strategisches Multi-Währungs-Setup")
st.markdown("Dashboard zur Simulation der Stripe-Zahlungsströme und Optimierung der FX-Margen.")
st.divider()

# --- SIDEBAR: INPUT PARAMETER ---
with st.sidebar:
    st.header(":material/settings: Parameter")
    
    st.subheader("Monatliches Wachstum")
    # GEÄNDERT: st.number_input statt st.slider für exakte Eingaben
    us_customers = st.number_input("Anzahl US-Abonnenten", min_value=0, value=15, step=1, help="Kunden à $1.499")
    uk_customers = st.number_input("Anzahl UK-Abonnenten", min_value=0, value=10, step=1, help="Kunden à £999")
    
    st.subheader("Stripe Auszahlungs-Intervall")
    payout_freq = st.selectbox(
        "Wie oft soll Stripe auf das Multi-Währungskonto auszahlen?", 
        options=["Monatlich (Empfohlen)", "Wöchentlich", "Täglich"],
        help="Da aktuell 250k € Überbrückungskapital für Gehälter vorhanden sind, wird 'Monatlich' empfohlen."
    )
    
    # Logik für das Dropdown
    if payout_freq == "Monatlich (Empfohlen)":
        payouts_per_month = 1
    elif payout_freq == "Wöchentlich":
        payouts_per_month = 4
    else:
        payouts_per_month = 20 # ca. Werktage

# --- BERECHNUNGSLOGIK ---
# Volumina in Originalwährung (Jetzt separat für die Anzeige)
vol_usd = us_customers * AOV_USD
vol_gbp = uk_customers * AOV_GBP

# Kosten Status Quo (2% Stripe Standard Konvertierung) - in EUR umgerechnet
cost_status_quo_eur = (vol_usd * FX_RATE_USD_EUR * 0.02) + (vol_gbp * FX_RATE_GBP_EUR * 0.02)

# Kosten Neues Setup (Alternative Currency Fee + Cross Border + Fixe Payout Fees)
cost_new_usd = (vol_usd * 0.0125) + (payouts_per_month * 1.50)
cost_new_gbp = (vol_gbp * 0.01) + (payouts_per_month * 0.50)

# Neue Kosten in EUR umrechnen, um die Ersparnis berechnen zu können
cost_new_eur = (cost_new_usd * FX_RATE_USD_EUR) + (cost_new_gbp * FX_RATE_GBP_EUR)

# Netto-Ersparnis in EUR
savings_eur = cost_status_quo_eur - cost_new_eur

# --- MAIN DASHBOARD ---
# 1. KPIs (GEÄNDERT: Umsatz getrennt nach USD und GBP, Ersparnis in EUR)
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="Umsatz-Volumen (USD)", 
        value=f"$ {vol_usd:,.0f}", 
        help=f"{us_customers} US-Kunden mal $1.499"
    )
with col2:
    st.metric(
        label="Umsatz-Volumen (GBP)", 
        value=f"£ {vol_gbp:,.0f}", 
        help=f"{uk_customers} UK-Kunden mal £999"
    )
with col3:
    st.metric(
        label="Netto-Ersparnis (Monat)", 
        value=f"€ {savings_eur:,.0f}",
        delta="Zusätzliche Marge",
        help="Ersparnis in Euro nach Abzug aller neuen Stripe-Payout-Gebühren für das Multi-Währungskonto."
    )

st.divider()

# 2. VISUALISIERUNG & BREAK-EVEN
col_chart, col_info = st.columns([2, 1])

with col_chart:
    st.subheader(":material/bar_chart: Kostenvergleich (in EUR)")
    # Daten für das Diagramm aufbereiten
    chart_data = pd.DataFrame({
        "Szenario": ["Status Quo (Sparkasse)", "Neues Setup (Multi-Währung)"],
        "Kosten in EUR": [cost_status_quo_eur, cost_new_eur]
    })
    
    # Altair Balkendiagramm für sauberes SaaS-Design
    chart = alt.Chart(chart_data).mark_bar(cornerRadiusTopLeft=5, cornerRadiusTopRight=5).encode(
        x=alt.X("Szenario", axis=alt.Axis(labelAngle=0, title="")),
        y=alt.Y("Kosten in EUR", title="Gebühren in €"),
        color=alt.condition(
            alt.datum.Szenario == 'Status Quo (Sparkasse)',
            alt.value('#ef4444'),     # Rot für hohe Kosten
            alt.value('#22c55e')      # Grün für optimierte Kosten
        )
    ).properties(height=300)
    
    st.altair_chart(chart, use_container_width=True)

with col_info:
    st.subheader(":material/insights: Analytische Insights")
    st.info(f"**Break-Even Point:** Bei eurem Ticketpreis amortisiert sich ein Firmenkonto bereits ab dem **ersten** zahlenden US/UK-Kunden.")
    st.info("**Liquiditäts-Vorteil:** Durch die 250k € Kapitaldecke könnt ihr das Auszahlungsintervall auf 'monatlich' belassen. Das minimiert die Payout-Fixgebühren von Stripe auf nahezu Null.")
    st.info("**UK Subsidiary:** Die Rechnung der Tochtergesellschaft kann verlustfrei über das lokale *Faster Payments (FPS)* Netzwerk aus dem GBP-Guthaben beglichen werden.")

st.divider()

# 3. ARCHITEKTUR / WORKFLOW (GEÄNDERT: Saubere Formatierung für Mermaid)
st.subheader(":material/account_tree: Ziel-Infrastruktur (Datenfluss)")

st.markdown("""
```mermaid
graph LR
    A[Kunden zahlen USD/GBP] -->|Processing| B[Stripe Plattform]
    B -->|Settlement Originalwährung| C[Multi-Währungs-Konto]
    C -->|Lokales ACH Netz| D[US Freelancer]
    C -->|Lokales FPS Netz| E[UK Tochterfirma]
    B -->|EUR Subscriptions| F[Sparkasse Geschäftskonto]
    
    style B fill:#635BFF,stroke:#fff,stroke-width:2px,color:#fff
    style C fill:#10223A,stroke:#fff,stroke-width:2px,color:#fff
    style F fill:#E60000,stroke:#fff,stroke-width:2px,color:#fff

""")
4. ANBIETER MATRIX
with st.expander(":material/tune: Matrix: Welcher Anbieter passt zu uns?", expanded=True):
matrix_data = {
"Kriterium": ["Empfang USD (aus Stripe)", "UK FPS Überweisung", "DATEV-Anbindung", "Mitarbeiterkarten"],
"Airwallex": ["Kostenlos (Echte US-Routing-Nr.)", "Kostenlos", "Nativ integriert", "Kostenlos + Cashback"],
"Wise Business": ["Kostenlos (Echte US-Routing-Nr.)", "Geringe Fixgebühr", "Export / Drittanbieter", "Einmalige Gebühr"],
"Revolut Business": ["Kostenlos (Partner-Banken)", "Inklusive (bis Limit)", "Standard-Export", "Inklusive"]
}
st.table(pd.DataFrame(matrix_data))

