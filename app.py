# ==========================================================
# APP STREAMLIT — EXTRACTION MOYENNE D'ORIENTATION (MO)
# Site: https://bourses.mendob.ci/index.php?adr=consultnotesbepc.inc
# Interface: Thème OR — Capture 2/3 | Monitoring 1/3
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
import base64

# ==========================================================
# CONFIG PAGE
# ==========================================================
st.set_page_config(
    page_title="MO",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==========================================================
# STYLE OR
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
    --violet: #BF5FFF;
}

html, body { margin: 0 !important; padding: 0 !important; }

.stApp {
    background: radial-gradient(ellipse at 20% 10%, #1a1200 0%, #0a0800 55%, #000 100%);
    font-family: 'DM Sans', sans-serif;
    color: #f5e6c0;
}

.block-container {
    padding: 6px 12px !important;
    max-width: 100% !important;
}

header, footer, #MainMenu, .stDeployButton,
[data-testid="stToolbar"], [data-testid="stDecoration"] {
    display: none !important;
    visibility: hidden !important;
    height: 0 !important;
}

/* Suppression topbar — plus de grande bannière */
.topbar { display: none !important; }

/* CTRL */
.ctrl-wrap {
    background: linear-gradient(135deg, #130f00, #0d0900);
    border: 1px solid var(--bord);
    border-radius: 10px; padding: 6px 14px 2px 14px; margin-bottom: 6px;
}
.ctrl-label {
    font-size: 0.62rem; letter-spacing: 2px; text-transform: uppercase;
    color: rgba(255,215,0,0.5); margin-bottom: 2px;
}

/* PILLS */
.pill-row { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 8px; }
.pill {
    background: rgba(255,215,0,0.04); border: 1px solid rgba(255,215,0,0.1);
    border-radius: 6px; padding: 3px 10px; font-size: 0.65rem;
    color: rgba(255,215,0,0.5);
}
.pill b { color: rgba(255,215,0,0.85); }

/* PANELS */
.panel-box {
    background: linear-gradient(160deg, #130f00 0%, #0d0900 100%);
    border: 1px solid var(--bord);
    border-radius: 12px; padding: 12px 14px;
    box-shadow: 0 2px 20px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,215,0,0.05);
}
.panel-title {
    font-family: 'Playfair Display', serif; font-size: 0.82rem;
    color: var(--or1); letter-spacing: 1.2px;
    border-bottom: 1px solid rgba(255,215,0,0.1);
    padding-bottom: 6px; margin-bottom: 10px; text-transform: uppercase;
}

/* CAPTURE SCREENSHOT */
.capture-idle {
    display: flex; align-items: center; justify-content: center;
    flex-direction: column; gap: 10px;
    background: #030200; border: 1px dashed rgba(255,215,0,0.1);
    border-radius: 8px; height: 75vh;
}
.capture-wrap {
    border: 1px solid rgba(255,215,0,0.15);
    border-radius: 8px; overflow: hidden; background: #000;
}
.capture-wrap img {
    width: 100% !important;
    height: 74vh !important;
    object-fit: contain !important;
    object-position: top !important;
    display: block;
}
.capture-idle-icon { font-size: 3rem; opacity: 0.4; }
.capture-idle-txt {
    font-family: 'Playfair Display', serif; font-size: 1rem;
    color: rgba(255,215,0,0.2);
}
.capture-idle-sub {
    font-size: 0.65rem; letter-spacing: 2px; text-transform: uppercase;
    color: white;
}
.capture-wrap {
    border: 1px solid rgba(255,215,0,0.15);
    border-radius: 8px; overflow: hidden; background: #000;
}
.capture-wrap img {
    width: 100% !important;
    height: calc(100vh - 165px) !important;
    object-fit: contain !important;
    display: block;
}
.capture-header {
    display: flex; align-items: center; justify-content: space-between;
    padding: 5px 10px;
    background: rgba(255,215,0,0.04);
    border-bottom: 1px solid rgba(255,215,0,0.08);
}
.capture-url {
    font-family: 'Courier New', monospace; font-size: 0.62rem;
    color: rgba(255,215,0,0.3);
}
.capture-status {
    font-size: 0.58rem; letter-spacing: 1.5px; text-transform: uppercase;
    color: rgba(57,255,122,0.6); flex-shrink: 0; margin-left: 8px;
}

/* PROGRESS */
.prog-area { margin-top: 8px; }
.prog-header {
    display: flex; justify-content: space-between;
    font-size: 0.65rem; letter-spacing: 1.5px;
    text-transform: uppercase; color: rgba(255,215,0,0.4); margin-bottom: 4px;
}
.stProgress { margin: 0 !important; }
.stProgress > div > div > div {
    background: linear-gradient(90deg, var(--or3), var(--or1), var(--or2)) !important;
    border-radius: 6px; box-shadow: 0 0 10px rgba(255,165,0,0.35);
}
.stProgress > div > div {
    background: rgba(255,215,0,0.07) !important;
    border-radius: 6px; height: 8px !important;
}

/* KPI CARDS */
.kpi-grid {
    display: grid; grid-template-columns: 1fr 1fr;
    gap: 8px; margin-bottom: 10px;
}
.kpi-card {
    background: linear-gradient(160deg, #1f1800 0%, #130f00 100%);
    border: 1px solid rgba(255,215,0,0.12);
    border-radius: 10px; padding: 10px 8px;
    text-align: center; position: relative; overflow: hidden;
}
.kpi-card::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, var(--or2), transparent);
}
.kpi-lbl {
    font-size: 0.58rem; font-weight: 500; letter-spacing: 1.8px;
    text-transform: uppercase; color: rgba(255,215,0,0.45); margin-bottom: 4px;
}
.kpi-val {
    font-family: 'Playfair Display', serif; font-size: 1.7rem; font-weight: 800;
    background: linear-gradient(135deg, var(--or1), var(--or2));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text; line-height: 1;
}
.kpi-val-g {
    font-family: 'Playfair Display', serif; font-size: 1.7rem; font-weight: 800;
    color: var(--vert); line-height: 1; text-shadow: 0 0 16px rgba(57,255,122,0.28);
}
.kpi-val-r {
    font-family: 'Playfair Display', serif; font-size: 1.7rem; font-weight: 800;
    color: var(--rouge); line-height: 1;
}

/* MO LIVE — ZONE VIOLETTE */
.mo-live-box {
    background: linear-gradient(135deg, rgba(191,95,255,0.1), rgba(80,0,120,0.15));
    border: 2px solid rgba(191,95,255,0.5);
    border-radius: 12px; padding: 14px 16px;
    margin-bottom: 10px; text-align: center;
    box-shadow: 0 0 20px rgba(191,95,255,0.12);
}
.mo-live-label {
    font-size: 0.62rem; letter-spacing: 2.5px; text-transform: uppercase;
    color: white; margin-bottom: 6px;
}
.mo-live-val {
    font-family: 'Playfair Display', serif; font-size: 3rem; font-weight: 800;
    color: white; text-shadow: 0 0 24px rgba(191,95,255,0.5); line-height: 1;
}
.mo-live-mat {
    font-size: 0.68rem; color: white;
    font-family: 'Courier New', monospace; margin-top: 5px;
}
.mo-live-src {
    font-size: 0.58rem; color: white;
    font-family: 'Courier New', monospace; margin-top: 2px;
}
.mo-none-box {
    background: rgba(255,75,75,0.05);
    border: 1px solid rgba(255,75,75,0.2);
    border-radius: 10px; padding: 10px; text-align: center; margin-bottom: 10px;
}
.mo-none-label {
    font-size: 0.62rem; letter-spacing: 2px; text-transform: uppercase;
    color: white; margin-bottom: 3px;
}
.mo-none-mat {
    font-family: 'Courier New', monospace; font-size: 0.7rem;
    color: white;
}

/* PAUSE */
.pause-box {
    background: rgba(255,165,0,0.06); border: 1px solid rgba(255,165,0,0.25);
    border-radius: 10px; padding: 10px 14px; margin-bottom: 10px; text-align: center;
}
.pause-label {
    font-size: 0.62rem; letter-spacing: 2px; text-transform: uppercase;
    color: var(--or2); margin-bottom: 4px;
}
.pause-timer {
    font-family: 'Playfair Display', serif; font-size: 2rem;
    color: var(--or1); font-weight: 800;
}

/* RESULT */
.result-box {
    background: linear-gradient(135deg, rgba(57,255,122,0.05), rgba(0,80,30,0.08));
    border: 1px solid rgba(57,255,122,0.2);
    border-radius: 8px; padding: 12px 14px; margin-top: 8px;
}
.result-title {
    font-family: 'Playfair Display', serif; font-size: 0.9rem;
    color: var(--vert); margin-bottom: 6px;
}
.stat-row { font-size: 0.72rem; color: rgba(255,215,0,0.65); line-height: 2; }
.stat-row b { color: var(--or1); }
.stat-row .g { color: var(--vert); }
.file-tag {
    display: inline-block; background: rgba(255,215,0,0.06);
    border: 1px solid rgba(255,215,0,0.15); border-radius: 5px;
    padding: 3px 8px; font-size: 0.65rem; color: rgba(255,215,0,0.55);
    font-family: 'Courier New', monospace; margin-top: 6px; word-break: break-all;
}

/* STEP */
.step-box {
    background: rgba(255,215,0,0.03); border: 1px solid rgba(255,215,0,0.08);
    border-radius: 8px; padding: 8px 12px; margin-top: 8px;
    font-family: 'Courier New', monospace; font-size: 0.68rem;
    color: rgba(255,215,0,0.45); min-height: 32px;
}
.step-pos { color: rgba(255,215,0,0.3); margin-right: 6px; }
.step-mat { color: var(--or1); }

/* INPUTS */
.stNumberInput input {
    background: #0d0900 !important;
    border: 1px solid rgba(255,215,0,0.2) !important;
    color: var(--or1) !important; border-radius: 6px !important;
    font-size: 0.85rem !important; padding: 5px 10px !important;
}
.stNumberInput label {
    color: rgba(255,215,0,0.6) !important; font-size: 0.65rem !important;
    letter-spacing: 1.5px !important; text-transform: uppercase !important;
}

/* LIGNE CONTROLES — tout aligné en bas sur une seule ligne */
[data-testid="stHorizontalBlock"] {
    gap: 8px !important;
    align-items: flex-end !important;
    flex-wrap: nowrap !important;
}
[data-testid="column"] { padding: 0 !important; min-width: 0 !important; }

/* Bouton aligné avec les inputs */
.stButton { margin: 0 !important; }
.stButton > button {
    background: linear-gradient(135deg, var(--or3) 0%, var(--or2) 50%, var(--or1) 100%) !important;
    color: #0a0800 !important; font-family: 'Playfair Display', serif !important;
    font-size: 0.78rem !important; font-weight: 800 !important;
    letter-spacing: 1.5px !important; text-transform: uppercase !important;
    border: none !important; border-radius: 7px !important;
    padding: 0 10px !important; width: 100% !important; height: 38px !important;
    box-shadow: 0 3px 14px rgba(255,165,0,0.28) !important;
    margin-bottom: 1px !important;
}
.stButton > button:disabled { opacity: 0.3 !important; cursor: not-allowed !important; }

[data-testid="stHorizontalBlock"] > div:last-child .stButton {
    margin-top: 55px !important;
}



.stMarkdown { margin: 0 !important; padding: 0 !important; }
div[data-testid="stVerticalBlock"] > div { gap: 4px !important; }

::-webkit-scrollbar { width: 3px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255,215,0,0.22); border-radius: 3px; }

