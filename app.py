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
        "subtitle": "Dashboard zur Simulation der Stripe-Zahlungsströme, Wachstums-Szenarien und Optimierung der FX-Margen.",
        "sidebar_title": ":material/settings: Parameter",
        "market_us": "🇺🇸 US-Markt",
        "market_uk": "🇬🇧 UK-Markt",
        "exist_subs": "Bestehende Kunden",
        "new_subs": "Neue Kunden / Monat",
        "help_subs": "Reguläres Abo",
        "help_new_subs": "Inkl. $2.500 einmalige Einrichtungsgebühr",
        "help_new_subs_uk": "Inkl. £2.500 einmalige Einrichtungsgebühr",
        "payout_freq": "Stripe Auszahlungs-Intervall",
        "payout_help": "Da aktuell 250k € Überbrückungskapital für Gehälter vorhanden sind, wird 'Monatlich' empfohlen.",
        "monthly": "Monatlich (Empfohlen)",
        "weekly": "Wöchentlich",
        "daily": "Täglich",
        "provider_select": ":material/account_balance_wallet: Ziel-Anbieter (Multi-Währung) auswählen",
        "provider_rates": "Gebührensätze des gewählten Anbieters:",
        "rev_usd": "Gesamtumsatz (USD)",
        "rev_gbp": "Gesamtumsatz (GBP)",
        "net_savings": "Netto-Ersparnis (Monat)",
        "savings_percent": "vom Umsatz",
        "annual_savings": "Jahres-Ersparnis (p.a.)",
        "base_fees": "Unvermeidbare Stripe Basis-Gebühren",
        "base_fees_help": "Standard Payment-Processing (ca. 3.25% + 0.30€) für Abos und Einrichtungsgebühren.",
        "chart_title": ":material/bar_chart: Kostenaufschlüsselung (in EUR)",
        "insights_title": ":material/insights: Analytische Insights",
        "insight_breakeven": "**Break-Even Point:** Bei eurem Ticketpreis inkl. Setup-Gebühr amortisieren sich jegliche Kontoführungsgebühren ab dem **ersten** Neukunden sofort.",
        "insight_annual": "**Jahres-Hebel:** Auf 12 Monate hochgerechnet schützt das Setup ca. **€ {annual:,.0f}** vor der FX-Erosion.",
        "flow_title": ":material/account_tree: Ziel-Infrastruktur (Datenfluss)",
        "matrix_title": ":material/tune: Matrix: Welcher Anbieter passt zu uns?",
        "scen_sq": "Status Quo (Sparkasse)",
        "scen_new": "Neues Setup ({provider})",
        "cat_base": "1. Basis-Gebühren (Processing)",
        "cat_fx": "2. FX- & Stripe-Payout Gebühren",
        "cat_prov": "3. Anbieter-Fixkosten",
        "rate_base": "Grundgebühr / Monat",
        "rate_transfer": "Lokale Überweisung (US/UK)",
        "rate_fx": "FX-Aufschlag (Like-for-Like)"
    },
    "EN": {
        "title": ":material/account_balance: Strategic Multi-Currency Setup",
        "subtitle": "Dashboard for simulating Stripe payment flows, growth scenarios and optimizing FX margins.",
        "sidebar_title": ":material/settings: Parameters",
        "market_us": "🇺🇸 US Market",
        "market_uk": "🇬🇧 UK Market",
        "exist_subs": "Existing Customers",
        "new_subs": "New Customers / Month",
        "help_subs": "Regular Subscription",
        "help_new_subs": "Incl. $2,500 one-time setup fee",
        "help_new_subs_uk": "Incl. £2,500 one-time setup fee",
        "payout_freq": "Stripe Payout Frequency",
        "payout_help": "Since there is currently €250k in bridge capital for payroll, 'Monthly' is recommended.",
        "monthly": "Monthly (Recommended)",
        "weekly": "Weekly",
        "daily": "Daily",
        "provider_select": ":material/account_balance_wallet: Select Target Provider (Multi-Currency)",
        "provider_rates": "Fee structure of selected provider:",
        "rev_usd": "Total Revenue (USD)",
        "rev_gbp": "Total Revenue (GBP)",
        "net_savings": "Net Savings (Monthly)",
        "savings_percent": "of revenue",
        "annual_savings": "Annual Savings (p.a.)",
        "base_fees": "Unavoidable Stripe Base Fees",
        "base_fees_help": "Standard payment processing (approx. 3.25% + 0.30€) for subscriptions and setup fees.",
        "chart_title": ":material/bar_chart: Cost Breakdown (in EUR)",
        "insights_title": ":material/insights: Analytical Insights",
        "insight_breakeven": "**Break-Even Point:** With your ticket price incl. setup fee, any account management fees pay for themselves immediately from the **first** new customer.",
        "insight_annual": "**Annual Leverage:** Extrapolated over 12 months, the setup protects approx. **€ {annual:,.0f}** from FX erosion.",
        "flow_title": ":material/account_tree: Target Infrastructure (Data Flow)",
        "matrix_title": ":material/tune: Matrix: Which provider suits us?",
        "scen_sq": "Status Quo (Local Bank)",
        "scen_new": "New Setup ({provider})",
        "cat_base": "1. Base Fees (Processing)",
        "cat_fx": "2. FX & Stripe Payout Fees",
        "cat_prov": "3. Provider Fixed Costs",
        "rate_base": "Base Fee / Month",
        "rate_transfer": "Local Transfer (US/UK)",
        "rate_fx": "FX Markup (Like-for-Like)"
    }
}

