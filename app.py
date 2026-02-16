# ==========================================================
# APP STREAMLIT — EXTRACTION MOYENNE D'ORIENTATION (MO)
# Site: https://bourses.mendob.ci/index.php?adr=consultnotesbepc.inc
# Interface: Thème OR — 100% no-scroll, tout tient en 1 écran
# ==========================================================

import streamlit as st
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from datetime import datetime
import time
import random
import os
import re

# ==========================================================
# CONFIG PAGE
# ==========================================================
st.set_page_config(
    page_title="Extraction MO — Mendob",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==========================================================
# STYLE OR — FULL-SCREEN NO-SCROLL
# ==========================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;800&family=DM+Sans:wght@300;400;500&display=swap');

:root {
    --or1: #FFD700;
    --or2: #FFA500;
    --or3: #B8860B;
    --or4: #8B6914;
    --fond: #0A0800;
    --bord: rgba(255,215,0,0.18);
    --vert: #39FF7A;
    --rouge: #FF4B4B;
}

/* ── RESET TOTAL SCROLL ── */
html, body {
    overflow: hidden !important;
    height: 100vh !important;
    margin: 0 !important;
    padding: 0 !important;
}

.stApp {
    background: radial-gradient(ellipse at 20% 10%, #1a1200 0%, #0a0800 55%, #000 100%);
    height: 100vh !important;
    overflow: hidden !important;
    font-family: 'DM Sans', sans-serif;
    color: #f5e6c0;
}

/* Streamlit wrappers */
.stApp > div,
.stApp > div > div,
.appview-container,
.appview-container > section,
.main,
.main > div {
    height: 100vh !important;
    overflow: hidden !important;
    padding: 0 !important;
}

.block-container {
    padding: 10px 18px 0 18px !important;
    max-width: 100% !important;
    height: 100vh !important;
    overflow: hidden !important;
}

/* Cacher chrome Streamlit */
header, footer, #MainMenu, .stDeployButton,
[data-testid="stToolbar"], [data-testid="stDecoration"] {
    display: none !important;
    visibility: hidden !important;
    height: 0 !important;
}

/* ── TOPBAR ── */
.topbar {
    background: linear-gradient(135deg, #1a1200 0%, #2a1f00 50%, #1a1200 100%);
    border: 1px solid var(--bord);
    border-radius: 10px;
    padding: 8px 18px;
    margin-bottom: 8px;
    position: relative;
    overflow: hidden;
    box-shadow: 0 4px 30px rgba(255,215,0,0.07), inset 0 1px 0 rgba(255,215,0,0.1);
}
.topbar::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--or1), var(--or2), transparent);
}
.topbar-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.topbar-title {
    font-family: 'Playfair Display', serif;
    font-size: 1.3rem;
    font-weight: 800;
    background: linear-gradient(135deg, var(--or1) 0%, var(--or2) 60%, #fff8dc 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0;
    line-height: 1.2;
}
.topbar-sub {
    color: rgba(255,215,0,0.45);
    font-size: 0.7rem;
    letter-spacing: 1.8px;
    text-transform: uppercase;
    margin-top: 2px;
}
.topbar-right {
    text-align: right;
    color: rgba(255,215,0,0.35);
    font-size: 0.68rem;
    letter-spacing: 0.5px;
}
.badge {
    display: inline-block;
    background: linear-gradient(135deg, var(--or3), var(--or4));
    color: var(--or1);
    font-size: 0.62rem;
    font-weight: 500;
    letter-spacing: 1.2px;
    text-transform: uppercase;
    padding: 2px 10px;
    border-radius: 20px;
    border: 1px solid rgba(255,215,0,0.2);
    margin-top: 3px;
}

/* ── BARRE DE CONTROLES ── */
.ctrl-wrap {
    background: linear-gradient(135deg, #130f00, #0d0900);
    border: 1px solid var(--bord);
    border-radius: 10px;
    padding: 6px 14px 2px 14px;
    margin-bottom: 6px;
}
.ctrl-label {
    font-size: 0.62rem;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: rgba(255,215,0,0.5);
    margin-bottom: 2px;
}

/* ── PILLS INFO ── */
.pill-row {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    margin-bottom: 8px;
}
.pill {
    background: rgba(255,215,0,0.04);
    border: 1px solid rgba(255,215,0,0.1);
    border-radius: 6px;
    padding: 3px 10px;
    font-size: 0.65rem;
    color: rgba(255,215,0,0.5);
}
.pill b { color: rgba(255,215,0,0.85); }

/* ── PANELS ── */
.panel-box {
    background: linear-gradient(160deg, #130f00 0%, #0d0900 100%);
    border: 1px solid var(--bord);
    border-radius: 12px;
    padding: 12px 14px;
    height: calc(100vh - 215px);
    overflow: hidden;
    box-shadow: 0 2px 20px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,215,0,0.05);
    display: flex;
    flex-direction: column;
}
.panel-title {
    font-family: 'Playfair Display', serif;
    font-size: 0.82rem;
    color: var(--or1);
    letter-spacing: 1.2px;
    border-bottom: 1px solid rgba(255,215,0,0.1);
    padding-bottom: 6px;
    margin-bottom: 8px;
    text-transform: uppercase;
    flex-shrink: 0;
}

/* ── CONSOLE LOG ── */
.log-console {
    background: #030200;
    border: 1px solid rgba(255,215,0,0.08);
    border-radius: 8px;
    padding: 10px 12px;
    flex: 1;
    overflow-y: auto;
    font-family: 'Courier New', monospace;
    font-size: 0.75rem;
    line-height: 1.65;
    min-height: 0;
}
.log-idle {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
    flex-direction: column;
    text-align: center;
    gap: 8px;
}
.log-idle-icon { font-size: 2rem; }
.log-idle-txt {
    font-family: 'Playfair Display', serif;
    font-size: 0.9rem;
    color: rgba(255,215,0,0.3);
}
.log-idle-sub {
    font-size: 0.65rem;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: rgba(255,215,0,0.18);
}
.log-line { margin: 0; padding: 1px 0; }
.log-ok   { color: var(--vert); }
.log-err  { color: var(--rouge); }
.log-info { color: var(--or1); }
.log-wait { color: rgba(255,215,0,0.42); }

/* ── PROGRESS ── */
.prog-area { flex-shrink: 0; margin-top: 6px; }
.prog-header {
    display: flex;
    justify-content: space-between;
    font-size: 0.65rem;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: rgba(255,215,0,0.4);
    margin-bottom: 4px;
}
.stProgress { margin: 0 !important; }
.stProgress > div > div > div {
    background: linear-gradient(90deg, var(--or3), var(--or1), var(--or2)) !important;
    border-radius: 6px;
    box-shadow: 0 0 10px rgba(255,165,0,0.35);
}
.stProgress > div > div {
    background: rgba(255,215,0,0.07) !important;
    border-radius: 6px;
    height: 8px !important;
}

/* ── KPI CARDS ── */
.kpi-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
    margin-bottom: 8px;
    flex-shrink: 0;
}
.kpi-card {
    background: linear-gradient(160deg, #1f1800 0%, #130f00 100%);
    border: 1px solid rgba(255,215,0,0.12);
    border-radius: 10px;
    padding: 10px 8px;
    text-align: center;
    position: relative;
    overflow: hidden;
}
.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--or2), transparent);
}
.kpi-lbl {
    font-size: 0.58rem;
    font-weight: 500;
    letter-spacing: 1.8px;
    text-transform: uppercase;
    color: rgba(255,215,0,0.45);
    margin-bottom: 4px;
}
.kpi-val {
    font-family: 'Playfair Display', serif;
    font-size: 1.7rem;
    font-weight: 800;
    background: linear-gradient(135deg, var(--or1), var(--or2));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1;
}
.kpi-val-g {
    font-family: 'Playfair Display', serif;
    font-size: 1.7rem;
    font-weight: 800;
    color: var(--vert);
    line-height: 1;
    text-shadow: 0 0 16px rgba(57,255,122,0.28);
}
.kpi-val-r {
    font-family: 'Playfair Display', serif;
    font-size: 1.7rem;
    font-weight: 800;
    color: var(--rouge);
    line-height: 1;
}

