```python
import streamlit as st
import pandas as pd
import altair as alt

# --- SEITENKONFIGURATION ---
st.set_page_config(
    page_title="Treasury Optimizer", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# --- KONSTANTEN & ANNAHMEN ---
AOV_USD = 1499
AOV_GBP = 999
FX_RATE_USD_EUR = 0.92 
FX_RATE_GBP_EUR = 1.17

# --- HEADER ---
st.title(":material/account_balance: Strategisches Multi-Währungs-Setup")
st.markdown("Dashboard zur Simulation der Stripe-Zahlungsströme und Optimierung der FX-Margen.")
st.divider()

# --- SIDEBAR: INPUT PARAMETER ---
with st.sidebar:
    st.header(":material/settings: Parameter")
    
    st.subheader("Monatliches Wachstum")
    us_customers = st.slider("Neue US-Abonnenten", min_value=1, max_value=100, value=15, help="Anzahl der Kunden à $1.499")
    uk_customers = st.slider("Neue UK-Abonnenten", min_value=1, max_value=100, value=10, help="Anzahl der Kunden à £999")
    
    st.subheader("Stripe Auszahlungs-Intervall")
    payout_freq = st.selectbox(
        "Wie oft soll Stripe auf das Multi-Währungskonto auszahlen?", 
        options=["Monatlich (Empfohlen)", "Wöchentlich", "Täglich"],
        help="Da aktuell 250k € Überbrückungskapital für Gehälter vorhanden sind, wird 'Monatlich' empfohlen, um die Fixgebühren pro Stripe-Payout zu minimieren."
    )
    
    # Logik für das Dropdown
    if payout_freq == "Monatlich (Empfohlen)":
        payouts_per_month = 1
    elif payout_freq == "Wöchentlich":
        payouts_per_month = 4
    else:
        payouts_per_month = 20 

# --- BERECHNUNGSLOGIK ---
vol_usd = us_customers * AOV_USD
vol_gbp = uk_customers * AOV_GBP
vol_eur_total = (vol_usd * FX_RATE_USD_EUR) + (vol_gbp * FX_RATE_GBP_EUR)

cost_status_quo_eur = vol_eur_total * 0.02
cost_new_usd = (vol_usd * 0.0125) + (payouts_per_month * 1.50)
cost_new_gbp = (vol_gbp * 0.01) + (payouts_per_month * 0.50)
cost_new_eur = (cost_new_usd * FX_RATE_USD_EUR) + (cost_new_gbp * FX_RATE_GBP_EUR)

savings_eur = cost_status_quo_eur - cost_new_eur

# --- MAIN DASHBOARD ---
# 1. KPIs
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="Umsatz-Volumen (Monat)", value=f"€ {vol_eur_total:,.0f}", help=f"Zusammengesetzt aus ${vol_usd:,.0f} und £{vol_gbp:,.0f}")
with col2:
    st.metric(label="Verlust im Standard-Setup", value=f"€ {cost_status_quo_eur:,.0f}", help="2% Umrechnungsgebühr, die Stripe bei direkter Auszahlung auf die Sparkasse einbehält.")
with col3:
    st.metric(label="Netto-Ersparnis (Monat)", value=f"€ {savings_eur:,.0f}", delta="Zusätzliche Marge", help="Ersparnis nach Abzug aller neuen Stripe-Payout-Gebühren für das Multi-Währungskonto.")

st.divider()

# 2. VISUALISIERUNG & BREAK-EVEN
col_chart, col_info = st.columns([2, 1])

with col_chart:
    st.subheader(":material/bar_chart: Kostenvergleich pro Monat")
    chart_data = pd.DataFrame({
        "Szenario": ["Status Quo (Sparkasse)", "Neues Setup (Multi-Währung)"],
        "Kosten in EUR": [cost_status_quo_eur, cost_new_eur]
    })
    
    chart = alt.Chart(chart_data).mark_bar(cornerRadiusTopLeft=5, cornerRadiusTopRight=5).encode(
        x=alt.X("Szenario", axis=alt.Axis(labelAngle=0, title="")),
        y=alt.Y("Kosten in EUR", title="Gebühren in €"),
        color=alt.condition(
            alt.datum.Szenario == 'Status Quo (Sparkasse)',
            alt.value('#ef4444'),     
            alt.value('#22c55e')      
        )
    ).properties(height=300)
    st.altair_chart(chart, use_container_width=True)

with col_info:
    st.subheader(":material/insights: Analytische Insights")
    st.info(f"**Break-Even Point:** Bei eurem Ticketpreis von $1.499 amortisiert sich selbst ein kostenpflichtiges Firmenkonto bereits ab dem **ersten** zahlenden US-Kunden.")
    st.info("**Liquiditäts-Vorteil:** Durch die 250k € Kapitaldecke könnt ihr das Auszahlungsintervall auf 'monatlich' belassen. Das minimiert die Payout-Fixgebühren von Stripe auf nahezu Null.")
    st.info("**UK Subsidiary:** Die Rechnung der Tochtergesellschaft kann verlustfrei über das lokale *Faster Payments (FPS)* Netzwerk aus dem GBP-Guthaben beglichen werden.")

st.divider()

# 3. ARCHITEKTUR / WORKFLOW
st.subheader(":material/account_tree: Ziel-Infrastruktur (Datenfluss)")

# Trick für die Darstellung, damit der Code-Block im Chat nicht bricht:
bt = "`" * 3
mermaid_code = f"""
{bt}mermaid
graph LR
    A[Kunden zahlen USD/GBP] -->|Processing| B[Stripe Plattform]
    B -->|Settlement Originalwährung| C[Multi-Währungs-Konto]
    C -->|Lokales ACH Netz| D[US Freelancer]
    C -->|Lokales FPS Netz| E[UK Tochterfirma]
    B -->|EUR Subscriptions| F[Sparkasse Geschäftskonto]
    
    style B fill:#635BFF,stroke:#fff,stroke-width:2px,color:#fff
    style C fill:#10223A,stroke:#fff,stroke-width:2px,color:#fff
    style F fill:#E60000,stroke:#fff,stroke-width:2px,color:#fff
{bt}
"""
st.markdown(mermaid_code)

# 4. ANBIETER MATRIX
with st.expander(":material/tune: Matrix: Welcher Anbieter passt zu uns?", expanded=True):
    matrix_data = {
        "Kriterium": ["Empfang USD (aus Stripe)", "UK FPS Überweisung", "DATEV-Anbindung", "Mitarbeiterkarten"],
        "Airwallex": ["Kostenlos (Echte US-Routing-Nr.)", "Kostenlos", "Nativ integriert", "Kostenlos + Cashback"],
        "Wise Business": ["Kostenlos (Echte US-Routing-Nr.)", "Geringe Fixgebühr", "Export / Drittanbieter", "Einmalige Gebühr"],
        "Revolut Business": ["Kostenlos (Partner-Banken)", "Inklusive (bis Limit)", "Standard-Export", "Inklusive"]
    }
    st.table(pd.DataFrame(matrix_data))