/* Monitoring sticky en haut à droite */
[data-testid="stHorizontalBlock"] > div:last-child {
    align-self: flex-start !important;
    position: sticky !important;
    top: 0 !important;
}
[data-testid="stHorizontalBlock"] > div:last-child {
    align-self: flex-start !important;
}

</style>
""", unsafe_allow_html=True)


# ==========================================================
# SESSION STATE
# ==========================================================
for _k, _v in {
    "running": False, "results": [],
    "total_ok": 0, "total_fail": 0, "total_introuvable": 0,
    "total_traite": 0, "total_a_traiter": 0,
    "termine": False, "stop_flag": False,
    "mo_courante": None, "mo_courante_mat": "", "mo_courante_src": "",
    "screenshot_b64": None,
}.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v


# ==========================================================
# EXTRACTION MO — CIBLAGE DIRECT : tbody[2] > tr[5] > td[12]
# ==========================================================

def extraire_moyenne_orientation_mendob(driver):
    """
    Extrait la MO : 12ème <td> du 5ème <tr> du 2ème <tbody>.
    La colonne MO est indiquée par le label 'MO' en tr[4]/td[11],
    et la valeur se trouve en tr[5]/td[12].
    Retourne (float, str) ou (None, None).
    """
    try:
        WebDriverWait(driver, 15).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        time.sleep(3)

        elem = driver.find_element(By.XPATH, "(//tbody)[2]/tr[5]/td[12]")
        txt = elem.text.strip()
        m = re.search(r'(\d{1,2}[.,]\d{2})', txt)
        if m:
            val = float(m.group(1).replace(',', '.'))
            if 0 < val <= 20:
                return val, f"tbody[2]>tr[5]>td[12] = {txt}"

        return None, None

    except Exception as e:
        return None, str(e)


def construire_chrome_options():
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
    opts.add_argument("--window-size=1440,1080")
    return opts


def prendre_screenshot(driver, scroll_bottom=False):
    try:
        if scroll_bottom:
            # Défile vers le bas pour voir la zone MO (bas-droite)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(0.5)
        return base64.b64encode(driver.get_screenshot_as_png()).decode("utf-8")
    except Exception:
        return None


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
    df_data = pd.read_excel(FILE_PATH, sheet_name="CAS_GSFA")
except Exception:
    try:
        df_data = pd.read_excel(FILE_PATH)
    except Exception as e2:
        st.error(f"Impossible de lire newachercher.xlsx : {e2}")
        st.stop()

if "MATRICULE" not in df_data.columns:
    st.error("Colonne 'MATRICULE' absente du fichier Excel.")
    st.stop()

total_lignes = len(df_data)

# ==========================================================
# BARRE DE CONTROLES COMPACTE — tout sur UNE ligne
# ==========================================================
st.markdown(
    '<p style="font-size:0.58rem;letter-spacing:1.8px;text-transform:uppercase;'
    'color:white;margin:0 0 3px 2px;">⚙️</p>',
    unsafe_allow_html=True
)

col_s, col_e, col_p, col_btn, col_stop = st.columns([1, 1, 1.2, 2.7, 0.9])
with col_s:
    start_idx = st.number_input("Début", 1, total_lignes, 1)
with col_e:
    end_idx = st.number_input("Fin", start_idx, total_lignes, start_idx + 4)
with col_p:
    pause_manuelle = st.number_input(
        "Pause/élève (s)", min_value=0, max_value=120, value=0, step=5,
        help="0 = pauses auto aléatoires | >0 = pause fixe entre chaque élève"
    )
with col_btn:
    lancer = st.button(
        "COMMENCER L'EXTRACTION DES MOYENNES D'ORIENTATION",
        use_container_width=True,
        disabled=st.session_state.running
    )
with col_stop:
    #st.markdown('<div class="btn-stop">', unsafe_allow_html=True)
    arreter = st.button(
        "⏹ ARRÊTER",
        use_container_width=True,
        disabled=not st.session_state.running
    )

nb_a_traiter = end_idx - start_idx + 1
st.markdown(f"""
<div class="pill-row">
  <div class="pill">📂 <b>{total_lignes}</b> matricules total</div>
  <div class="pill">🎯 <b>{nb_a_traiter}</b> sélectionnés</div>
  <div class="pill">⏱ Pause: <b>{"auto" if pause_manuelle == 0 else f"{pause_manuelle}s"}</b></div>
  <div class="pill">🌐 edgeworth.Group</div>