/* ── RESULT BOX ── */
.result-box {
    background: linear-gradient(135deg, rgba(57,255,122,0.05), rgba(0,80,30,0.08));
    border: 1px solid rgba(57,255,122,0.2);
    border-radius: 8px;
    padding: 10px 14px;
    flex: 1;
    overflow-y: auto;
    min-height: 0;
}
.result-title {
    font-family: 'Playfair Display', serif;
    font-size: 0.9rem;
    color: var(--vert);
    margin-bottom: 6px;
}
.stat-row {
    font-size: 0.72rem;
    color: rgba(255,215,0,0.65);
    line-height: 1.9;
}
.stat-row b { color: var(--or1); }
.stat-row .g { color: var(--vert); }
.file-tag {
    display: inline-block;
    background: rgba(255,215,0,0.06);
    border: 1px solid rgba(255,215,0,0.15);
    border-radius: 5px;
    padding: 3px 8px;
    font-size: 0.65rem;
    color: rgba(255,215,0,0.55);
    font-family: 'Courier New', monospace;
    margin-top: 6px;
    word-break: break-all;
}
.idle-right {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
    color: rgba(255,215,0,0.15);
    font-size: 0.7rem;
    letter-spacing: 2px;
    text-transform: uppercase;
}

/* ── INPUTS STREAMLIT ── */
.stNumberInput { margin-bottom: 0 !important; }
.stNumberInput input {
    background: #0d0900 !important;
    border: 1px solid rgba(255,215,0,0.2) !important;
    color: var(--or1) !important;
    border-radius: 6px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.85rem !important;
    padding: 5px 10px !important;
}
.stNumberInput input:focus {
    border-color: var(--or1) !important;
    box-shadow: 0 0 0 2px rgba(255,215,0,0.1) !important;
}
.stNumberInput label {
    color: rgba(255,215,0,0.6) !important;
    font-size: 0.65rem !important;
    letter-spacing: 1.5px !important;
    text-transform: uppercase !important;
    font-family: 'DM Sans', sans-serif !important;
}

