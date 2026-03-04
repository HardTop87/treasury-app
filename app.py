import streamlit as st
import pandas as pd
import altair as alt

# --- SEITENKONFIGURATION ---
st.set_page_config(
    page_title="Treasury Optimizer", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# --- SPRACHSTEUERUNG (Zweisprachigkeit) ---
# Language Toggle in der Top-Bar
col1, col2 = st.columns([8, 2])
with col2:
    lang_toggle = st.radio(
        "Language", 
        ["🇩🇪 DE", "🇬🇧 EN"], 
        horizontal=True, 
        label_visibility="collapsed"
    )
lang = "DE" if "DE" in lang_toggle else "EN"

# Übersetzungs-Wörterbuch
T = {
    "DE": {
        "title": ":material/account_balance: Strategisches Multi-Währungs-Setup",
        "subtitle": "Dashboard zur Simulation der Stripe-Zahlungsströme und Optimierung der FX-Margen.",
        "sidebar_title": ":material/settings: Parameter",
        "growth": "Monatliches Wachstum",
        "us_subs": "Anzahl US-Abonnenten",
        "uk_subs": "Anzahl UK-Abonnenten",
        "payout_freq": "Stripe Auszahlungs-Intervall",
        "payout_help": "Da aktuell 250k € Überbrückungskapital für Gehälter vorhanden sind, wird 'Monatlich' empfohlen.",
        "monthly": "Monatlich (Empfohlen)",
        "weekly": "Wöchentlich",
        "daily": "Täglich",
        "provider_select": "Ziel-Anbieter (Multi-Währung)",
        "rev_usd": "Umsatz (USD)",
        "rev_gbp": "Umsatz (GBP)",
        "net_savings": "Netto-Ersparnis (Monat)",
        "savings_percent": "vom Umsatz",
        "annual_savings": "Jahres-Ersparnis (p.a.)",
        "base_fees": "Unvermeidbare Stripe Basis-Gebühren",
        "base_fees_help": "Standard Payment-Processing Gebühren für internationale Karten (ca. 3.25% + 0.30€). Diese fallen immer an, unabhängig vom Setup.",
        "chart_title": ":material/bar_chart: Kostenaufschlüsselung (in EUR)",
        "insights_title": ":material/insights: Analytische Insights",
        "insight_breakeven": "**Break-Even Point:** Bei diesem Ticketpreis amortisiert sich jegliche Kontoführungsgebühr bereits ab dem **ersten** zahlenden US/UK-Kunden.",
        "insight_annual": "**Jahres-Hebel:** Auf 12 Monate hochgerechnet schützt das Setup ca. **€ {annual:,.0f}** vor der FX-Erosion.",
        "insight_provider": "**Anbieter-Wahl:** {provider} wurde ausgewählt. Die Berechnung berücksichtigt {fees}.",
        "flow_title": ":material/account_tree: Ziel-Infrastruktur (Datenfluss)",
        "matrix_title": ":material/tune: Matrix: Welcher Anbieter passt zu uns?",
        "scen_sq": "Status Quo (Sparkasse)",
        "scen_new": "Neues Setup ({provider})",
        "cat_base": "1. Basis-Gebühren (Processing)",
        "cat_fx": "2. FX- & Stripe-Payout Gebühren",
        "cat_prov": "3. Anbieter-Fixkosten",
    },
    "EN": {
        "title": ":material/account_balance: Strategic Multi-Currency Setup",
        "subtitle": "Dashboard for simulating Stripe payment flows and optimizing FX margins.",
        "sidebar_title": ":material/settings: Parameters",
        "growth": "Monthly Growth",
        "us_subs": "Number of US Subscribers",
        "uk_subs": "Number of UK Subscribers",
        "payout_freq": "Stripe Payout Frequency",
        "payout_help": "Since there is currently €250k in bridge capital for payroll, 'Monthly' is recommended.",
        "monthly": "Monthly (Recommended)",
        "weekly": "Weekly",
        "daily": "Daily",
        "provider_select": "Target Provider (Multi-Currency)",
        "rev_usd": "Revenue (USD)",
        "rev_gbp": "Revenue (GBP)",
        "net_savings": "Net Savings (Monthly)",
        "savings_percent": "of revenue",
        "annual_savings": "Annual Savings (p.a.)",
        "base_fees": "Unavoidable Stripe Base Fees",
        "base_fees_help": "Standard payment processing fees for international cards (approx. 3.25% + 0.30€). These always apply, regardless of the setup.",
        "chart_title": ":material/bar_chart: Cost Breakdown (in EUR)",
        "insights_title": ":material/insights: Analytical Insights",
        "insight_breakeven": "**Break-Even Point:** With this ticket price, any account management fee pays for itself from the **first** paying US/UK customer.",
        "insight_annual": "**Annual Leverage:** Extrapolated over 12 months, the setup protects approx. **€ {annual:,.0f}** from FX erosion.",
        "insight_provider": "**Provider Choice:** {provider} was selected. The calculation accounts for {fees}.",
        "flow_title": ":material/account_tree: Target Infrastructure (Data Flow)",
        "matrix_title": ":material/tune: Matrix: Which provider suits us?",
        "scen_sq": "Status Quo (Local Bank)",
        "scen_new": "New Setup ({provider})",
        "cat_base": "1. Base Fees (Processing)",
        "cat_fx": "2. FX & Stripe Payout Fees",
        "cat_prov": "3. Provider Fixed Costs",
    }
}

def t(key):
    return T[lang][key]

# --- KONSTANTEN & AKTUELLE WECHSELKURSE (März 2026) ---
AOV_USD = 1499
AOV_GBP = 999
FX_RATE_USD_EUR = 0.92  
FX_RATE_GBP_EUR = 1.17  

# --- HEADER ---
st.title(t("title"))
st.markdown(t("subtitle"))
st.divider()

# --- SIDEBAR: INPUT PARAMETER ---
with st.sidebar:
    st.header(t("sidebar_title"))
    
    st.subheader(t("growth"))
    us_customers = st.number_input(t("us_subs"), min_value=0, value=15, step=1)
    uk_customers = st.number_input(t("uk_subs"), min_value=0, value=10, step=1)
    
    st.subheader(t("payout_freq"))
    payout_freq = st.selectbox(
        t("payout_freq"), 
        options=[t("monthly"), t("weekly"), t("daily")],
        help=t("payout_help"),
        label_visibility="collapsed"
    )
    
    st.subheader(t("provider_select"))
    provider = st.selectbox(
        t("provider_select"),
        options=["Airwallex", "Wise Business", "Revolut Business"],
        label_visibility="collapsed"
    )
    
    # Logik für das Dropdown
    if payout_freq == t("monthly"):
        payouts_per_month = 1
    elif payout_freq == t("weekly"):
        payouts_per_month = 4
    else:
        payouts_per_month = 20 # ca. Werktage

# --- BERECHNUNGSLOGIK ---
# 1. Volumina
vol_usd = us_customers * AOV_USD
vol_gbp = uk_customers * AOV_GBP
vol_eur_total = (vol_usd * FX_RATE_USD_EUR) + (vol_gbp * FX_RATE_GBP_EUR)

# 2. Unvermeidbare Basis-Gebühren (Stripe Processing: EWR -> Non-EWR Cards ca. 3.25% + 0.30€)
# Wir nehmen einen pauschalen Mix an
base_fee_usd_processing = (vol_usd * 0.0325) + (us_customers * 0.30)
base_fee_gbp_processing = (vol_gbp * 0.025) + (uk_customers * 0.30) # UK etwas günstiger
base_fee_eur_total = (base_fee_usd_processing * FX_RATE_USD_EUR) + (base_fee_gbp_processing * FX_RATE_GBP_EUR)

# 3. Status Quo (2% Stripe Standard Konvertierung oben drauf)
fx_cost_status_quo_eur = (vol_usd * FX_RATE_USD_EUR * 0.02) + (vol_gbp * FX_RATE_GBP_EUR * 0.02)
total_cost_sq_eur = base_fee_eur_total + fx_cost_status_quo_eur

# 4. Neues Setup (Stripe Payout Fees auf Fremdwährungskonten)
# USD: 1% Alt Currency + 0.25% Cross Border + $1.50 pro Auszahlung
stripe_payout_cost_usd = (vol_usd * 0.0125) + (payouts_per_month * 1.50) if vol_usd > 0 else 0
# GBP: 1% Alt Currency + £0.50 pro Auszahlung
stripe_payout_cost_gbp = (vol_gbp * 0.01) + (payouts_per_month * 0.50) if vol_gbp > 0 else 0

# 5. Anbieter-spezifische Kosten (Neu!)
# Annahme: 1 Sammelüberweisung pro Monat an US Freelancer, 1 an UK Tochterfirma
provider_monthly_fee_eur = 0
provider_transfer_fee_eur = 0
prov_desc = ""

if provider == "Airwallex":
    provider_monthly_fee_eur = 0
    provider_transfer_fee_eur = 0 # Lokale Überweisungen sind kostenlos
    prov_desc = "0€ Basisgebühr & 0€ lokale Überweisungsgebühren" if lang == "DE" else "€0 base fee & €0 local transfer fees"
elif provider == "Wise Business":
    provider_monthly_fee_eur = 0 # (Ignorieren einmalige 50€ Setup)
    provider_transfer_fee_eur = (1 * 0.50 * FX_RATE_USD_EUR) + (1 * 0.50 * FX_RATE_GBP_EUR) # ca. 50 Cent pro lokaler ÜW
    prov_desc = "0€ Basisgebühr & minimale Transaktionsgebühren (~0.50€)" if lang == "DE" else "€0 base fee & minimal transaction fees (~€0.50)"
elif provider == "Revolut Business":
    provider_monthly_fee_eur = 25 # Grow Plan für sinnvolle Freibeträge
    provider_transfer_fee_eur = 2 * 0.20 # ca. 20 Cent nach Freibetrag
    prov_desc = "25€ monatliche Fixkosten & 0.20€ Transaktionsgebühren" if lang == "DE" else "€25 monthly fixed cost & €0.20 transaction fees"

fx_cost_new_eur = (stripe_payout_cost_usd * FX_RATE_USD_EUR) + (stripe_payout_cost_gbp * FX_RATE_GBP_EUR)
total_cost_new_eur = base_fee_eur_total + fx_cost_new_eur + provider_monthly_fee_eur + provider_transfer_fee_eur

# 6. Ersparnis berechnen
savings_eur = total_cost_sq_eur - total_cost_new_eur
savings_percent = (savings_eur / vol_eur_total * 100) if vol_eur_total > 0 else 0
annual_savings = savings_eur * 12

# --- MAIN DASHBOARD ---
# 1. KPIs
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label=t("rev_usd"), value=f"$ {vol_usd:,.0f}")
with col2:
    st.metric(label=t("rev_gbp"), value=f"£ {vol_gbp:,.0f}")
