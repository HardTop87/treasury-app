import streamlit as st
import pandas as pd
import altair as alt
import urllib.request
import json

# --- SEITENKONFIGURATION ---
st.set_page_config(
    page_title="Treasury Optimizer", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# --- LIVE WECHSELKURSE ---
@st.cache_data(ttl=3600) # Cacht die Kurse für 1 Stunde
def get_live_rates():
    try:
        url = "https://open.er-api.com/v6/latest/EUR"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
            # API gibt Raten basierend auf 1 EUR zurück.
            # Umrechnung: 1 USD in EUR = 1 / (USD pro EUR)
            rate_usd_eur = 1 / data["rates"]["USD"]
            rate_gbp_eur = 1 / data["rates"]["GBP"]
            return rate_usd_eur, rate_gbp_eur, True
    except Exception as e:
        # Fallback Kurse, falls keine Internetverbindung
        return 0.92, 1.17, False

FX_RATE_USD_EUR, FX_RATE_GBP_EUR, rates_are_live = get_live_rates()

# --- SPRACHSTEUERUNG (Zweisprachigkeit) ---
col1, col2 = st.columns([8, 2])
with col2:
    lang_toggle = st.radio(
        "Language", 
        ["DE", "EN"], 
        horizontal=True, 
        label_visibility="collapsed"
    )
lang = "DE" if "DE" in lang_toggle else "EN"

# Übersetzungs-Wörterbuch
T = {
    "DE": {
        "title": ":material/account_balance: Strategisches Multi-Währungs-Setup",
        "subtitle": "Dashboard zur Simulation der Stripe-Zahlungsströme, Wachstums-Szenarien und Rücktausch-Effekte.",
        "live_rates": ":material/check_circle: Live-Wechselkurse aktiv",
        "offline_rates": ":material/warning: Offline-Kurse (Fallback)",
        "sidebar_title": ":material/settings: Parameter",
        "market_us": ":material/public: US-Markt",
        "market_uk": ":material/language: UK-Markt",
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
        "net_savings": "Netto-Ersparnis (Aktueller Monat)",
        "savings_percent": "vom Umsatz",
        "annual_savings": "Jahres-Ersparnis (p.a.)",
        "base_fees": "Stripe Basis-Processing",
        "base_fees_help": "Unvermeidbare Standard-Gebühren (ca. 3.25% + 0.30€) für Kreditkarten.",
        "proj_title": ":material/trending_up: Kumulierte 12-Monats-Auswertung",
        "proj_help": "Simuliert dynamisch das Wachstum über 12 Monate. Berücksichtigt, dass Abos kumulieren und Airwallex-Gebühren ggf. entfallen, sobald im Jahresverlauf 10k Umsatz geknackt werden.",
        "proj_sub": "Summe Subscriptions",
        "proj_setup": "Summe Onboarding",
        "proj_total": "Gesamt (12 Monate)",
        "chart_title": ":material/bar_chart: Kostenaufschlüsselung aktueller Monat (in EUR)",
        "insights_title": ":material/insights: Analytische Insights",
        "insight_repat": "**Rücktausch-Falle:** Wenn ihr {pct}% zurücktauscht, zahlt ihr im aktuellen Monat {fx_cost}€ an {provider} FX-Gebühren. Das schmälert die Ersparnis.",
        "insight_awx": "**Airwallex Bonus:** Durch euren aktuellen Umsatz von >10.000€ entfällt die Airwallex-Grundgebühr von 19€ automatisch.",
        "insight_awx_fee": "**Airwallex Gebühr:** Da der Umsatz im aktuellen Monat unter 10.000€ liegt, fallen 19€ Grundgebühr an. (Wird im 12-Monats-Plan dynamisch berechnet, sobald 10k erreicht sind).",
        "insight_breakeven": "**Setup-Boost:** Durch die hohen Einrichtungsgebühren bei Neukunden ist das Volumen extrem schnell in profitablen Zonen.",
        "insight_annual": "**Dynamischer Jahres-Hebel:** Unter Berücksichtigung des eingestellten monatlichen Wachstums schützt das Setup in den nächsten 12 Monaten ca. **€ {annual:,.0f}** vor der FX-Erosion.",
        "flow_title": ":material/account_tree: Ziel-Infrastruktur (Datenfluss)",
        "scen_sq": "Status Quo (Sparkasse)",
        "scen_new": "Neues Setup ({provider})",
        "cat_base": "1. Basis-Processing",
        "cat_fx": "2. Stripe FX / Payout Gebühr",
        "cat_prov": "3. Provider Fixkosten",
        "cat_repat": "4. Provider FX (Rücktausch)",
        "rate_base": "Grundgebühr / Monat",
        "rate_transfer": "Lokale Überweisung (US/UK)",
        "rate_fx": "FX-Aufschlag (Rücktausch)",
        
        "vs_title": ":material/balance: Vor- und Nachteile der Anbieter",
        "pro": "Vorteile",
        "con": "Nachteile",
        "awx_p1": "Lokale US/UK-Überweisungen komplett kostenlos",
        "awx_p2": "Native DATEV-Schnittstelle (GoBD-konform)",
        "awx_p3": "Guthabenverzinsung ('Yield') & Cashback auf Karten",
        "awx_c1": "Monatliche Gebühr (19€), wenn Umsatz unter 10k fällt",
        "awx_c2": "Plattform kann anfangs komplex wirken",
        "wise_p1": "Keinerlei monatliche Fixkosten, transparenteste App",
        "wise_p2": "Branchenbester Mid-Market Wechselkurs",
        "wise_p3": "Sehr schnelle und einfache Kontoeröffnung",
        "wise_c1": "Lokale Überweisungen (Payroll) kosten Gebühren (~0.50€)",
        "wise_c2": "DATEV-Anbindung nur über Umwege/Exporte",
        "rev_p1": "Sehr gute App mit starken Automatisierungen",
        "rev_p2": "FX-Freibeträge in den Bezahlplänen (Grow)",
        "rev_c1": "Mind. 25€ / Monat für einen sinnvollen Plan nötig",
        "rev_c2": "Lokale USD-Daten teils über Partnerbanken"
    },
    "EN": {
        "title": ":material/account_balance: Strategic Multi-Currency Setup",
        "subtitle": "Dashboard for simulating Stripe payment flows, growth scenarios, and repatriation effects.",
        "live_rates": ":material/check_circle: Live Exchange Rates Active",
        "offline_rates": ":material/warning: Offline Rates (Fallback)",
        "sidebar_title": ":material/settings: Parameters",
        "market_us": ":material/public: US Market",
        "market_uk": ":material/language: UK Market",
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
        "rev_usd": "Current Revenue (USD)",
        "rev_gbp": "Current Revenue (GBP)",
        "net_savings": "Net Savings (Current Month)",
        "savings_percent": "of revenue",
        "annual_savings": "Annual Savings (p.a.)",
        "base_fees": "Stripe Base Processing",
        "base_fees_help": "Unavoidable standard fees (approx. 3.25% + €0.30) for credit cards.",
        "proj_title": ":material/trending_up: Cumulative 12-Month Projection",
        "proj_help": "Dynamically simulates growth over 12 months. Accounts for compounding subscriptions and dropping Airwallex fees once 10k revenue is reached during the year.",
        "proj_sub": "Total Subscriptions",
        "proj_setup": "Total Onboarding",
        "proj_total": "Total (12 Months)",
        "chart_title": ":material/bar_chart: Current Month Cost Breakdown (in EUR)",
        "insights_title": ":material/insights: Analytical Insights",
        "insight_repat": "**Repatriation Trap:** By converting {pct}% back, you pay {fx_cost}€ in {provider} FX fees this month. This reduces savings.",
        "insight_awx": "**Airwallex Bonus:** Because your current volume exceeds €10,000, the €19 Airwallex base fee is automatically waived.",
        "insight_awx_fee": "**Airwallex Fee:** Since current month's revenue is below €10,000, a €19 base fee applies. (This is dynamically updated in the 12-month projection once 10k is reached).",
        "insight_breakeven": "**Setup Boost:** Thanks to high setup fees for new customers, the volume quickly reaches highly profitable zones.",
        "insight_annual": "**Dynamic Annual Leverage:** Accounting for the set monthly growth, the setup protects approx. **€ {annual:,.0f}** from FX erosion over the next 12 months.",
        "flow_title": ":material/account_tree: Target Infrastructure (Data Flow)",
        "scen_sq": "Status Quo (Local Bank)",
        "scen_new": "New Setup ({provider})",
        "cat_base": "1. Base Processing",
        "cat_fx": "2. Stripe FX / Payout Fee",
        "cat_prov": "3. Provider Fixed Cost",
        "cat_repat": "4. Provider FX (Conversion)",
        "rate_base": "Base Fee / Month",
        "rate_transfer": "Local Transfer (US/UK)",
        "rate_fx": "FX Markup (Conversion)",
        
        "vs_title": ":material/balance: Provider Pros & Cons",
        "pro": "Pros",
        "con": "Cons",
        "awx_p1": "Local US/UK transfers are completely free",
        "awx_p2": "Native DATEV integration (German compliance)",
        "awx_p3": "Interest on balances ('Yield') & card cashback",
        "awx_c1": "Monthly fee (€19) if revenue drops below 10k",
        "awx_c2": "Platform can feel complex initially",
        "wise_p1": "Zero monthly fixed costs, very intuitive app",
        "wise_p2": "Industry best Mid-Market exchange rate",
        "wise_p3": "Very fast and easy account setup",
        "wise_c1": "Fees apply for local transfers/payroll (~€0.50)",
        "wise_c2": "DATEV integration requires workarounds",
        "rev_p1": "Great app with strong automation features",
        "rev_p2": "FX allowances included in paid plans (Grow)",
        "rev_c1": "Requires at least €25/month for a sensible plan",
        "rev_c2": "Local USD details sometimes via partner banks"
    }
}

def t(key):
    return T[lang][key]

# --- KONSTANTEN ---
AOV_USD = 1499
AOV_GBP = 999
SETUP_FEE_USD = 2500
SETUP_FEE_GBP = 2500

# --- HEADER ---
st.title(t("title"))
st.markdown(t("subtitle"))

# Info, ob Live Kurse geladen wurden
if rates_are_live:
    st.caption(f"{t('live_rates')} (1 USD = {FX_RATE_USD_EUR:.4f} €, 1 GBP = {FX_RATE_GBP_EUR:.4f} €)")
else:
    st.caption(f"{t('offline_rates')} (1 USD = {FX_RATE_USD_EUR:.4f} €, 1 GBP = {FX_RATE_GBP_EUR:.4f} €)")
    
st.divider()

# --- SIDEBAR: INPUT PARAMETER ---
with st.sidebar:
    st.header(t("sidebar_title"))
    
    st.subheader(t("market_us"))
    us_exist = st.number_input(f"{t('exist_subs')} (US)", min_value=0, value=1, step=1, help=t("help_subs"))
    us_new = st.number_input(f"{t('new_subs')} (US)", min_value=0, value=2, step=1, help=t("help_new_subs"))
    
    st.subheader(t("market_uk"))
    uk_exist = st.number_input(f"{t('exist_subs')} (UK)", min_value=0, value=0, step=1, help=t("help_subs"))
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

# --- BERECHNUNGSLOGIK (AKTUELLER MONAT) ---
# 1. Volumina (Abo-Bestand + Abo-Neu + Setup-Gebühr-Neu) für den ersten Monat
total_us_customers = us_exist + us_new
total_uk_customers = uk_exist + uk_new

vol_usd = (total_us_customers * AOV_USD) + (us_new * SETUP_FEE_USD)
vol_gbp = (total_uk_customers * AOV_GBP) + (uk_new * SETUP_FEE_GBP)
vol_eur_total = (vol_usd * FX_RATE_USD_EUR) + (vol_gbp * FX_RATE_GBP_EUR)

# 2. Unvermeidbare Basis-Gebühren (Aktueller Monat)
transactions_usd = total_us_customers 
transactions_gbp = total_uk_customers
base_fee_usd_processing = (vol_usd * 0.0325) + (transactions_usd * 0.30)
base_fee_gbp_processing = (vol_gbp * 0.025) + (transactions_gbp * 0.30) 
base_fee_eur_total = (base_fee_usd_processing * FX_RATE_USD_EUR) + (base_fee_gbp_processing * FX_RATE_GBP_EUR)

# 3. Status Quo Kosten (Aktueller Monat)
fx_cost_status_quo_eur = (vol_usd * FX_RATE_USD_EUR * 0.02) + (vol_gbp * FX_RATE_GBP_EUR * 0.02)
total_cost_sq_eur = base_fee_eur_total + fx_cost_status_quo_eur

# 4. Neues Setup Stripe Payout Fees (Aktueller Monat)
stripe_payout_cost_usd = (vol_usd * 0.0125) + (payouts_per_month * 1.50) if vol_usd > 0 else 0
stripe_payout_cost_gbp = (vol_gbp * 0.01) + (payouts_per_month * 0.50) if vol_gbp > 0 else 0
stripe_payout_total_eur = (stripe_payout_cost_usd * FX_RATE_USD_EUR) + (stripe_payout_cost_gbp * FX_RATE_GBP_EUR)

# 5. Anbieter-spezifische Fix- & Transaktionskosten (Aktueller Monat)
provider_monthly_fee_eur = 0
provider_transfer_fee_eur = 0
provider_fx_cost_eur = 0

repat_vol_usd = vol_usd * (repatriation_pct / 100)
repat_vol_gbp = vol_gbp * (repatriation_pct / 100)
repat_vol_eur = (repat_vol_usd * FX_RATE_USD_EUR) + (repat_vol_gbp * FX_RATE_GBP_EUR)

if provider == "Airwallex":
    provider_monthly_fee_eur = 19 if vol_eur_total < 10000 else 0
    provider_transfer_fee_eur = 0 
    provider_fx_cost_eur = (repat_vol_usd * FX_RATE_USD_EUR * 0.005) + (repat_vol_gbp * FX_RATE_GBP_EUR * 0.005)
    r_base = f"€ 19 (entfällt, da Umsatz > 10k €)" if vol_eur_total >= 10000 and lang == "DE" else f"€ 19 (waived, revenue > 10k €)" if vol_eur_total >= 10000 else "€ 19"
    r_trans = "€ 0 (Kostenlos)" if lang == "DE" else "€ 0 (Free)"
    r_fx = "~ 0.5 %"

elif provider == "Wise Business":
    provider_monthly_fee_eur = 0 
    provider_transfer_fee_eur = (1 * 0.39 * FX_RATE_USD_EUR) + (1 * 0.35 * FX_RATE_GBP_EUR) 
    provider_fx_cost_eur = (repat_vol_usd * FX_RATE_USD_EUR * 0.0043) + (repat_vol_gbp * FX_RATE_GBP_EUR * 0.0043)
    r_base = "€ 0 (Einmalig 50€ Setup)" if lang == "DE" else "€ 0 (€50 one-time setup)"
    r_trans = "~ 0.35£ / 0.39$ pro ÜW" if lang == "DE" else "~ £0.35 / $0.39 per transfer"
    r_fx = "~ 0.43 %"

elif provider == "Revolut Business":
    provider_monthly_fee_eur = 25 
    provider_transfer_fee_eur = 0 
    fx_subject_to_fee = max(0, repat_vol_eur - 11700)
    provider_fx_cost_eur = fx_subject_to_fee * 0.006
    r_base = "€ 25 (Grow Plan)"
    r_trans = "€ 0 (im Freibetrag)" if lang == "DE" else "€ 0 (in allowance)"
    r_fx = "0 % (bis 10k £, dann 0.6%)" if lang == "DE" else "0 % (up to £10k, then 0.6%)"

total_cost_new_eur = base_fee_eur_total + stripe_payout_total_eur + provider_monthly_fee_eur + provider_transfer_fee_eur + provider_fx_cost_eur

# 6. Ersparnis aktueller Monat berechnen
savings_eur = total_cost_sq_eur - total_cost_new_eur
savings_percent = (savings_eur / vol_eur_total * 100) if vol_eur_total > 0 else 0


# --- DYNAMISCHE 12-MONATS SCHLEIFE FÜR JAHRES-ERSPARNIS ---
# Simuliert exakt Monat für Monat das Wachstum, um Gebühren (wie Airwallex < 10k) präzise abzubilden
annual_savings_dynamic = 0

for m in range(1, 13):
    # Kunden im Monat m
    us_cust_m = us_exist + (m * us_new)
    uk_cust_m = uk_exist + (m * uk_new)
    
    # Volumen im Monat m
    vol_usd_m = (us_cust_m * AOV_USD) + (us_new * SETUP_FEE_USD)
    vol_gbp_m = (uk_cust_m * AOV_GBP) + (uk_new * SETUP_FEE_GBP)
    vol_eur_m = (vol_usd_m * FX_RATE_USD_EUR) + (vol_gbp_m * FX_RATE_GBP_EUR)
    
    # Base Processing Monat m
    base_usd_m = (vol_usd_m * 0.0325) + (us_cust_m * 0.30)
    base_gbp_m = (vol_gbp_m * 0.025) + (uk_cust_m * 0.30) 
    base_eur_m = (base_usd_m * FX_RATE_USD_EUR) + (base_gbp_m * FX_RATE_GBP_EUR)
    
    # Status Quo Monat m
    sq_fx_m = (vol_usd_m * FX_RATE_USD_EUR * 0.02) + (vol_gbp_m * FX_RATE_GBP_EUR * 0.02)
    sq_cost_m = base_eur_m + sq_fx_m
    
    # Stripe Payouts Monat m
    p_usd_m = (vol_usd_m * 0.0125) + (payouts_per_month * 1.50) if vol_usd_m > 0 else 0
    p_gbp_m = (vol_gbp_m * 0.01) + (payouts_per_month * 0.50) if vol_gbp_m > 0 else 0
    payout_eur_m = (p_usd_m * FX_RATE_USD_EUR) + (p_gbp_m * FX_RATE_GBP_EUR)
    
    # Repatriation Monat m
    rep_usd_m = vol_usd_m * (repatriation_pct / 100)
    rep_gbp_m = vol_gbp_m * (repatriation_pct / 100)
    rep_eur_m = (rep_usd_m * FX_RATE_USD_EUR) + (rep_gbp_m * FX_RATE_GBP_EUR)
    
    prov_fee_m = 0
    trans_fee_m = 0
    fx_fee_m = 0
    
    if provider == "Airwallex":
        prov_fee_m = 19 if vol_eur_m < 10000 else 0
        fx_fee_m = (rep_usd_m * FX_RATE_USD_EUR * 0.005) + (rep_gbp_m * FX_RATE_GBP_EUR * 0.005)
    elif provider == "Wise Business":
        trans_fee_m = (1 * 0.39 * FX_RATE_USD_EUR) + (1 * 0.35 * FX_RATE_GBP_EUR) 
        fx_fee_m = (rep_usd_m * FX_RATE_USD_EUR * 0.0043) + (rep_gbp_m * FX_RATE_GBP_EUR * 0.0043)
    elif provider == "Revolut Business":
        prov_fee_m = 25 
        fx_subj = max(0, rep_eur_m - 11700)
        fx_fee_m = fx_subj * 0.006
        
    new_cost_m = base_eur_m + payout_eur_m + prov_fee_m + trans_fee_m + fx_fee_m
    
    # Ersparnis im jeweiligen Monat zur Jahressumme addieren
    annual_savings_dynamic += (sq_cost_m - new_cost_m)

# --- KUMULIERTE 12-MONATS BERECHNUNG (Umsatz) ---
usd_sub_12m = (us_exist * 12 * AOV_USD) + (us_new * 78 * AOV_USD)
usd_setup_12m = us_new * 12 * SETUP_FEE_USD
usd_total_12m = usd_sub_12m + usd_setup_12m

gbp_sub_12m = (uk_exist * 12 * AOV_GBP) + (uk_new * 78 * AOV_GBP)
gbp_setup_12m = uk_new * 12 * SETUP_FEE_GBP
gbp_total_12m = gbp_sub_12m + gbp_setup_12m


# Konditionen anzeigen
st.caption(t("provider_rates"))
r1, r2, r3 = st.columns(3)
r1.info(f"**{t('rate_base')}:**\n\n{r_base}")
r2.info(f"**{t('rate_transfer')}:**\n\n{r_trans}")
r3.info(f"**{t('rate_fx')}:**\n\n{r_fx}")

st.divider()

# --- DASHBOARD KPIs (Aktueller Monat) ---
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
        value=f"€ {annual_savings_dynamic:,.0f}",
        delta="12 Months ROI",
        delta_color="normal" if annual_savings_dynamic > 0 else "inverse"
    )