def t(key):
    return T[lang][key]

# --- KONSTANTEN & AKTUELLE WECHSELKURSE (März 2026) ---
AOV_USD = 1499
AOV_GBP = 999
SETUP_FEE_USD = 2500
SETUP_FEE_GBP = 2500

FX_RATE_USD_EUR = 0.92  
FX_RATE_GBP_EUR = 1.17  

# --- HEADER ---
st.title(t("title"))
st.markdown(t("subtitle"))
st.divider()

# --- SIDEBAR: INPUT PARAMETER ---
with st.sidebar:
    st.header(t("sidebar_title"))
    
    st.subheader(t("market_us"))
    us_exist = st.number_input(f"{t('exist_subs')} (US)", min_value=0, value=15, step=1, help=t("help_subs"))
    us_new = st.number_input(f"{t('new_subs')} (US)", min_value=0, value=3, step=1, help=t("help_new_subs"))
    
    st.subheader(t("market_uk"))
    uk_exist = st.number_input(f"{t('exist_subs')} (UK)", min_value=0, value=10, step=1, help=t("help_subs"))
    uk_new = st.number_input(f"{t('new_subs')} (UK)", min_value=0, value=2, step=1, help=t("help_new_subs_uk"))
    
    st.divider()
    
    st.subheader(t("payout_freq"))
    payout_freq = st.selectbox(
        t("payout_freq"), 
        options=[t("monthly"), t("weekly"), t("daily")],
        help=t("payout_help"),
        label_visibility="collapsed"
    )
    
    if payout_freq == t("monthly"):
        payouts_per_month = 1
    elif payout_freq == t("weekly"):
        payouts_per_month = 4
    else:
        payouts_per_month = 20

# --- HAUPTBEREICH: ANBIETER-AUSWAHL ---
st.subheader(t("provider_select"))
provider = st.selectbox(
    "Provider",
    options=["Airwallex", "Wise Business", "Revolut Business"],
    label_visibility="collapsed"
)

# Anbieter-Konditionen direkt anzeigen
if provider == "Airwallex":
    r_base, r_trans, r_fx = "€ 0", "€ 0 (Kostenlos)", "0 %"
elif provider == "Wise Business":
    r_base, r_trans, r_fx = "€ 0 (Einmalig € 50)", "~ € 0.50 pro ÜW", "0 %"
elif provider == "Revolut Business":
    r_base, r_trans, r_fx = "€ 25 (Grow Plan)", "€ 0.20 pro ÜW", "0 %"

st.caption(t("provider_rates"))
r1, r2, r3 = st.columns(3)
r1.info(f"**{t('rate_base')}:** {r_base}")
r2.info(f"**{t('rate_transfer')}:** {r_trans}")
r3.info(f"**{t('rate_fx')}:** {r_fx}")

st.divider()

# --- BERECHNUNGSLOGIK ---
# 1. Volumina (Abo-Bestand + Abo-Neu + Setup-Gebühr-Neu)
total_us_customers = us_exist + us_new
total_uk_customers = uk_exist + uk_new

vol_usd = (total_us_customers * AOV_USD) + (us_new * SETUP_FEE_USD)
vol_gbp = (total_uk_customers * AOV_GBP) + (uk_new * SETUP_FEE_GBP)
vol_eur_total = (vol_usd * FX_RATE_USD_EUR) + (vol_gbp * FX_RATE_GBP_EUR)

