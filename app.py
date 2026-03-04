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
        "subtitle": "Dashboard zur Simulation der Stripe-Zahlungsströme, Wachstums-Szenarien und Rücktausch-Effekte.",
        "sidebar_title": ":material/settings: Parameter",
        "market_us": "🇺🇸 US-Markt",
        "market_uk": "🇬🇧 UK-Markt",
        "exist_subs": "Bestehende Kunden",
        "new_subs": "Neue Kunden / Monat",
        "help_subs": "Reguläres Abo ($1.499 / £999)",
        "help_new_subs": "Inkl. einmaliger Setup-Gebühr ($2.500 / £2.500)",
        "payout_freq": "Stripe Auszahlungs-Intervall",
        "payout_help": "Empfohlen: Monatlich, um Stripe-Fixkosten zu minimieren.",
        "monthly": "Monatlich",
        "weekly": "Wöchentlich",
        "daily": "Täglich",
        "repat_title": "Rückführung in EUR (Repatriation)",
        "repat_label": "% Anteil, der zwingend in EUR zurückgetauscht werden muss",
        "repat_help": "Wenn das Überbrückungsbudget aufgebraucht ist und Fremdwährungen für deutsche Gehälter getauscht werden müssen.",
        "provider_select": ":material/account_balance_wallet: Ziel-Anbieter (Multi-Währung)",
        "provider_rates": "Dynamische Gebührensätze:",
        "rev_usd": "Gesamtumsatz (USD)",
        "rev_gbp": "Gesamtumsatz (GBP)",
        "net_savings": "Netto-Ersparnis (Monat)",
        "savings_percent": "vom Umsatz",
        "annual_savings": "Jahres-Ersparnis (p.a.)",
        "base_fees": "Stripe Basis-Processing",
        "base_fees_help": "Unvermeidbare Standard-Gebühren (ca. 3.25% + 0.30€) für Kreditkarten.",
        "chart_title": ":material/bar_chart: Kostenaufschlüsselung (in EUR)",
        "insights_title": ":material/insights: Analytische Insights",
        "insight_repat": "**Rücktausch-Falle:** Wenn ihr {pct}% zurücktauscht, zahlt ihr {fx_cost}€ an {provider} FX-Gebühren. Das schmälert die Ersparnis massiv.",
        "insight_awx": "**Airwallex Bonus:** Durch euer Volumen von >10.000€ entfällt die Airwallex-Grundgebühr von 19€ automatisch.",
        "insight_breakeven": "**Setup-Boost:** Durch die hohen Einrichtungsgebühren bei Neukunden ist das Volumen extrem schnell in profitablen Zonen.",
        "flow_title": ":material/account_tree: Ziel-Infrastruktur (Datenfluss)",
        "matrix_title": ":material/tune: Detail-Matrix der Anbieter",
        "scen_sq": "Status Quo (Sparkasse)",
        "scen_new": "Neues Setup ({provider})",
        "cat_base": "1. Basis-Processing",
        "cat_fx": "2. Stripe FX / Payout Gebühr",
        "cat_prov": "3. Provider Fixkosten",
        "cat_repat": "4. Provider FX (Rücktausch)",
        "rate_base": "Grundgebühr / Monat",
        "rate_transfer": "Lokale Überweisung (US/UK)",
        "rate_fx": "FX-Aufschlag (Rücktausch)"
    },
    "EN": {
        "title": ":material/account_balance: Strategic Multi-Currency Setup",
        "subtitle": "Dashboard for simulating Stripe payment flows, growth scenarios, and repatriation effects.",
        "sidebar_title": ":material/settings: Parameters",
        "market_us": "🇺🇸 US Market",
        "market_uk": "🇬🇧 UK Market",
        "exist_subs": "Existing Customers",
        "new_subs": "New Customers / Month",
        "help_subs": "Regular sub ($1,499 / £999)",
        "help_new_subs": "Incl. one-time setup fee ($2,500 / £2,500)",
        "payout_freq": "Stripe Payout Frequency",
        "payout_help": "Recommended: Monthly, to minimize Stripe fixed costs.",
        "monthly": "Monthly",
        "weekly": "Weekly",
        "daily": "Daily",
        "repat_title": "Repatriation to EUR",
        "repat_label": "% Share that must be converted back to EUR",
        "repat_help": "If bridge capital is depleted and foreign currency must be converted for German payroll.",
        "provider_select": ":material/account_balance_wallet: Target Provider",
        "provider_rates": "Dynamic Fee Structure:",
        "rev_usd": "Total Revenue (USD)",
        "rev_gbp": "Total Revenue (GBP)",
        "net_savings": "Net Savings (Monthly)",
        "savings_percent": "of revenue",
        "annual_savings": "Annual Savings (p.a.)",
        "base_fees": "Stripe Base Processing",
        "base_fees_help": "Unavoidable standard fees (approx. 3.25% + €0.30) for credit cards.",
        "chart_title": ":material/bar_chart: Cost Breakdown (in EUR)",
        "insights_title": ":material/insights: Analytical Insights",
        "insight_repat": "**Repatriation Trap:** By converting {pct}% back, you pay {fx_cost}€ in {provider} FX fees. This heavily reduces savings.",
        "insight_awx": "**Airwallex Bonus:** Because your volume exceeds €10,000, the €19 Airwallex base fee is automatically waived.",
        "insight_breakeven": "**Setup Boost:** Thanks to high setup fees for new customers, the volume quickly reaches highly profitable zones.",
        "flow_title": ":material/account_tree: Target Infrastructure (Data Flow)",
        "matrix_title": ":material/tune: Provider Detail Matrix",
        "scen_sq": "Status Quo (Local Bank)",
        "scen_new": "New Setup ({provider})",
        "cat_base": "1. Base Processing",
        "cat_fx": "2. Stripe FX / Payout Fee",
        "cat_prov": "3. Provider Fixed Cost",
        "cat_repat": "4. Provider FX (Conversion)",
        "rate_base": "Base Fee / Month",
        "rate_transfer": "Local Transfer (US/UK)",
        "rate_fx": "FX Markup (Conversion)"
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
    us_exist = st.number_input(f"{t('exist_subs')} (US)", min_value=0, value=10, step=1, help=t("help_subs"))
    us_new = st.number_input(f"{t('new_subs')} (US)", min_value=0, value=2, step=1, help=t("help_new_subs"))
    
    st.subheader(t("market_uk"))
    uk_exist = st.number_input(f"{t('exist_subs')} (UK)", min_value=0, value=5, step=1, help=t("help_subs"))
    uk_new = st.number_input(f"{t('new_subs')} (UK)", min_value=0, value=1, step=1, help=t("help_new_subs"))
    
    st.divider()
    
    st.subheader(t("repat_title"))
    repatriation_pct = st.slider(t("repat_label"), 0, 100, 0, step=5, help=t("repat_help"))
    
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

# --- BERECHNUNGSLOGIK ---
# 1. Volumina (Abo-Bestand + Abo-Neu + Setup-Gebühr-Neu)
total_us_customers = us_exist + us_new
total_uk_customers = uk_exist + uk_new

vol_usd = (total_us_customers * AOV_USD) + (us_new * SETUP_FEE_USD)
vol_gbp = (total_uk_customers * AOV_GBP) + (uk_new * SETUP_FEE_GBP)
vol_eur_total = (vol_usd * FX_RATE_USD_EUR) + (vol_gbp * FX_RATE_GBP_EUR)

# 2. Unvermeidbare Basis-Gebühren (Stripe Processing: ca. 3.25% + 0.30€ pro Transaktion)
transactions_usd = total_us_customers 
transactions_gbp = total_uk_customers
base_fee_usd_processing = (vol_usd * 0.0325) + (transactions_usd * 0.30)
base_fee_gbp_processing = (vol_gbp * 0.025) + (transactions_gbp * 0.30) 
base_fee_eur_total = (base_fee_usd_processing * FX_RATE_USD_EUR) + (base_fee_gbp_processing * FX_RATE_GBP_EUR)

# 3. Status Quo (2% Stripe Standard Konvertierung)
fx_cost_status_quo_eur = (vol_usd * FX_RATE_USD_EUR * 0.02) + (vol_gbp * FX_RATE_GBP_EUR * 0.02)
total_cost_sq_eur = base_fee_eur_total + fx_cost_status_quo_eur

# 4. Neues Setup (Stripe Payout Fees auf Fremdwährungskonten)
stripe_payout_cost_usd = (vol_usd * 0.0125) + (payouts_per_month * 1.50) if vol_usd > 0 else 0
stripe_payout_cost_gbp = (vol_gbp * 0.01) + (payouts_per_month * 0.50) if vol_gbp > 0 else 0
stripe_payout_total_eur = (stripe_payout_cost_usd * FX_RATE_USD_EUR) + (stripe_payout_cost_gbp * FX_RATE_GBP_EUR)

# 5. Anbieter-spezifische Fix- & Transaktionskosten (Dynamisch)
provider_monthly_fee_eur = 0
provider_transfer_fee_eur = 0
provider_fx_cost_eur = 0

# Volumen für Rücktausch in EUR
repat_vol_usd = vol_usd * (repatriation_pct / 100)
repat_vol_gbp = vol_gbp * (repatriation_pct / 100)
repat_vol_eur = (repat_vol_usd * FX_RATE_USD_EUR) + (repat_vol_gbp * FX_RATE_GBP_EUR)

if provider == "Airwallex":
    # 19€ Explore Plan, ABER kostenlos ab 10.000€ Volumen!
    provider_monthly_fee_eur = 19 if vol_eur_total < 10000 else 0
    provider_transfer_fee_eur = 0 
    provider_fx_cost_eur = (repat_vol_usd * FX_RATE_USD_EUR * 0.005) + (repat_vol_gbp * FX_RATE_GBP_EUR * 0.005) # ca 0.5% FX
    r_base = f"€ 19 (entfällt, da Umsatz > 10k €)" if vol_eur_total >= 10000 and lang == "DE" else f"€ 19 (waived, revenue > 10k €)" if vol_eur_total >= 10000 else "€ 19"
    r_trans = "€ 0 (Kostenlos)" if lang == "DE" else "€ 0 (Free)"
    r_fx = "~ 0.5 %"

elif provider == "Wise Business":
    provider_monthly_fee_eur = 0 
    provider_transfer_fee_eur = (1 * 0.39 * FX_RATE_USD_EUR) + (1 * 0.35 * FX_RATE_GBP_EUR) 
    provider_fx_cost_eur = (repat_vol_usd * FX_RATE_USD_EUR * 0.0043) + (repat_vol_gbp * FX_RATE_GBP_EUR * 0.0043) # ca 0.43% FX
    r_base = "€ 0 (Einmalig 50€ Setup)" if lang == "DE" else "€ 0 (€50 one-time setup)"
    r_trans = "~ 0.35£ / 0.39$ pro ÜW" if lang == "DE" else "~ £0.35 / $0.39 per transfer"
    r_fx = "~ 0.43 %"

elif provider == "Revolut Business":
    provider_monthly_fee_eur = 25 
    provider_transfer_fee_eur = 0 
    # Grow Plan: FX kostenlos bis 10k GBP (~11.7k EUR), danach 0.6%
    fx_subject_to_fee = max(0, repat_vol_eur - 11700)
    provider_fx_cost_eur = fx_subject_to_fee * 0.006
    r_base = "€ 25 (Grow Plan)"
    r_trans = "€ 0 (im Freibetrag)" if lang == "DE" else "€ 0 (in allowance)"
    r_fx = "0 % (bis 10k £, dann 0.6%)" if lang == "DE" else "0 % (up to £10k, then 0.6%)"

total_cost_new_eur = base_fee_eur_total + stripe_payout_total_eur + provider_monthly_fee_eur + provider_transfer_fee_eur + provider_fx_cost_eur

# 6. Ersparnis berechnen
savings_eur = total_cost_sq_eur - total_cost_new_eur
savings_percent = (savings_eur / vol_eur_total * 100) if vol_eur_total > 0 else 0
annual_savings = savings_eur * 12

# Konditionen anzeigen
st.caption(t("provider_rates"))
r1, r2, r3 = st.columns(3)
r1.info(f"**{t('rate_base')}:**\n\n{r_base}")
r2.info(f"**{t('rate_transfer')}:**\n\n{r_trans}")
r3.info(f"**{t('rate_fx')}:**\n\n{r_fx}")

st.divider()

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
        delta=f"{savings_percent:.1f}% {t('savings_percent')}",
        delta_color="normal" if savings_eur > 0 else "inverse"
    )
