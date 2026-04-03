import streamlit as st
from pharmacy import Pharmacy
from llm import LLM

# ── PAGE CONFIG ────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="SmartRx",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── GLOBAL CSS ─────────────────────────────────────────────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=DM+Sans:wght@300;400;500&display=swap');

/* ── reset & base ── */
*, *::before, *::after { box-sizing: border-box; }

html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
    background: #f5f4f0 !important;
    font-family: 'DM Sans', sans-serif !important;
}

[data-testid="stMainBlockContainer"] {
    max-width: 1100px !important;
    padding: 2rem 2.5rem 4rem !important;
    margin: 0 auto !important;
}

/* hide ALL streamlit chrome — toolbar, top colour bar, header, footer */
[data-testid="stToolbar"]              { display: none !important; }
[data-testid="stDecoration"]           { display: none !important; }
[data-testid="stHeader"]               { display: none !important; }
header[data-testid="stHeader"]         { display: none !important; }
footer                                 { display: none !important; }
#MainMenu                              { display: none !important; }
.stAppDeployButton                     { display: none !important; }
/* remove top padding streamlit adds to compensate for hidden header */
[data-testid="stAppViewContainer"] > section:first-child { padding-top: 0 !important; }
[data-testid="stMainBlockContainer"] { padding-top: 2rem !important; }