/* Réduire l'espace Streamlit columns */
[data-testid="stHorizontalBlock"] {
    gap: 8px !important;
    align-items: flex-end !important;
    margin-bottom: 0 !important;
}
[data-testid="column"] { padding: 0 !important; }

/* ── BOUTONS ── */
.stButton { margin: 0 !important; }
.stButton > button {
    background: linear-gradient(135deg, var(--or3) 0%, var(--or2) 50%, var(--or1) 100%) !important;
    color: #0a0800 !important;
    font-family: 'Playfair Display', serif !important;
    font-size: 0.82rem !important;
    font-weight: 800 !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    border: none !important;
    border-radius: 7px !important;
    padding: 8px 14px !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 3px 14px rgba(255,165,0,0.28) !important;
    width: 100% !important;
    height: 38px !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 22px rgba(255,165,0,0.45) !important;
    filter: brightness(1.07) !important;
}
.stButton > button:disabled {
    opacity: 0.3 !important;
    cursor: not-allowed !important;
    transform: none !important;
}

/* Bouton ARRETER (4eme colonne) */
[data-testid="column"]:last-child .stButton > button {
    background: rgba(255,75,75,0.08) !important;
    border: 1px solid rgba(255,75,75,0.32) !important;
    color: var(--rouge) !important;
    box-shadow: none !important;
    font-size: 0.78rem !important;
}
[data-testid="column"]:last-child .stButton > button:hover {
    background: rgba(255,75,75,0.18) !important;
    box-shadow: 0 3px 12px rgba(255,75,75,0.22) !important;
    transform: translateY(-1px) !important;
}

/* ── SCROLLBAR ── */
::-webkit-scrollbar { width: 3px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255,215,0,0.22); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(255,215,0,0.4); }