# 2. Unvermeidbare Basis-Gebühren (Stripe Processing: ca. 3.25% + 0.30€)
base_fee_usd_processing = (vol_usd * 0.0325) + (total_us_customers * 0.30)
base_fee_gbp_processing = (vol_gbp * 0.025) + (total_uk_customers * 0.30) 
base_fee_eur_total = (base_fee_usd_processing * FX_RATE_USD_EUR) + (base_fee_gbp_processing * FX_RATE_GBP_EUR)

# 3. Status Quo (2% Stripe Standard Konvertierung oben drauf)
fx_cost_status_quo_eur = (vol_usd * FX_RATE_USD_EUR * 0.02) + (vol_gbp * FX_RATE_GBP_EUR * 0.02)
total_cost_sq_eur = base_fee_eur_total + fx_cost_status_quo_eur

# 4. Neues Setup (Stripe Payout Fees auf Fremdwährungskonten)
stripe_payout_cost_usd = (vol_usd * 0.0125) + (payouts_per_month * 1.50) if vol_usd > 0 else 0
stripe_payout_cost_gbp = (vol_gbp * 0.01) + (payouts_per_month * 0.50) if vol_gbp > 0 else 0

# 5. Anbieter-spezifische Kosten
provider_monthly_fee_eur = 0
provider_transfer_fee_eur = 0

if provider == "Airwallex":
    provider_monthly_fee_eur = 0
    provider_transfer_fee_eur = 0 
elif provider == "Wise Business":
    provider_monthly_fee_eur = 0 
    provider_transfer_fee_eur = (1 * 0.50 * FX_RATE_USD_EUR) + (1 * 0.50 * FX_RATE_GBP_EUR) 
elif provider == "Revolut Business":
    provider_monthly_fee_eur = 25 
    provider_transfer_fee_eur = 2 * 0.20 

fx_cost_new_eur = (stripe_payout_cost_usd * FX_RATE_USD_EUR) + (stripe_payout_cost_gbp * FX_RATE_GBP_EUR)
total_cost_new_eur = base_fee_eur_total + fx_cost_new_eur + provider_monthly_fee_eur + provider_transfer_fee_eur

# 6. Ersparnis berechnen
savings_eur = total_cost_sq_eur - total_cost_new_eur
savings_percent = (savings_eur / vol_eur_total * 100) if vol_eur_total > 0 else 0
annual_savings = savings_eur * 12

# --- DASHBOARD KPIs ---
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

st.caption(f"ℹ️ **{t('base_fees')}: € {base_fee_eur_total:,.0f}**. {t('base_fees_help')}")
st.divider()

# --- VISUALISIERUNG & BREAK-EVEN ---
col_chart, col_info = st.columns([2, 1])

with col_chart:
    st.subheader(t("chart_title"))
    
    chart_data = pd.DataFrame([
        {"Szenario": t("scen_sq"), "Kostenart": t("cat_base"), "Betrag": base_fee_eur_total},
        {"Szenario": t("scen_sq"), "Kostenart": t("cat_fx"), "Betrag": fx_cost_status_quo_eur},
        {"Szenario": t("scen_sq"), "Kostenart": t("cat_prov"), "Betrag": 0},
        
        {"Szenario": t("scen_new").format(provider=provider), "Kostenart": t("cat_base"), "Betrag": base_fee_eur_total},
        {"Szenario": t("scen_new").format(provider=provider), "Kostenart": t("cat_fx"), "Betrag": fx_cost_new_eur},
        {"Szenario": t("scen_new").format(provider=provider), "Kostenart": t("cat_prov"), "Betrag": provider_monthly_fee_eur + provider_transfer_fee_eur},
    ])
    
    domain = [t("cat_base"), t("cat_fx"), t("cat_prov")]
    range_ = ['#94a3b8', '#ef4444', '#f59e0b'] 
    
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
    st.info(t("insight_breakeven"))

st.divider()

# --- ARCHITEKTUR / WORKFLOW ---
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

# --- ANBIETER MATRIX ---
with st.expander(t("matrix_title"), expanded=True):
    matrix_data = {
        "Kriterium / Criterion": ["Empfang USD (aus Stripe)", "UK FPS Überweisung", "DATEV-Anbindung", "Mitarbeiterkarten"],
        "Airwallex": ["Kostenlos (Echte US-Routing-Nr.)", "Kostenlos", "Nativ integriert", "Kostenlos + Cashback"],
        "Wise Business": ["Kostenlos (Echte US-Routing-Nr.)", "Geringe Fixgebühr", "Export / Drittanbieter", "Einmalige Gebühr"],
        "Revolut Business": ["Kostenlos (Partner-Banken)", "Inklusive (bis Limit)", "Standard-Export", "Inklusive"]
    }
    st.table(pd.DataFrame(matrix_data))