with col3:
    st.metric(
        label=t("net_savings"), 
        value=f"€ {savings_eur:,.0f}",
        delta=f"{savings_percent:.1f}% {t('savings_percent')}"
    )
with col4:
    st.metric(
        label=t("annual_savings"), 
        value=f"€ {annual_savings:,.0f}",
        delta="12 Months ROI"
    )

# Hinweis zu Basisgebühren
st.caption(f"ℹ️ **{t('base_fees')}: € {base_fee_eur_total:,.0f}**. {t('base_fees_help')}")
st.divider()

# 2. VISUALISIERUNG & BREAK-EVEN
col_chart, col_info = st.columns([2, 1])

with col_chart:
    st.subheader(t("chart_title"))
    
    # Daten für gestapeltes Diagramm
    chart_data = pd.DataFrame([
        {"Szenario": t("scen_sq"), "Kostenart": t("cat_base"), "Betrag": base_fee_eur_total},
        {"Szenario": t("scen_sq"), "Kostenart": t("cat_fx"), "Betrag": fx_cost_status_quo_eur},
        {"Szenario": t("scen_sq"), "Kostenart": t("cat_prov"), "Betrag": 0},
        
        {"Szenario": t("scen_new").format(provider=provider), "Kostenart": t("cat_base"), "Betrag": base_fee_eur_total},
        {"Szenario": t("scen_new").format(provider=provider), "Kostenart": t("cat_fx"), "Betrag": fx_cost_new_eur},
        {"Szenario": t("scen_new").format(provider=provider), "Kostenart": t("cat_prov"), "Betrag": provider_monthly_fee_eur + provider_transfer_fee_eur},
    ])
    
    # Altair Gestapeltes Balkendiagramm
    domain = [t("cat_base"), t("cat_fx"), t("cat_prov")]
    range_ = ['#94a3b8', '#ef4444', '#f59e0b'] # Grau (Basis), Rot (FX/Verlust), Orange (Provider)
    
    chart = alt.Chart(chart_data).mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3).encode(
        x=alt.X("Szenario:N", axis=alt.Axis(labelAngle=0, title="")),
        y=alt.Y("Betrag:Q", title="EUR (€)"),
        color=alt.Color("Kostenart:N", scale=alt.Scale(domain=domain, range=range_), legend=alt.Legend(orient="bottom", title="")),
        order=alt.Order('Kostenart:N', sort='ascending'),
        tooltip=[alt.Tooltip("Kostenart:N"), alt.Tooltip("Betrag:Q", format=",.2f")]
    ).properties(height=350)
    
    st.altair_chart(chart, width="stretch")