/* Supprimer marges inutiles */
.stMarkdown { margin: 0 !important; padding: 0 !important; }
div[data-testid="stVerticalBlock"] > div { gap: 0 !important; }
</style>
""", unsafe_allow_html=True)


# ==========================================================
# FONCTIONS D'EXTRACTION (depuis moyenneOr.py — intégrées)
# ==========================================================

def extraire_mo_depuis_page(driver):
    """Extrait la MO via 5 méthodes en cascade. Retourne (float, str) ou (None, None)."""
    try:
        WebDriverWait(driver, 15).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        time.sleep(3)

        page_text   = driver.find_element(By.TAG_NAME, "body").text
        page_source = driver.page_source

        # Méthode 1 — "MO" suivi d'un nombre dans le texte brut
        m1 = re.search(r'MO[\s:=]*(\d{1,2}[.,]\d{2})', page_text, re.IGNORECASE)
        if m1:
            try:
                val = float(m1.group(1).replace(',', '.'))
                if 0 <= val <= 20:
                    return val, f"M1 texte: {m1.group(0)}"
            except ValueError:
                pass

        # Méthode 2 — éléments DOM avec texte "MO" et voisinage
        for elem in driver.find_elements(By.XPATH, "//*[contains(text(),'MO')]"):
            try:
                text = elem.text.strip()
                m2 = re.search(r'MO[:\s]*(\d{1,2}[.,]\d{2})', text, re.IGNORECASE)
                if m2:
                    val = float(m2.group(1).replace(',', '.'))
                    if 0 <= val <= 20:
                        return val, f"M2 DOM: {text[:60]}"
                sibs = (elem.find_elements(By.XPATH, './following-sibling::*') +
                        elem.find_elements(By.XPATH, './preceding-sibling::*'))
                for sib in sibs[:4]:
                    st_ = sib.text.strip()
                    if re.match(r'^\d{1,2}[.,]\d{2}$', st_):
                        val = float(st_.replace(',', '.'))
                        if 0 <= val <= 20:
                            return val, f"M2 sibling: {st_}"
            except Exception:
                continue

        # Méthode 3 — tableau après cellule MGA
        try:
            mga = driver.find_elements(
                By.XPATH, "//td[contains(text(),'MGA')] | //td[contains(text(),'mga')]"
            )
            if mga:
                for cell in mga[0].find_elements(By.XPATH, ".//following::td")[:10]:
                    ct = cell.text.strip()
                    if re.match(r'^\d{1,2}[.,]\d{2}$', ct):
                        val = float(ct.replace(',', '.'))
                        if 0 <= val <= 15:
                            return val, f"M3 tableau: {ct}"
        except Exception:
            pass

        # Méthode 4 — éléments stylés contenant un nombre
        try:
            for elem in driver.find_elements(
                By.CSS_SELECTOR,
                "*[style*='border'], *[style*='background'], *[style*='outline']"
            ):
                text = elem.text.strip()
                if re.match(r'^\d{1,2}[.,]\d{2}$', text):
                    val = float(text.replace(',', '.'))
                    if 0 <= val <= 15:
                        try:
                            ptxt = elem.find_element(By.XPATH, './..').text
                        except Exception:
                            ptxt = ""
                        if 'MGA' not in ptxt.upper():
                            return val, f"M4 style: {text}"
        except Exception:
            pass

        # Méthode 5 — regex dans le HTML source
        for pattern in [
            r'MO[^0-9]{0,5}(\d{1,2}[.,]\d{2})',
            r'style="[^"]*(?:border|background)[^"]*"[^>]*>(\d{1,2}[.,]\d{2})',
        ]:
            for m5 in re.findall(pattern, page_source, re.IGNORECASE):
                try:
                    val = float(m5.replace(',', '.'))
                    if 0 <= val <= 15:
                        return val, f"M5 HTML: {m5}"
                except ValueError:
                    continue

        return None, None
    except Exception:
        return None, None


def construire_chrome_options():
    """Options Chrome headless optimisées."""
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option("useAutomationExtension", False)
    opts.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    opts.add_argument("--window-size=1366,768")
    return opts


# ==========================================================
# SESSION STATE
# ==========================================================
for _k, _v in {
    "running": False, "logs": [], "results": [],
    "total_ok": 0, "total_fail": 0, "total_introuvable": 0,
    "total_traite": 0, "total_a_traiter": 0, "termine": False,
}.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v


# ==========================================================
# TOPBAR (compacte)
# ==========================================================
st.markdown("""
<div class="topbar">
  <div class="topbar-row">
    <div>
      <p class="topbar-title">🏆 Extraction MO &mdash; Mendob</p>
      <p class="topbar-sub">Moyenne d'orientation &bull; BEPC &bull; Côte d'Ivoire</p>
      <span class="badge">⚡ Zone violette &bull; Anti-MGA</span>
    </div>
    <div class="topbar-right">
      bourses.mendob.ci<br>
      <span style="font-size:0.6rem;letter-spacing:0.8px;">consultnotesbepc.inc</span>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ==========================================================