st.caption(f":material/info: **{t('base_fees')}: € {base_fee_eur_total:,.0f}**. {t('base_fees_help')}")
st.divider()

# --- KUMULIERTE 12-MONATS-AUSWERTUNG ---
st.subheader(t("proj_title"), help=t("proj_help"))

proj_col1, proj_col2 = st.columns(2)

with proj_col1:
    st.markdown(f"**{t('market_us')}**")
    st.write(f"• {t('proj_sub')}: **$ {usd_sub_12m:,.0f}**")
    st.write(f"• {t('proj_setup')}: **$ {usd_setup_12m:,.0f}**")
    st.success(f"**{t('proj_total')}: $ {usd_total_12m:,.0f}**")

with proj_col2:
    st.markdown(f"**{t('market_uk')}**")
    st.write(f"• {t('proj_sub')}: **£ {gbp_sub_12m:,.0f}**")
    st.write(f"• {t('proj_setup')}: **£ {gbp_setup_12m:,.0f}**")
    st.success(f"**{t('proj_total')}: £ {gbp_total_12m:,.0f}**")

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
    
    if provider == "Airwallex":
        if vol_eur_total >= 10000:
            st.success(t("insight_awx"))
        else:
            st.warning(t("insight_awx_fee"))
        
    if repatriation_pct > 0:
        st.warning(t("insight_repat").format(pct=repatriation_pct, fx_cost=f"{provider_fx_cost_eur:,.0f}", provider=provider))
    else:
        st.info(t("insight_breakeven"))
        
    st.success(t("insight_annual").format(annual=annual_savings_dynamic))

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

st.divider()

# --- VOR- UND NACHTEILE VERGLEICH ---
st.subheader(t("vs_title"))

col_awx, col_wise, col_rev = st.columns(3)

with col_awx:
    st.markdown("### :material/business: Airwallex")
    st.success(f"**{t('pro')}:**\n- {t('awx_p1')}\n- {t('awx_p2')}\n- {t('awx_p3')}")
    st.error(f"**{t('con')}:**\n- {t('awx_c1')}\n- {t('awx_c2')}")

with col_wise:
    st.markdown("### :material/account_balance: Wise Business")
    st.success(f"**{t('pro')}:**\n- {t('wise_p1')}\n- {t('wise_p2')}\n- {t('wise_p3')}")
    st.error(f"**{t('con')}:**\n- {t('wise_c1')}\n- {t('wise_c2')}")

with col_rev:
    st.markdown("### :material/credit_card: Revolut Business")
    st.success(f"**{t('pro')}:**\n- {t('rev_p1')}\n- {t('rev_p2')}")
    st.error(f"**{t('con')}:**\n- {t('rev_c1')}\n- {t('rev_c2')}")