/* ── header ── */
.srx-header {
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    padding-bottom: 1.5rem;
    margin-bottom: 2rem;
    border-bottom: 1px solid rgba(0,0,0,0.14);
}
.srx-wordmark {
    font-family: 'Instrument Serif', serif;
    font-size: 32px;
    color: #111210;
    letter-spacing: -0.5px;
    line-height: 1;
}
.srx-wordmark em { font-style: italic; color: #2d7a50; }
.srx-tagline { font-size: 12px; color: #8a8a84; margin-top: 5px; font-weight: 300; }
.srx-badge {
    font-size: 11px; color: #2d7a50;
    background: #edf7f1; border: 1px solid #c8e8d4;
    padding: 4px 12px; border-radius: 999px; font-weight: 500;
}

/* ── eyebrow labels ── */
.srx-eyebrow {
    font-size: 11px; font-weight: 500; letter-spacing: 0.08em;
    text-transform: uppercase; color: #4a4a46; margin-bottom: 0.6rem;
    display: block;
}

/* ── input card — style the streamlit block that holds input + button ── */
div[data-testid="stHorizontalBlock"]:has(div[data-testid="stTextInput"]) {
    background: #ffffff;
    border: 1px solid rgba(0,0,0,0.12);
    border-radius: 16px;
    padding: 1.1rem 1.25rem;
    margin-bottom: 1rem;
}

/* ── med found bar ── */
.srx-med-bar {
    display: flex; align-items: center; justify-content: space-between;
    background: #edf7f1; border: 1px solid #c8e8d4;
    border-radius: 10px; padding: 10px 16px; margin-bottom: 1.5rem;
}
.srx-med-bar-left { display: flex; align-items: center; gap: 10px; }
.srx-med-dot { width: 8px; height: 8px; border-radius: 50%; background: #2d7a50; flex-shrink: 0; display: inline-block; }
.srx-med-name { font-size: 15px; font-weight: 500; color: #1c4a32; }
.srx-med-meta { font-size: 13px; color: #2d6644; margin-top: 1px; }
.srx-pill-green {
    font-size: 12px; font-weight: 500; padding: 4px 12px;
    border-radius: 999px; background: #c8e8d4; color: #1c4a32;
}

/* ── divider ── */
.srx-divider {
    display: flex; align-items: center; gap: 12px;
    margin: 1.75rem 0 1.25rem;
}
.srx-divider-line { flex: 1; height: 1px; background: rgba(0,0,0,0.18); }
.srx-divider-label {
    font-size: 11px; font-weight: 500; letter-spacing: 0.08em;
    text-transform: uppercase; color: #4a4a46;
}

/* ── risk cards ── */
.srx-risk-card {
    border-radius: 10px; padding: 14px 16px;
    display: grid; grid-template-columns: 18px 1fr;
    gap: 0 14px; align-items: start;
    border: 1px solid transparent;
    margin-bottom: 8px;
}
.srx-risk-card.severe  { background: #fdf0f0; border-color: #f0bebe; }
.srx-risk-card.moderate{ background: #fdf6e3; border-color: #f0d080; }
.srx-risk-card.mild    { background: #edf7f1; border-color: #c8e8d4; }
.srx-sev-label {
    writing-mode: vertical-rl; text-orientation: mixed;
    transform: rotate(180deg); font-size: 9px; font-weight: 500;
    letter-spacing: 0.12em; text-transform: uppercase;
    display: flex; align-items: center; justify-content: center;
    height: 100%;
}
.srx-risk-card.severe  .srx-sev-label { color: #7a1c1c; }
.srx-risk-card.moderate .srx-sev-label { color: #7a5000; }
.srx-risk-card.mild    .srx-sev-label { color: #1c4a32; }
.srx-risk-name { font-size: 14px; font-weight: 500; color: #111210; }
.srx-risk-symptoms { font-size: 13px; color: #2a2a28; margin-top: 4px; line-height: 1.6; }
.srx-risk-trigger {
    font-size: 12px; color: #6b6b66; margin-top: 6px;
    display: flex; align-items: center; gap: 6px;
}
.srx-risk-trigger::before {
    content: ''; display: inline-block;
    width: 12px; height: 1px; background: #6b6b66;
}

/* ── split panel ── */
.srx-split {
    display: grid; grid-template-columns: 1fr 1fr;
    border: 1px solid rgba(0,0,0,0.14);
    border-radius: 16px; overflow: hidden;
    margin-bottom: 1.75rem;
    background: #fff;
}
.srx-split-left  { background: #fff; border-right: 1px solid rgba(0,0,0,0.14); }
.srx-split-right { background: #f9f8f5; }
.srx-split-header {
    padding: 1rem 1.25rem 0.85rem;
    border-bottom: 1px solid rgba(0,0,0,0.08);
}
.srx-split-title {
    font-family: 'Instrument Serif', serif;
    font-size: 22px; color: #111210; line-height: 1.1;
}
.srx-split-title.conflict { color: #7a1c1c; }
.srx-split-sub { font-size: 13px; color: #4a4a46; margin-top: 4px; }

/* ── question items ── */
.srx-q-wrap { padding: 1rem 1.25rem; }
.srx-q-item {
    border: 1px solid rgba(0,0,0,0.08); border-radius: 10px;
    padding: 11px 13px; background: #f5f4f0; margin-bottom: 9px;
}
.srx-q-item.ans-no  { border-color: #c8e8d4; background: #edf7f1; }
.srx-q-item.ans-yes { border-color: #f0bebe; background: #fdf0f0; }
.srx-q-top { display: flex; gap: 9px; margin-bottom: 6px; }
.srx-q-num {
    font-family: 'Instrument Serif', serif; font-style: italic;
    font-size: 22px; color: #8a8a84; line-height: 1; flex-shrink: 0;
}
.srx-q-text { font-size: 13px; color: #111210; line-height: 1.7; padding-top: 3px; }

/* ── cross-reactivity ── */
.srx-crossreact {
    margin: 0.75rem 1.25rem 0.25rem;
    background: #fdf6e3; border: 1px solid #f0d080;
    border-radius: 10px; padding: 9px 12px;
    display: flex; gap: 10px;
}
.srx-crossreact-bar { width: 3px; background: #e8c840; border-radius: 99px; flex-shrink: 0; }
.srx-crossreact-eyebrow {
    font-size: 10px; font-weight: 600; text-transform: uppercase;
    letter-spacing: 0.08em; color: #7a5000; margin-bottom: 4px;
}
.srx-crossreact-text { font-size: 13px; color: #2a2a28; line-height: 1.65; }

/* ── split footer ── */
.srx-split-footer {
    padding: 0.75rem 1.25rem;
    border-top: 1px solid rgba(0,0,0,0.08);
}
.srx-physician-note {
    font-size: 12px; color: #4a4a46; font-style: italic; margin-bottom: 8px;
}

/* ── alternatives ── */
.srx-alt-wrap { padding: 1rem 1.25rem; }
.srx-alt-intro { font-size: 13px; color: #2a2a28; line-height: 1.6; margin-bottom: 10px; }
.srx-alt-card {
    background: #fff; border: 1px solid rgba(0,0,0,0.10);
    border-radius: 10px; padding: 12px 14px; margin-bottom: 9px;
}
.srx-alt-card.top-pick { border-color: #a8d8b8; background: #edf7f1; }
.srx-alt-head { display: flex; align-items: center; justify-content: space-between; margin-bottom: 4px; }
.srx-alt-name { font-size: 14px; font-weight: 500; color: #111210; }
.srx-alt-tag {
    font-size: 11px; font-weight: 500; padding: 3px 9px;
    border-radius: 999px; background: #c8e8d4; color: #1c4a32;
}
.srx-alt-meta { font-size: 12px; color: #4a4a46; margin-bottom: 6px; }
.srx-alt-reason { font-size: 13px; color: #2a2a28; line-height: 1.65; }
.srx-alt-footer { display: flex; align-items: center; justify-content: space-between; margin-top: 8px; }
.srx-alt-stock { font-size: 12px; color: #4a4a46; }
.srx-stock-track { width: 56px; height: 3px; background: rgba(0,0,0,0.1); border-radius: 99px; overflow: hidden; display: inline-block; vertical-align: middle; margin-left: 6px; }
.srx-stock-fill  { height: 100%; border-radius: 99px; background: #2d7a50; }

/* ── clear result ── */
.srx-clear {
    background: #edf7f1; border: 1px solid #c8e8d4;
    border-radius: 16px; padding: 2.5rem 1.5rem;
    text-align: center; margin-top: 0.5rem;
}
.srx-clear-ring {
    width: 64px; height: 64px; border-radius: 50%;
    border: 1.5px solid #c8e8d4; background: #fff;
    display: flex; align-items: center; justify-content: center;
    margin: 0 auto 1rem; position: relative;
}
.srx-clear-ring::after {
    content: ''; position: absolute; inset: -6px; border-radius: 50%;
    border: 1px solid #c8e8d4; opacity: 0.45;
}
.srx-clear-check {
    font-family: 'Instrument Serif', serif;
    font-size: 28px; color: #2d7a50;
}
.srx-clear-title {
    font-family: 'Instrument Serif', serif;
    font-size: 28px; font-style: italic; color: #1c4a32;
}
.srx-clear-sub { font-size: 14px; color: #2d6644; margin-top: 8px; line-height: 1.7; }

/* ── error bar ── */
.srx-error {
    background: #fdf0f0; border: 1px solid #e8a0a0;
    border-radius: 10px; padding: 12px 16px;
    font-size: 14px; color: #7a1c1c; margin-bottom: 1rem;
}

/* ── streamlit widget overrides — legibility fixes ── */

/* text input — dark text on light background */
div[data-testid="stTextInput"] input {
    border: 1px solid rgba(0,0,0,0.20) !important;
    border-radius: 10px !important;
    font-family: 'DM Sans', sans-serif !important;
    background: #ffffff !important;
    color: #111210 !important;
    height: 42px !important;
    font-size: 14px !important;
}
div[data-testid="stTextInput"] input::placeholder { color: #aaa9a4 !important; }
div[data-testid="stTextInput"] input:focus {
    border-color: #2d7a50 !important;
    box-shadow: 0 0 0 2px rgba(45,122,80,0.12) !important;
    outline: none !important;
}
div[data-testid="stTextInput"] input:focus-visible {
    border-color: #2d7a50 !important;
    box-shadow: 0 0 0 2px rgba(45,122,80,0.12) !important;
    outline: none !important;
}
/* kill streamlit's default red focus ring on the wrapper */
div[data-testid="stTextInput"] > div:focus-within,
div[data-testid="stTextInput"] > div[data-focused="true"],
div[data-testid="stTextInput"] > div {
    box-shadow: none !important;
    border-color: transparent !important;
}
div[data-baseweb="input"]:focus-within {
    border-color: #2d7a50 !important;
    box-shadow: 0 0 0 2px rgba(45,122,80,0.12) !important;
    outline: none !important;
}
div[data-baseweb="input"] {
    border-color: rgba(0,0,0,0.20) !important;
}
/* input label */
div[data-testid="stTextInput"] label {
    color: #4a4a46 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 13px !important;
}

/* buttons — target all text nodes inside */
div[data-testid="stButton"] button {
    border-radius: 10px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    font-size: 13px !important;
}
/* primary button */
div[data-testid="stButton"] button[kind="primary"],
div[data-testid="stButton"] button[data-testid="baseButton-primary"] {
    background: #111210 !important;
    color: #ffffff !important;
    border: none !important;
}
div[data-testid="stButton"] button[kind="primary"] p,
div[data-testid="stButton"] button[kind="primary"] span,
div[data-testid="stButton"] button[data-testid="baseButton-primary"] p,
div[data-testid="stButton"] button[data-testid="baseButton-primary"] span {
    color: #ffffff !important;
}
div[data-testid="stButton"] button[kind="primary"]:hover,
div[data-testid="stButton"] button[data-testid="baseButton-primary"]:hover {
    background: #2d2d2a !important;
}
/* secondary / ghost button */
div[data-testid="stButton"] button[kind="secondary"],
div[data-testid="stButton"] button[data-testid="baseButton-secondary"] {
    background: transparent !important;
    color: #111210 !important;
    border: 1px solid rgba(0,0,0,0.20) !important;
}
div[data-testid="stButton"] button[kind="secondary"] p,
div[data-testid="stButton"] button[kind="secondary"] span,
div[data-testid="stButton"] button[data-testid="baseButton-secondary"] p,
div[data-testid="stButton"] button[data-testid="baseButton-secondary"] span {
    color: #111210 !important;
}

/* radio buttons */
div[data-testid="stRadio"] label {
    font-size: 13px !important;
    font-family: 'DM Sans', sans-serif !important;
    color: #111210 !important;
}
div[data-testid="stRadio"] > div { gap: 4px !important; }

/* spinner text */
div[data-testid="stSpinner"] p {
    color: #4a4a46 !important;
    font-family: 'DM Sans', sans-serif !important;
}

/* any paragraph / markdown text streamlit renders */
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li,
[data-testid="stMarkdownContainer"] span {
    color: #111210 !important;
    font-family: 'DM Sans', sans-serif !important;
}

/* column gap */
div[data-testid="stColumns"] { gap: 0 !important; }
</style>
""", unsafe_allow_html=True)


# ── HELPERS ───────────────────────────────────────────────────────────────────

def severity_class(severity: str) -> str:
    return {"Severe": "severe", "Moderate": "moderate", "Mild": "mild"}.get(severity, "mild")


def stock_pct(qty: int) -> int:
    return min(int((qty / 150) * 100), 100)


# ── SESSION STATE ─────────────────────────────────────────────────────────────

_DEFAULTS = {
    "summary":        None,
    "questions":      [],
    "crossreact":     "",
    "responses":      {},
    "submitted":      False,
    "recommendation": None,
}

def init_state():
    """Ensure every key exists — safe to call on every rerun."""
    for key, default in _DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = default

def reset_state():
    """Clear all keys then re-initialise to defaults."""
    for key in _DEFAULTS:
        st.session_state.pop(key, None)
    init_state()

init_state()


# ── HEADER ────────────────────────────────────────────────────────────────────

st.markdown("""
<div class="srx-header">
  <div>
    <div class="srx-wordmark">Smart<em>Rx</em></div>
    <div class="srx-tagline">AI-powered allergy screening · Point of dispensing</div>
  </div>
  <div class="srx-badge">Pharmacist view</div>
</div>
""", unsafe_allow_html=True)


# ── PRESCRIPTION INPUT ────────────────────────────────────────────────────────

st.markdown('<span class="srx-eyebrow">Prescription</span>', unsafe_allow_html=True)

col_input, col_btn = st.columns([5, 1])
with col_input:
    med_input = st.text_input(
        "Medication name",
        placeholder="e.g. Amoxicillin",
        label_visibility="collapsed",
        key="med_input",
    )
with col_btn:
    analyse = st.button("Analyse", type="primary", use_container_width=True)

if analyse and med_input.strip():
    reset_state()
    with st.spinner("Looking up prescription and checking allergy data…"):
        st.session_state.summary = Pharmacy.get_allergy_summary(med_input.strip())

    summary = st.session_state.summary
    if summary["found"] and summary["risks"]:
        with st.spinner("Generating screening questions with Gemini…"):
            result = LLM.generate_screening_questions(
                medication_name=summary["medication"]["medication_name"],
                ingredients=summary["ingredients"],
                risks=summary["risks"],
            )
            st.session_state.questions  = result.questions
            st.session_state.crossreact = result.cross_reactivity_note

elif analyse and not med_input.strip():
    st.markdown('<div class="srx-error">Please enter a medication name before clicking Analyse.</div>', unsafe_allow_html=True)


# ── RESULTS ───────────────────────────────────────────────────────────────────

summary = st.session_state.summary

if summary is None:
    st.stop()

# medication not found
if not summary["found"]:
    st.markdown(
        f'<div class="srx-error">No medication matching <strong>{med_input}</strong> was found in the inventory. Please check the spelling and try again.</div>',
        unsafe_allow_html=True,
    )
    st.stop()

med = summary["medication"]

# ── MED FOUND BAR ─────────────────────────────────────────────────────────────

st.markdown(f"""
<div class="srx-med-bar">
  <div class="srx-med-bar-left">
    <span class="srx-med-dot"></span>
    <div>
      <div class="srx-med-name">{med['medication_name']}</div>
      <div class="srx-med-meta">{med['dosage_form']} · {med['strength']} · {med['therapeutic_class']} · {med['stock_quantity']} units in stock</div>
    </div>
  </div>
  <span class="srx-pill-green">Found in inventory</span>
</div>
""", unsafe_allow_html=True)

# ── NO RISKS — safe to dispense immediately ───────────────────────────────────

if not summary["risks"]:
    st.markdown("""
    <div class="srx-divider"><div class="srx-divider-line"></div><div class="srx-divider-label">Result</div><div class="srx-divider-line"></div></div>
    <div class="srx-clear">
      <div class="srx-clear-ring"><span class="srx-clear-check">✓</span></div>
      <div class="srx-clear-title">Clear to dispense</div>
      <div class="srx-clear-sub">No known allergy risks found for this medication. Safe to dispense.</div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ── ALLERGY RISKS ─────────────────────────────────────────────────────────────

st.markdown("""
<div class="srx-divider">
  <div class="srx-divider-line"></div>
  <div class="srx-divider-label">Allergy risks detected</div>
  <div class="srx-divider-line"></div>
</div>
""", unsafe_allow_html=True)

risk_html = ""
for risk in summary["risks"]:
    sev = severity_class(risk["severity"])
    risk_html += f"""
    <div class="srx-risk-card {sev}">
      <div class="srx-sev-label">{risk['severity']}</div>
      <div>
        <div class="srx-risk-name">{risk['allergy_name']}</div>
        <div class="srx-risk-symptoms">{risk['symptoms']}</div>
        <div class="srx-risk-trigger">{risk['ingredient_name']} · {risk['ingredient_class']}</div>
      </div>
    </div>"""
st.markdown(risk_html, unsafe_allow_html=True)

# ── SCREENING + CONFLICT SPLIT ────────────────────────────────────────────────

if not st.session_state.questions:
    st.stop()

questions  = st.session_state.questions
crossreact = st.session_state.crossreact
alternatives = summary["alternatives"]

st.markdown("""
<div class="srx-divider">
  <div class="srx-divider-line"></div>
  <div class="srx-divider-label">Screening · Outcome</div>
  <div class="srx-divider-line"></div>
</div>
""", unsafe_allow_html=True)

col_left, col_right = st.columns(2, gap="small")

# ── LEFT: QUESTIONS ───────────────────────────────────────────────────────────

with col_left:
    st.markdown("""
    <div style="background:#fff;border:1px solid rgba(0,0,0,0.14);border-radius:16px;overflow:hidden;">
      <div class="srx-split-header">
        <div class="srx-split-title">Screening questions</div>
        <div class="srx-split-sub">Work through each question with the patient</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # render questions with radio buttons
    responses = {}
    for i, q in enumerate(questions):
        ans = st.session_state.responses.get(i, "No")
        item_class = "ans-no" if ans == "No" else "ans-yes"

        st.markdown(f"""
        <div class="srx-q-item {item_class}">
          <div class="srx-q-top">
            <div class="srx-q-num">0{i+1}</div>
            <div class="srx-q-text">{q}</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        choice = st.radio(
            label=f"q{i}",
            options=["No", "Yes"],
            index=0 if ans == "No" else 1,
            horizontal=True,
            label_visibility="collapsed",
            key=f"radio_{i}",
        )
        responses[i] = choice

    st.session_state.responses = responses

    # physician note + buttons
    st.markdown('<div class="srx-physician-note">If unsure, contact the prescribing physician before dispensing.</div>', unsafe_allow_html=True)

    col_reset, col_submit = st.columns([1, 2])
    with col_reset:
        if st.button("Reset", use_container_width=True):
            reset_state()
            st.rerun()
    with col_submit:
        if st.button("Submit responses", type="primary", use_container_width=True):
            st.session_state.submitted = True
            confirmed = [
                summary["risks"][i]["allergy_name"]
                for i, v in responses.items()
                if v == "Yes" and i < len(summary["risks"])
            ]
            if confirmed and alternatives:
                with st.spinner("Generating recommendation…"):
                    st.session_state.recommendation = LLM.generate_alternative_recommendation(
                        medication_name=med["medication_name"],
                        confirmed_allergies=confirmed,
                        alternatives=alternatives,
                    )  # returns RecommendationOutput
            st.rerun()


# ── RIGHT: CONFLICT / OUTCOME ─────────────────────────────────────────────────

with col_right:
    any_yes = any(v == "Yes" for v in st.session_state.responses.values())
    submitted = st.session_state.submitted

    if not submitted:
        # waiting state
        st.markdown("""
        <div style="background:#f9f8f5;border:1px solid rgba(0,0,0,0.14);border-radius:16px;overflow:hidden;height:100%;">
          <div class="srx-split-header">
            <div class="srx-split-title">Outcome</div>
            <div class="srx-split-sub">Submit responses to see the result</div>
          </div>
          <div style="padding:2rem 1.25rem;text-align:center;color:#c0bfb8;font-size:13px;">
            Complete the screening questions on the left and click <em>Submit responses</em>.
          </div>
        </div>
        """, unsafe_allow_html=True)

    elif any_yes:
        # build the entire conflict panel as one html block
        rec = st.session_state.recommendation  # RecommendationOutput | None

        # determine top pick by searching the structured recommendation sentence
        top_pick_name = alternatives[0]["medication_name"] if alternatives else ""
        if rec and alternatives:
            rec_lower = rec.recommendation.lower()
            for alt in alternatives:
                if alt["medication_name"].lower() in rec_lower:
                    top_pick_name = alt["medication_name"]
                    break

        alt_count = len(alternatives)
        plural = "s" if alt_count != 1 else ""

        # header
        html = f"""
        <div style="background:#f9f8f5;border:1px solid rgba(0,0,0,0.14);border-radius:16px;overflow:hidden;">
          <div class="srx-split-header">
            <div class="srx-split-title conflict">Conflict detected</div>
            <div class="srx-split-sub">{alt_count} safer alternative{plural} available in stock</div>
          </div>
        """

        # cross-reactivity note
        if crossreact and crossreact.lower() != "none identified.":
            html += f"""
          <div class="srx-crossreact" style="margin:0.75rem 1.25rem 0;">
            <div class="srx-crossreact-bar"></div>
            <div>
              <div class="srx-crossreact-eyebrow">AI · Cross-reactivity note</div>
              <div class="srx-crossreact-text">{crossreact}</div>
            </div>
          </div>
            """

        # no alternatives fallback
        if not alternatives:
            html += """
          <div style="padding:1rem 1.25rem;font-size:13px;color:#7a1c1c;line-height:1.6;">
            No in-stock alternatives found in the same therapeutic class.
            Please contact the prescribing physician.
          </div>
            """
        else:
            html += f'<div class="srx-alt-wrap">'
            html += f'<div class="srx-alt-intro">Alternatives carry no known cross-reactivity with <strong>{med["therapeutic_class"]}</strong> and are currently in stock.</div>'

            for alt in alternatives:
                is_top = alt["medication_name"] == top_pick_name
                card_class = "srx-alt-card top-pick" if is_top else "srx-alt-card"
                pct = stock_pct(alt["stock_quantity"])
                tag = '<span class="srx-alt-tag">Top pick</span>' if is_top else ""
                html += f"""
                <div class="{card_class}">
                  <div class="srx-alt-head">
                    <div class="srx-alt-name">{alt['medication_name']}</div>
                    {tag}
                  </div>
                  <div class="srx-alt-meta">{alt['dosage_form']} · {alt['strength']} · {alt['therapeutic_class']}</div>
                  <div class="srx-alt-footer">
                    <div class="srx-alt-stock">{alt['stock_quantity']} units in stock</div>
                    <div class="srx-stock-track"><div class="srx-stock-fill" style="width:{pct}%"></div></div>
                  </div>
                </div>"""

            html += "</div>"

            # gemini recommendation
            if rec:
                import html as _html
                analysis_safe = _html.escape(rec.analysis).replace("\n", "<br>")
                rec_safe = _html.escape(rec.recommendation)
                html += f"""
          <div style="margin:0 1.25rem 1rem;padding:12px 14px;background:#fff;border:1px solid rgba(0,0,0,0.10);border-radius:10px;font-size:13px;color:#2a2a28;line-height:1.7;">
            {analysis_safe}<br><br><strong>Recommendation:</strong> {rec_safe}
          </div>
                """

        html += "</div>"
        st.markdown(html, unsafe_allow_html=True)

    else:
        # all No — show clear result inside right panel
        st.markdown("""
        <div style="background:#edf7f1;border:1px solid #c8e8d4;border-radius:16px;overflow:hidden;height:100%;">
          <div class="srx-split-header" style="border-bottom:1px solid #c8e8d4;">
            <div class="srx-split-title" style="color:#1c4a32;">All clear</div>
            <div class="srx-split-sub">No conflicts detected</div>
          </div>
          <div style="padding:2rem 1.25rem;text-align:center;">
            <div class="srx-clear-ring"><span class="srx-clear-check">✓</span></div>
            <div class="srx-clear-title" style="margin-top:1rem;">Clear to dispense</div>
            <div class="srx-clear-sub">All screening questions returned negative.<br>No allergy conflicts detected.</div>
          </div>
        </div>
        """, unsafe_allow_html=True)


# ── CLEAR RESULT BELOW SPLIT (all-No path) ────────────────────────────────────

if st.session_state.submitted and not any(v == "Yes" for v in st.session_state.responses.values()):
    st.markdown("""
    <div class="srx-divider">
      <div class="srx-divider-line"></div>
      <div class="srx-divider-label">Result</div>
      <div class="srx-divider-line"></div>
    </div>
    <div class="srx-clear">
      <div class="srx-clear-ring"><span class="srx-clear-check">✓</span></div>
      <div class="srx-clear-title">Clear to dispense</div>
      <div class="srx-clear-sub">No allergy conflicts detected. All screening questions returned negative.</div>
    </div>
    """, unsafe_allow_html=True)