# CHARGEMENT FICHIER
# ==========================================================
FILE_PATH = "newachercher.xlsx"

if not os.path.exists(FILE_PATH):
    st.markdown("""
    <div style="background:rgba(255,75,75,0.07);border:1px solid rgba(255,75,75,0.28);
                border-radius:10px;padding:14px;text-align:center;margin-top:8px;">
      <p style="color:#FF6B6B;font-family:'Playfair Display',serif;font-size:0.95rem;margin:0;">
        ⚠️ Fichier <code>newachercher.xlsx</code> introuvable
      </p>
      <p style="color:rgba(255,215,0,0.45);font-size:0.75rem;margin-top:5px;">
        Placez le fichier dans le même dossier que app.py
      </p>
    </div>""", unsafe_allow_html=True)
    st.stop()

try:
    df_data = pd.read_excel(FILE_PATH)
except Exception as e:
    st.error(f"Impossible de lire newachercher.xlsx : {e}")
    st.stop()

if "MATRICULE" not in df_data.columns:
    st.error("Colonne 'MATRICULE' absente du fichier Excel.")
    st.stop()

total_lignes = len(df_data)

# ==========================================================
# BARRE DE CONTROLES (compacte)
# ==========================================================
st.markdown(
    '<div class="ctrl-wrap"><p class="ctrl-label">⚙️ Paramètres d\'extraction</p></div>',
    unsafe_allow_html=True
)

col_s, col_e, col_btn, col_stop = st.columns([1, 1, 2.5, 1])

with col_s:
    start_idx = st.number_input(
        "Départ", min_value=1, max_value=total_lignes, value=1, step=1
    )
with col_e:
    end_idx = st.number_input(
        "Fin", min_value=start_idx, max_value=total_lignes, value=total_lignes, step=1
    )
with col_btn:
    lancer = st.button(
        "🚀 LANCER L'EXTRACTION",
        use_container_width=True,
        disabled=st.session_state.running
    )
with col_stop:
    arreter = st.button(
        "⏹ ARRÊTER",
        use_container_width=True,
        disabled=not st.session_state.running
    )

# Pills d'info
nb_a_traiter = end_idx - start_idx + 1
st.markdown(f"""
<div class="pill-row">
  <div class="pill">📂 <b>{total_lignes}</b> matricules</div>
  <div class="pill">🎯 <b>{nb_a_traiter}</b> sélectionnés</div>
  <div class="pill">🌐 bourses.mendob.ci</div>
</div>
""", unsafe_allow_html=True)

# ==========================================================
# GESTION BOUTONS
# ==========================================================
if lancer and not st.session_state.running:
    st.session_state.update({
        "running": True, "termine": False, "logs": [], "results": [],
        "total_ok": 0, "total_fail": 0, "total_introuvable": 0,
        "total_traite": 0, "total_a_traiter": nb_a_traiter,
    })

if arreter and st.session_state.running:
    st.session_state.running = False

# ==========================================================
# DASHBOARD — 2 COLONNES HAUTEUR FIXE
# ==========================================================
left_col, right_col = st.columns([3, 2])