</div>
""", unsafe_allow_html=True)

# ==========================================================
# GESTION BOUTONS
# ==========================================================
if lancer and not st.session_state.running:
    st.session_state.update({
        "running": True, "termine": False, "results": [],
        "total_ok": 0, "total_fail": 0, "total_introuvable": 0,
        "total_traite": 0, "total_a_traiter": nb_a_traiter,
        "mo_courante": None, "mo_courante_mat": "",
        "mo_courante_src": "", "screenshot_b64": None,
        "stop_flag": False,
    })
    st.rerun()

if arreter and st.session_state.running:
    st.session_state.stop_flag = True
    st.session_state.running   = False


# ==========================================================
# DASHBOARD — 2/3 CAPTURE | 1/3 MONITORING
# ==========================================================
left_col, right_col = st.columns([3, 1])

with left_col:
    st.markdown('<div class="panel-box">', unsafe_allow_html=True)
    st.markdown('<p class="panel-title">🌐 navigateur</p>', unsafe_allow_html=True)
    capture_ph    = st.empty()
    prog_label_ph = st.empty()
    progress_ph   = st.empty()
    step_ph       = st.empty()
    st.markdown('</div>', unsafe_allow_html=True)

with right_col:
    st.markdown('<div class="panel-box">', unsafe_allow_html=True)
    st.markdown('<p class="panel-title">📊 statistique</p>', unsafe_allow_html=True)
    mo_live_ph = st.empty()
    pause_ph   = st.empty()
    kpi_ph     = st.empty()
    result_ph  = st.empty()
    st.markdown('</div>', unsafe_allow_html=True)


# ==========================================================
# HELPERS AFFICHAGE
# ==========================================================
def render_capture(b64, status="LIVE"):
    if b64:
        capture_ph.markdown(f"""
        <div class="capture-wrap">
          <div class="capture-header">
            <span class="capture-status">● {status}</span>
          </div>
          <img src="data:image/png;base64,{b64}" style="width:100%;display:block;" />
        </div>
        """, unsafe_allow_html=True)
    else:
        capture_ph.markdown("""
        <div class="capture-idle">
          <div class="capture-idle-icon">🖥️</div>
          <p class="capture-idle-txt"></p>
          <p class="capture-idle-sub">Le navigateur apparaîtra ici</p>
        </div>
        """, unsafe_allow_html=True)


def render_progress(traite, total):
    pct = int(traite / total * 100) if total > 0 else 0
    prog_label_ph.markdown(f"""
    <div class="prog-area">
      <div class="prog-header">
        <span>Progression</span><span>{traite}/{total} — {pct}%</span>
      </div>
    </div>""", unsafe_allow_html=True)
    progress_ph.progress(traite / total if total > 0 else 0)


def render_step(label, pos=""):
    step_ph.markdown(f"""
    <div class="step-box">
      <span class="step-pos">{pos} </span><span class="step-mat">{label}</span>
    </div>""", unsafe_allow_html=True)


def render_kpis(ok, fail, introuvable):
    kpi_ph.markdown(f"""
    <div class="kpi-grid">
      <div class="kpi-card">
        <div class="kpi-lbl">Moyenne(s) d'orientation trouvées</div>
        <div class="kpi-val-g">{ok}</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-lbl">Moyenne(s) d'orientation Non détectées</div>
        <div class="kpi-val-r">{fail}</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-lbl">Moyenne(s) d'orientation Introuvables</div>
        <div class="kpi-val">{introuvable}</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-lbl">Total Moyenne(s) d'orientation traités</div>
        <div class="kpi-val">{ok + fail + introuvable}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)