with col_info:
    st.subheader(t("insights_title"))
    st.success(t("insight_annual").format(annual=annual_savings))
    st.info(t("insight_provider").format(provider=provider, fees=prov_desc))
    st.info(t("insight_breakeven"))

st.divider()

# 3. ARCHITEKTUR / WORKFLOW
st.subheader(t("flow_title"))

mermaid_html = """
<div class="mermaid" style="font-family: sans-serif; display: flex; justify-content: center;">
graph LR
    A[Clients USD/GBP] -->|Processing| B[Stripe Platform]
    B -->|Settlement Original Currency| C[Multi-Currency-Account]
    C -->|Local ACH Network| D[US Freelancer]
    C -->|Local FPS Network| E[UK Subsidiary]
    B -->|EUR Subscriptions| F[Local Bank / Sparkasse]
    
    style B fill:#635BFF,stroke:#fff,stroke-width:2px,color:#fff
    style C fill:#10223A,stroke:#fff,stroke-width:2px,color:#fff
    style F fill:#E60000,stroke:#fff,stroke-width:2px,color:#fff
</div>
<script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
<script>mermaid.initialize({startOnLoad:true});</script>
"""
st.components.v1.html(mermaid_html, height=250)

# 4. ANBIETER MATRIX
with st.expander(t("matrix_title"), expanded=True):
    # Einfache statische Matrix, bei Bedarf auch ins Dictionary auslagerbar
    matrix_data = {
        "Kriterium / Criterion": ["Empfang USD (aus Stripe)", "UK FPS Überweisung", "DATEV-Anbindung", "Mitarbeiterkarten"],
        "Airwallex": ["Kostenlos (Echte US-Routing-Nr.)", "Kostenlos", "Nativ integriert", "Kostenlos + Cashback"],
        "Wise Business": ["Kostenlos (Echte US-Routing-Nr.)", "Geringe Fixgebühr", "Export / Drittanbieter", "Einmalige Gebühr"],
        "Revolut Business": ["Kostenlos (Partner-Banken)", "Inklusive (bis Limit)", "Standard-Export", "Inklusive"]
    }
    st.table(pd.DataFrame(matrix_data))