with left_col:
    st.markdown('<div class="panel-box">', unsafe_allow_html=True)
    st.markdown('<p class="panel-title">📜 Journal d\'exécution</p>', unsafe_allow_html=True)
    log_placeholder = st.empty()
    prog_label_ph   = st.empty()
    progress_ph     = st.empty()
    st.markdown('</div>', unsafe_allow_html=True)

with right_col:
    st.markdown('<div class="panel-box">', unsafe_allow_html=True)
    st.markdown('<p class="panel-title">📊 Monitoring</p>', unsafe_allow_html=True)
    kpi_placeholder    = st.empty()
    result_placeholder = st.empty()
    st.markdown('</div>', unsafe_allow_html=True)


# ==========================================================
# HELPERS D'AFFICHAGE
# ==========================================================
def render_logs(logs):
    lines = ""
    for e in logs[-80:]:
        txt = (e.get("text", "")
               .replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))
        lines += f'<p class="log-line {e.get("cls","log-info")}">› {txt}</p>\n'
    log_placeholder.markdown(
        f'<div class="log-console">{lines}</div>',
        unsafe_allow_html=True
    )


def render_kpis(traite, total, ok, fail, introuvable):
    pct = int(traite / total * 100) if total > 0 else 0
    kpi_placeholder.markdown(f"""
    <div class="kpi-grid">
      <div class="kpi-card">
        <div class="kpi-lbl">Traités</div>
        <div class="kpi-val">{traite}</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-lbl">MO trouvées</div>
        <div class="kpi-val-g">{ok}</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-lbl">Non détectées</div>
        <div class="kpi-val-r">{fail}</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-lbl">Introuvables</div>
        <div class="kpi-val">{introuvable}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)
    prog_label_ph.markdown(f"""
    <div class="prog-area">
      <div class="prog-header"><span>Progression</span><span>{pct}%</span></div>
    </div>""", unsafe_allow_html=True)
    progress_ph.progress(traite / total if total > 0 else 0)


def render_result_final(results):
    """Résumé final dans le panneau droit, à la place des KPIs."""
    df_r  = pd.DataFrame(results)
    n_ok  = (df_r["Statut"] == "MO_EXTRAITE").sum()
    n_tot = len(df_r)
    moys  = df_r["MO"].dropna()
    avg   = f"{moys.mean():.2f}" if len(moys) > 0 else "—"
    mn    = f"{moys.min():.2f}"  if len(moys) > 0 else "—"
    mx    = f"{moys.max():.2f}"  if len(moys) > 0 else "—"
    ts    = datetime.now().strftime("%Y%m%d_%H%M%S")
    fic   = f"resultats_MO_{ts}.csv"
    df_r.to_csv(fic, index=False, encoding="utf-8")
    result_placeholder.markdown(f"""
    <div class="result-box">
      <p class="result-title">✅ Extraction terminée</p>
      <div class="stat-row">
        📊 Total traités  : <b>{n_tot}</b><br>
        ✅ MO extraites   : <b class="g">{n_ok}</b><br>
        📈 Moyenne MO     : <b>{avg}</b><br>
        ↕ Min / Max       : <b>{mn}</b> / <b>{mx}</b>
      </div>
      <div class="file-tag">💾 {fic}</div>
    </div>
    """, unsafe_allow_html=True)


def log(text, cls="log-info"):
    ts = datetime.now().strftime("%H:%M:%S")
    st.session_state.logs.append({"text": f"[{ts}] {text}", "cls": cls})


# ==========================================================
# ETAT INITIAL
# ==========================================================
if not st.session_state.running and not st.session_state.termine:
    log_placeholder.markdown("""
    <div class="log-console">
      <div class="log-idle">
        <div class="log-idle-icon">🏆</div>
        <p class="log-idle-txt">Prêt à extraire</p>
        <p class="log-idle-sub">Configurez et lancez l'extraction</p>
      </div>
    </div>""", unsafe_allow_html=True)

    kpi_placeholder.markdown("""
    <div class="kpi-grid">
      <div class="kpi-card"><div class="kpi-lbl">Traités</div><div class="kpi-val">—</div></div>
      <div class="kpi-card"><div class="kpi-lbl">MO trouvées</div><div class="kpi-val">—</div></div>
      <div class="kpi-card"><div class="kpi-lbl">Non détectées</div><div class="kpi-val">—</div></div>
      <div class="kpi-card"><div class="kpi-lbl">Introuvables</div><div class="kpi-val">—</div></div>
    </div>""", unsafe_allow_html=True)

    prog_label_ph.markdown("""
    <div class="prog-area">
      <div class="prog-header"><span>Progression</span><span>0%</span></div>
    </div>""", unsafe_allow_html=True)
    progress_ph.progress(0)

    result_placeholder.markdown(
        '<div class="idle-right">En attente</div>',
        unsafe_allow_html=True
    )

# ==========================================================
# BOUCLE D'EXTRACTION
# ==========================================================
if st.session_state.running:

    matricules = df_data.iloc[start_idx - 1: end_idx]["MATRICULE"].astype(str).tolist()
    a_traiter  = len(matricules)

    log("Initialisation Chrome...", "log-wait")
    render_logs(st.session_state.logs)
    render_kpis(0, a_traiter, 0, 0, 0)

    driver = None
    try:
        driver = webdriver.Chrome(options=construire_chrome_options())
        driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )
        driver.set_window_size(1366, 768)
        log("Chrome démarré ✓", "log-ok")

        base_url = "https://bourses.mendob.ci/index.php?adr=consultnotesbepc.inc"

        for i, matricule in enumerate(matricules):

            if not st.session_state.running:
                log("⏹ Arrêt demandé", "log-err")
                break

            pos = i + 1

            # Pauses adaptatives anti-ban
            if pos > 1 and pos % 100 == 0:
                pause = random.randint(45, 90)
                log(f"Pause longue {pause}s...", "log-wait")
                render_logs(st.session_state.logs)
                time.sleep(pause)
            elif pos > 1 and pos % 25 == 0:
                pause = random.randint(15, 30)
                log(f"Pause {pause}s...", "log-wait")
                render_logs(st.session_state.logs)
                time.sleep(pause)

            log(f"[{pos}/{a_traiter}] Matricule: {matricule}", "log-info")

            try:
                driver.get(base_url)
                WebDriverWait(driver, 20).until(
                    lambda d: d.execute_script("return document.readyState") == "complete"
                )
                time.sleep(random.uniform(3, 6))

                # Trouver le champ de saisie
                champ = None
                for sel in [
                    "input[name='matricule']",
                    "input[placeholder*='matricule' i]",
                    "input[type='text']", "input[type='number']",
                    "#matricule", ".form-control", "input"
                ]:
                    try:
                        c = WebDriverWait(driver, 8).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, sel))
                        )
                        if c.is_displayed() and c.is_enabled():
                            champ = c
                            break
                    except Exception:
                        continue

                if champ is None:
                    log(f"  ✗ Champ introuvable", "log-err")
                    st.session_state.results.append({
                        "Matricule": matricule, "MO": None,
                        "Statut": "ERREUR_TECHNIQUE",
                        "Détails": "Champ matricule introuvable",
                        "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    })
                    st.session_state.total_fail += 1
                    st.session_state.total_traite += 1
                    render_logs(st.session_state.logs)
                    render_kpis(
                        st.session_state.total_traite, a_traiter,
                        st.session_state.total_ok, st.session_state.total_fail,
                        st.session_state.total_introuvable
                    )
                    continue

                # Saisie progressive (imitation humaine)
                champ.clear()
                time.sleep(0.4)
                for char in str(matricule):
                    champ.send_keys(char)
                    time.sleep(random.uniform(0.08, 0.22))

                # Soumission
                try:
                    btn = driver.find_element(
                        By.CSS_SELECTOR,
                        "button[type='submit'], input[type='submit'], .btn, button"
                    )
                    driver.execute_script("arguments[0].click();", btn)
                except Exception:
                    champ.send_keys(Keys.RETURN)

                time.sleep(random.uniform(8, 15))

                # Vérification résultat
                page_text = driver.find_element(By.TAG_NAME, "body").text.lower()
                mots_err  = [
                    "matricule non reconnu", "introuvable",
                    "non trouvé", "not found", "aucun résultat", "erreur"
                ]

                if any(m in page_text for m in mots_err):
                    log(f"  ✗ Matricule inconnu", "log-err")
                    st.session_state.results.append({
                        "Matricule": matricule, "MO": None,
                        "Statut": "MATRICULE_INTROUVABLE",
                        "Détails": "Absent de la base Mendob",
                        "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    })
                    st.session_state.total_introuvable += 1
                else:
                    log(f"  🔍 Extraction MO...", "log-wait")
                    mo_val, mo_src = extraire_mo_depuis_page(driver)

                    if mo_val is not None:
                        log(f"  ✅ MO = {mo_val:.2f}", "log-ok")
                        st.session_state.results.append({
                            "Matricule": matricule, "MO": mo_val,
                            "Statut": "MO_EXTRAITE",
                            "Détails": (mo_src or "")[:100],
                            "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        })
                        st.session_state.total_ok += 1
                    else:
                        log(f"  ⚠ MO non détectée", "log-err")
                        dbg = f"debug_MO_{matricule}_{pos}.html"
                        try:
                            with open(dbg, "w", encoding="utf-8") as f:
                                f.write(driver.page_source)
                        except Exception:
                            pass
                        st.session_state.results.append({
                            "Matricule": matricule, "MO": None,
                            "Statut": "MO_NON_DETECTEE",
                            "Détails": f"Debug: {dbg}",
                            "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        })
                        st.session_state.total_fail += 1

                st.session_state.total_traite += 1

                # Checkpoint tous les 50
                if pos % 50 == 0 and st.session_state.results:
                    cp = f"checkpoint_MO_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                    pd.DataFrame(st.session_state.results).to_csv(
                        cp, index=False, encoding="utf-8"
                    )
                    log(f"  💾 Checkpoint: {cp}", "log-ok")

                render_logs(st.session_state.logs)
                render_kpis(
                    st.session_state.total_traite, a_traiter,
                    st.session_state.total_ok, st.session_state.total_fail,
                    st.session_state.total_introuvable
                )

                time.sleep(random.uniform(4, 10))
                driver.delete_all_cookies()

            except Exception as ex:
                log(f"  ✗ Exception: {str(ex)[:70]}", "log-err")
                st.session_state.results.append({
                    "Matricule": matricule, "MO": None,
                    "Statut": "ERREUR_TECHNIQUE",
                    "Détails": str(ex)[:100],
                    "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                })
                st.session_state.total_fail += 1
                st.session_state.total_traite += 1
                render_logs(st.session_state.logs)
                render_kpis(
                    st.session_state.total_traite, a_traiter,
                    st.session_state.total_ok, st.session_state.total_fail,
                    st.session_state.total_introuvable
                )
                time.sleep(5)

    except Exception as ex:
        log(f"Erreur fatale: {ex}", "log-err")
        if st.session_state.results:
            urg = f"urgence_MO_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            pd.DataFrame(st.session_state.results).to_csv(urg, index=False, encoding="utf-8")
            log(f"🆘 Urgence sauvé: {urg}", "log-ok")

    finally:
        if driver:
            try:
                driver.quit()
                log("Navigateur fermé.", "log-wait")
            except Exception:
                pass
        st.session_state.running = False
        st.session_state.termine = True
        render_logs(st.session_state.logs)
        render_kpis(
            st.session_state.total_traite,
            st.session_state.total_a_traiter or 1,
            st.session_state.total_ok,
            st.session_state.total_fail,
            st.session_state.total_introuvable,
        )
        if st.session_state.results:
            render_result_final(st.session_state.results)

# ==========================================================
# ETAT TERMINE (rechargement après fin)
# ==========================================================
if st.session_state.termine and st.session_state.results and not st.session_state.running:
    render_logs(st.session_state.logs)
    render_kpis(
        st.session_state.total_traite,
        st.session_state.total_a_traiter or 1,
        st.session_state.total_ok,
        st.session_state.total_fail,
        st.session_state.total_introuvable,
    )
    render_result_final(st.session_state.results)