with col4:
    st.metric(
        label=t("annual_savings"), 
        value=f"€ {annual_savings:,.0f}",
        delta="12 Months ROI",
        delta_color="normal" if annual_savings > 0 else "inverse"
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
        {"Szenario": t("scen_sq"), "Kostenart": t("cat_repat"), "Betrag": 0},
        
        {"Szenario": t("scen_new").format(provider=provider), "Kostenart": t("cat_base"), "Betrag": base_fee_eur_total},
        {"Szenario": t("scen_new").format(provider=provider), "Kostenart": t("cat_fx"), "Betrag": stripe_payout_total_eur},
        {"Szenario": t("scen_new").format(provider=provider), "Kostenart": t("cat_prov"), "Betrag": provider_monthly_fee_eur + provider_transfer_fee_eur},
        {"Szenario": t("scen_new").format(provider=provider), "Kostenart": t("cat_repat"), "Betrag": provider_fx_cost_eur},
    ])
    
    domain = [t("cat_base"), t("cat_fx"), t("cat_prov"), t("cat_repat")]
    range_ = ['#94a3b8', '#ef4444', '#f59e0b', '#8b5cf6'] 
    
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
    
    if provider == "Airwallex" and vol_eur_total >= 10000:
        st.success(t("insight_awx"))
        
    if repatriation_pct > 0:
        st.warning(t("insight_repat").format(pct=repatriation_pct, fx_cost=f"{provider_fx_cost_eur:,.0f}", provider=provider))
    else:
        st.info(t("insight_breakeven"))
        
    st.success(t("insight_annual").format(annual=annual_savings))

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