def render_mo_live(mo_val, matricule, source):
    if mo_val is not None:
        mo_live_ph.markdown(f"""
        <div class="mo-live-box">
          <div class="mo-live-label">🟣 Moyenne(s) d'orientation</div>
          <div class="mo-live-val">{mo_val:.2f}</div>
          <div class="mo-live-mat">Matricule : {matricule}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        mo_live_ph.markdown(f"""
        <div class="mo-none-box">
          <div class="mo-none-label">⚠ Moyenne non détectée</div>
          <div class="mo-none-mat">{matricule}</div>
        </div>
        """, unsafe_allow_html=True)


def render_pause(restant, total_p):
    if restant > 0:
        pause_ph.markdown(f"""
        <div class="pause-box">
          <div class="pause-label">⏸ Pause</div>
          <div class="pause-timer">{restant}s</div>
          <div style="font-size:0.58rem;color:rgba(255,215,0,0.25);margin-top:2px;">/ {total_p}s</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        pause_ph.empty()


def render_result_final(results):
    df_r = pd.DataFrame(results)
    n_ok = (df_r["Statut"] == "MO_EXTRAITE").sum()
    n_tot = len(df_r)
    moys = df_r["MO"].dropna()
    avg = f"{moys.mean():.2f}" if len(moys) > 0 else "—"
    mn  = f"{moys.min():.2f}"  if len(moys) > 0 else "—"
    mx  = f"{moys.max():.2f}"  if len(moys) > 0 else "—"
    ts  = datetime.now().strftime("%Y%m%d_%H%M%S")
    fic = f"resultats_MO_{ts}.csv"
    df_r.to_csv(fic, index=False, encoding="utf-8")
    result_ph.markdown(f"""
    <div class="result-box">
      <p class="result-title">✅ Extraction terminée</p>
      <div class="stat-row">
        📊 Total traités : <b>{n_tot}</b><br>
        ✅ MO extraites  : <b class="g">{n_ok}</b><br>
        📈 Moyenne MO    : <b>{avg}</b><br>
        ↕ Min / Max      : <b>{mn}</b> / <b>{mx}</b>
      </div>
      <div class="file-tag">💾 {fic}</div>
    </div>
    """, unsafe_allow_html=True)


# ==========================================================
# ÉTAT INITIAL
# ==========================================================
if not st.session_state.running and not st.session_state.termine:
    render_capture(None)
    render_progress(0, 1)
    render_step("En attente de lancement")
    render_kpis(0, 0, 0)
    mo_live_ph.markdown(
        '<div style="color:white;font-size:0.68rem;letter-spacing:2px;'
        'text-transform:uppercase;text-align:center; align-items:center; padding:20px;">'
        'Zone des moyennes en attente</div>', unsafe_allow_html=True
    )
    result_ph.markdown(
        '<div style="color:rgba(255,215,0,0.1);font-size:0.65rem;letter-spacing:2px;'
        'text-transform:uppercase;text-align:center;padding:12px;">En attente</div>',
        unsafe_allow_html=True
    )


# ==========================================================
# BOUCLE D'EXTRACTION
# ==========================================================
if st.session_state.running:

    matricules = df_data.iloc[start_idx - 1: end_idx]["MATRICULE"].astype(str).tolist()
    a_traiter  = len(matricules)

    render_step("Initialisation Chrome...")
    render_progress(0, a_traiter)
    render_kpis(0, 0, 0)

    driver = None
    try:
        driver = webdriver.Chrome(options=construire_chrome_options())
        driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )
        driver.set_window_size(1440, 1080)
        base_url = "https://bourses.mendob.ci/index.php?adr=consultnotesbepc.inc"

        for i, matricule in enumerate(matricules):

            if st.session_state.stop_flag:
                render_step("⏹ Arrêt demandé")
                break

            pos = i + 1

            # ── PAUSES ──────────────────────────────────────────
            if pause_manuelle > 0 and pos > 1:
                p = pause_manuelle
                render_step(f"Pause {p}s...", f"[{pos}/{a_traiter}]")
                for t in range(p, 0, -1):
                    render_pause(t, p)
                    time.sleep(1)
                render_pause(0, p)
            elif pause_manuelle == 0 and pos > 1:
                if pos % 100 == 0:
                    p = random.randint(45, 90)
                    render_step(f"Pause longue {p}s...", f"[{pos}/{a_traiter}]")
                    for t in range(p, 0, -1):
                        render_pause(t, p)
                        time.sleep(1)
                    render_pause(0, p)
                elif pos % 25 == 0:
                    p = random.randint(15, 30)
                    render_step(f"Pause {p}s...", f"[{pos}/{a_traiter}]")
                    for t in range(p, 0, -1):
                        render_pause(t, p)
                        time.sleep(1)
                    render_pause(0, p)

            render_step(f"Traitement : {matricule}", f"[{pos}/{a_traiter}]")

            try:
                # Chargement page
                driver.get(base_url)
                WebDriverWait(driver, 20).until(
                    lambda d: d.execute_script("return document.readyState") == "complete"
                )
                time.sleep(random.uniform(2, 4))
                render_capture(prendre_screenshot(driver), "PAGE CHARGÉE")

                # Champ matricule
                champ = None
                for sel in [
                    "input[name='matricule']", "input[placeholder*='matricule' i]",
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
                    st.session_state.results.append({
                        "Matricule": matricule, "MO": None,
                        "Statut": "ERREUR_TECHNIQUE",
                        "Détails": "Champ matricule introuvable",
                        "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    })
                    st.session_state.total_fail   += 1
                    st.session_state.total_traite += 1
                    render_mo_live(None, matricule, "Champ introuvable")
                    render_kpis(
                        st.session_state.total_ok,
                        st.session_state.total_fail,
                        st.session_state.total_introuvable
                    )
                    render_progress(st.session_state.total_traite, a_traiter)
                    continue

                # Saisie
                render_step(f"Saisie matricule : {matricule}", f"[{pos}/{a_traiter}]")
                champ.clear()
                time.sleep(0.4)
                for char in str(matricule):
                    champ.send_keys(char)
                    time.sleep(random.uniform(0.08, 0.22))
                render_capture(prendre_screenshot(driver), "SAISIE")

                # Soumission
                try:
                    btn = driver.find_element(
                        By.CSS_SELECTOR,
                        "button[type='submit'], input[type='submit'], .btn, button"
                    )
                    driver.execute_script("arguments[0].click();", btn)
                except Exception:
                    champ.send_keys(Keys.RETURN)

                render_step(f"Attente résultats... → {matricule}", f"[{pos}/{a_traiter}]")
                time.sleep(random.uniform(6, 12))
                render_capture(prendre_screenshot(driver, scroll_bottom=True), "RÉSULTATS")

                # Vérification page
                page_text = driver.find_element(By.TAG_NAME, "body").text.lower()
                mots_err  = [
                    "matricule non reconnu", "introuvable", "non trouvé",
                    "not found", "aucun résultat", "erreur"
                ]

                if any(m in page_text for m in mots_err):
                    st.session_state.results.append({
                        "Matricule": matricule, "MO": None,
                        "Statut": "MATRICULE_INTROUVABLE",
                        "Détails": "Absent de la base Mendob",
                        "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    })
                    st.session_state.total_introuvable += 1
                    render_mo_live(None, matricule, "Matricule inconnu")
                else:
                    # Extraction MO — 5 méthodes
                    render_step(f"Extraction MO zone violette... → {matricule}", f"[{pos}/{a_traiter}]")
                    mo_val, mo_src = extraire_moyenne_orientation_mendob(driver)

                    # Screenshot final avec statut MO
                    render_capture(
                        prendre_screenshot(driver, scroll_bottom=True),
                        f"MO = {mo_val:.2f}" if mo_val else "MO NON DÉTECTÉE"
                    )
                    render_mo_live(mo_val, matricule, mo_src or "")

                    if mo_val is not None:
                        st.session_state.results.append({
                            "Matricule": matricule, "MO": mo_val,
                            "Statut": "MO_EXTRAITE",
                            "Détails": (mo_src or "")[:100],
                            "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        })
                        st.session_state.total_ok += 1
                    else:
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

                render_kpis(
                    st.session_state.total_ok,
                    st.session_state.total_fail,
                    st.session_state.total_introuvable
                )
                render_progress(st.session_state.total_traite, a_traiter)

                if pause_manuelle == 0:
                    time.sleep(random.uniform(3, 8))
                driver.delete_all_cookies()

            except Exception as ex:
                try:
                    render_capture(prendre_screenshot(driver), "ERREUR")
                except Exception:
                    pass
                st.session_state.results.append({
                    "Matricule": matricule, "MO": None,
                    "Statut": "ERREUR_TECHNIQUE",
                    "Détails": str(ex)[:100],
                    "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                })
                st.session_state.total_fail   += 1
                st.session_state.total_traite += 1
                render_mo_live(None, matricule, f"Erreur: {str(ex)[:35]}")
                render_kpis(
                    st.session_state.total_ok,
                    st.session_state.total_fail,
                    st.session_state.total_introuvable
                )
                render_progress(st.session_state.total_traite, a_traiter)
                time.sleep(5)

    except Exception as ex:
        render_step(f"Erreur fatale: {str(ex)[:60]}")
        if st.session_state.results:
            urg = f"urgence_MO_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            pd.DataFrame(st.session_state.results).to_csv(urg, index=False, encoding="utf-8")

    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass
        st.session_state.running   = False
        st.session_state.termine   = True
        st.session_state.stop_flag = False
        render_kpis(
            st.session_state.total_ok,
            st.session_state.total_fail,
            st.session_state.total_introuvable
        )
        render_progress(
            st.session_state.total_traite,
            st.session_state.total_a_traiter or 1
        )
        render_step("✅ Extraction terminée")
        pause_ph.empty()
        if st.session_state.results:
            render_result_final(st.session_state.results)


# ==========================================================
# ÉTAT TERMINÉ
# ==========================================================
if st.session_state.termine and st.session_state.results and not st.session_state.running:
    render_kpis(
        st.session_state.total_ok,
        st.session_state.total_fail,
        st.session_state.total_introuvable
    )
    render_progress(
        st.session_state.total_traite,
        st.session_state.total_a_traiter or 1
    )
    render_result_final(st.session_state.results)
