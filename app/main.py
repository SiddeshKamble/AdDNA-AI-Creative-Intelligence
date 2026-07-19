from __future__ import annotations
from datetime import datetime
from html import escape
from io import BytesIO
import base64
import json
from pathlib import Path
import sys
from typing import Any, Dict, List, Tuple, Union
import zipfile

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
import streamlit as st
from models.market import AdProvider, MarketQuery
from pipeline.orchestrator import AdDNAPipeline

st.set_page_config(
    page_title="AdDNA: AI Creative Intelligence",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown(
    """
<style>
:root{
  --bg:#f5f5f7;
  --surface:#fff;
  --surface-soft:#f0f0f3;
  --text:#1d1d1f;
  --muted:#6e6e73;
  --line:#d9d9df;
  --dark:#1d1d1f;
  --sidebar:#151517;
  --field:#252528;
}
html,body,[class*="css"],.stApp{
  font-family:-apple-system,BlinkMacSystemFont,"SF Pro Text","SF Pro Display","Helvetica Neue",Arial,sans-serif!important;
}
.stApp{background:var(--bg);color:var(--text)}
.block-container{max-width:1280px;padding-top:2.25rem;padding-bottom:3rem}

/* New navigation rail */
section[data-testid="stSidebar"]{
  width:268px!important;min-width:268px!important;max-width:268px!important;
  background:var(--sidebar);border-right:1px solid rgba(255,255,255,.08)
}
section[data-testid="stSidebar"]>div{padding:.9rem .8rem 1.1rem!important}
section[data-testid="stSidebar"] *{color:#fff!important}
.rail-brand{display:flex;align-items:center;gap:.55rem;padding:.1rem .1rem .8rem}
.rail-logo{font-size:1.35rem}
.rail-name{font-size:.95rem;font-weight:720;letter-spacing:-.02em}
.rail-sub{font-size:.64rem;color:#9b9ba2!important}
.rail-section{margin:.55rem 0 .18rem;color:#86868d!important;font-size:.59rem;font-weight:750;letter-spacing:.08em;text-transform:uppercase}
.rail-divider{height:1px;background:rgba(255,255,255,.08);margin:.7rem 0 .55rem}
section[data-testid="stSidebar"] input,
section[data-testid="stSidebar"] [data-baseweb="select"]>div,
section[data-testid="stSidebar"] [data-baseweb="input"]>div{
  height:35px!important;min-height:35px!important;background:var(--field)!important;
  border:1px solid rgba(255,255,255,.12)!important;border-radius:9px!important;box-shadow:none!important
}
section[data-testid="stSidebar"] input{font-size:.84rem!important;padding-left:.68rem!important}
section[data-testid="stSidebar"] input::placeholder{color:#7f7f87!important;opacity:1!important}
section[data-testid="stSidebar"] [data-baseweb="select"] span{font-size:.84rem!important}
section[data-testid="stSidebar"] [data-baseweb="tag"]{
  height:24px!important;margin:2px!important;background:#39393e!important;border-radius:7px!important
}
section[data-testid="stSidebar"] [data-baseweb="tag"] span{font-size:.7rem!important}
section[data-testid="stSidebar"] [data-testid="stCheckbox"]{margin:.18rem 0 .06rem!important}
section[data-testid="stSidebar"] [data-testid="stCheckbox"] p{font-size:.8rem!important}
section[data-testid="stSidebar"] [data-testid="stSlider"]{padding:0!important;margin:-.18rem 0 .05rem!important}
section[data-testid="stSidebar"] [data-testid="stSlider"] [role="slider"]{width:14px!important;height:14px!important}
section[data-testid="stSidebar"] .stButton{margin-top:.55rem!important}
section[data-testid="stSidebar"] .stButton>button,
section[data-testid="stSidebar"] .stButton>button:hover,
section[data-testid="stSidebar"] .stButton>button:active{
  height:39px!important;min-height:39px!important;background:#fff!important;color:#1d1d1f!important;
  border:0!important;border-radius:10px!important;font-size:.84rem!important;font-weight:700!important;box-shadow:none!important
}
section[data-testid="stSidebar"] .stButton>button *{color:#1d1d1f!important}

/* Header and export */
.hero{padding:.1rem 0 1rem;border-bottom:1px solid var(--line)}
.hero h1{margin:0;font-size:1.95rem;font-weight:770;letter-spacing:-.04em;color:var(--text)!important}
.hero p{margin:.3rem 0 0;font-size:.9rem;color:var(--muted)!important}
.context{margin:1.05rem 0 .8rem}
.context h2{margin:0;font-size:1.3rem;letter-spacing:-.025em}
.context p{margin:.22rem 0 0;color:var(--muted);font-size:.83rem}
.export-title{margin-bottom:.2rem;color:var(--muted)!important;font-size:.59rem;font-weight:750;letter-spacing:.075em;text-transform:uppercase}
.export-area [data-testid="stSelectbox"]>div>div,.export-area .stDownloadButton>button{
  height:34px!important;min-height:34px!important;border-radius:9px!important
}
.export-area .stDownloadButton>button,
.export-area .stDownloadButton>button:hover,
.export-area .stDownloadButton>button:active{
  background:#fff!important;color:var(--text)!important;border:1px solid var(--line)!important;font-size:.76rem!important
}
.export-area .stDownloadButton>button *{color:var(--text)!important}

/* KPIs and tabs */
.kpi{min-height:86px;padding:.76rem .82rem;border-radius:14px;background:var(--dark);color:#fff!important}
.kpi *{color:#fff!important}
.kpi-label{font-size:.62rem;font-weight:750;letter-spacing:.065em;text-transform:uppercase;color:#b7b7bd!important}
.kpi-value{margin-top:.2rem;font-size:1.35rem;font-weight:770;letter-spacing:-.03em}
[data-testid="stTabs"]{margin-top:.9rem}
[data-testid="stTabs"] [data-baseweb="tab-list"]{
  display:flex!important;gap:.05rem!important;padding:0!important;background:transparent!important;border-bottom:1px solid var(--line)!important
}
[data-testid="stTabs"] button{
  width:auto!important;min-height:39px!important;padding:.52rem .8rem!important;border-radius:0!important;
  background:transparent!important;color:var(--muted)!important;font-size:.82rem!important;font-weight:630!important;box-shadow:none!important
}
[data-testid="stTabs"] button[aria-selected="true"]{color:var(--text)!important;box-shadow:inset 0 -2px 0 var(--text)!important}
[data-testid="stTabs"] [data-baseweb="tab-highlight"]{display:none!important}
[data-testid="stTabs"] [data-baseweb="tab-panel"]{padding-top:1.2rem!important}

/* Components */
.card,.brief-card,.idea-card,.strategy-card,.notice{
  width:100%;box-sizing:border-box;background:var(--surface);border:1px solid var(--line);
  border-radius:15px;color:var(--text)!important
}
.card *,.brief-card *,.idea-card *,.strategy-card *,.notice *{color:var(--text)!important}
.card{padding:.95rem}.score-card{min-height:126px}.intel-card{min-height:245px}.split-card{min-height:310px}
.title{margin-bottom:.48rem;color:var(--muted)!important;font-size:.63rem;font-weight:750;letter-spacing:.065em;text-transform:uppercase}
.value{margin-bottom:.25rem;font-size:1.4rem;font-weight:770;letter-spacing:-.03em}
.copy,.brief-value,.note,.idea-line{font-size:.86rem;line-height:1.55}
.notice{padding:.72rem .88rem;margin-bottom:.9rem}
.section-title{margin:1.1rem 0 .6rem;font-size:.96rem;font-weight:730;letter-spacing:-.015em}
.intel-item{padding:.65rem 0;border-bottom:1px solid var(--line)}
.intel-item:last-child{border-bottom:0}
.intel-head{display:flex;justify-content:space-between;gap:1rem}
.intel-label{font-weight:690}.pct,.note{color:var(--muted)!important}
.track{height:6px;margin:.32rem 0;overflow:hidden;border-radius:999px;background:#e7e7ec}
.fill{height:100%;border-radius:999px;background:var(--text)}
.brief-card{min-height:138px;padding:.95rem}
.brief-key{margin-bottom:.42rem;color:var(--muted)!important;font-size:.62rem;font-weight:750;letter-spacing:.065em;text-transform:uppercase}
.idea-card{min-height:230px;padding:.95rem}
.idea-name{font-size:.98rem;font-weight:730;letter-spacing:-.02em}.idea-meta{margin:.18rem 0 .55rem;color:var(--muted)!important;font-size:.76rem}
.idea-line{margin:.42rem 0}
.pill{display:inline-block;margin:0 .2rem .2rem 0;padding:.18rem .42rem;border-radius:999px;background:var(--surface-soft);color:var(--muted)!important;font-size:.66rem;font-weight:650}
.strategy-card{min-height:250px;padding:.95rem}
.checklist{margin:.25rem 0 0;padding-left:1rem}.checklist li{margin:.33rem 0;font-size:.84rem;line-height:1.45}
div[data-testid="stHorizontalBlock"]{gap:.9rem!important;align-items:stretch!important}
div[data-testid="stHorizontalBlock"]>div[data-testid="column"]{display:flex!important;flex-direction:column!important}
div[data-testid="stHorizontalBlock"]>div[data-testid="column"]>div{height:100%!important}

/* Readable expanders */
div[data-testid="stExpander"]{
  margin-top:.65rem!important;overflow:hidden!important;border:1px solid var(--line)!important;border-radius:13px!important;background:#fff!important
}
div[data-testid="stExpander"] summary,
div[data-testid="stExpander"] summary:hover,
div[data-testid="stExpander"] summary:focus,
div[data-testid="stExpander"] summary[aria-expanded="true"]{
  min-height:42px!important;background:#fff!important;color:var(--text)!important
}
div[data-testid="stExpander"] summary *{color:var(--text)!important;fill:var(--text)!important}
div[data-testid="stExpander"] [data-testid="stExpanderDetails"]{padding:.85rem .95rem 1rem!important;background:#fff!important;color:var(--text)!important}
[data-testid="stDataFrame"]{overflow:hidden!important;border-radius:13px!important}
*{animation:none!important;transition:border-color 80ms ease,box-shadow 80ms ease!important}
@media(max-width:900px){
  section[data-testid="stSidebar"]{width:auto!important;min-width:auto!important;max-width:none!important}
  .score-card,.intel-card,.split-card,.brief-card,.idea-card,.strategy-card{min-height:auto!important}
}
</style>
""",
    unsafe_allow_html=True,
)

st.markdown(r"""
<style>
/* Final polish */
.export-area div[data-testid="stHorizontalBlock"] {
  gap: .55rem !important;
}
.export-area div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
  flex: 1 1 0 !important;
}
.export-area [data-testid="stSelectbox"],
.export-area .stDownloadButton {
  width: 100% !important;
}
.export-area [data-testid="stSelectbox"] > div > div,
.export-area .stDownloadButton > button {
  width: 100% !important;
  height: 36px !important;
  min-height: 36px !important;
  border-radius: 9px !important;
  box-sizing: border-box !important;
}
.export-area [data-testid="stSelectbox"] > div > div {
  background: #ffffff !important;
  color: #1d1d1f !important;
  border: 1px solid #d9d9df !important;
}
.export-area [data-testid="stSelectbox"] span,
.export-area [data-testid="stSelectbox"] svg {
  color: #1d1d1f !important;
  fill: #1d1d1f !important;
}
.export-area .stDownloadButton > button,
.export-area .stDownloadButton > button:hover,
.export-area .stDownloadButton > button:active,
.export-area .stDownloadButton > button:focus {
  background: #1d1d1f !important;
  color: #ffffff !important;
  border: 1px solid #1d1d1f !important;
}
.export-area .stDownloadButton > button *,
.export-area .stDownloadButton > button:hover *,
.export-area .stDownloadButton > button:active *,
.export-area .stDownloadButton > button:focus * {
  color: #ffffff !important;
  fill: #ffffff !important;
}

/* Cleaner sidebar selects */
section[data-testid="stSidebar"] [data-baseweb="select"] > div {
  padding-left: .15rem !important;
}
section[data-testid="stSidebar"] [data-baseweb="select"] input {
  caret-color: transparent !important;
}
section[data-testid="stSidebar"] [data-baseweb="select"] > div:focus-within {
  border-color: rgba(255,255,255,.22) !important;
}

/* Equal strategy row height */
.strategy-card {
  min-height: 355px !important;
}
@media(max-width:900px){
  .strategy-card{min-height:auto!important}
}
</style>
""", unsafe_allow_html=True)

st.markdown(r"""
<style>
/* Final select cleanup: remove hidden input bubbles/carets */
section[data-testid="stSidebar"] [data-baseweb="select"] input {
  position: absolute !important;
  width: 1px !important;
  min-width: 1px !important;
  max-width: 1px !important;
  height: 1px !important;
  min-height: 1px !important;
  max-height: 1px !important;
  padding: 0 !important;
  margin: 0 !important;
  border: 0 !important;
  opacity: 0 !important;
  pointer-events: none !important;
  caret-color: transparent !important;
}

section[data-testid="stSidebar"] [data-baseweb="select"] > div > div:first-child {
  min-width: 0 !important;
  overflow: hidden !important;
}

section[data-testid="stSidebar"] [data-baseweb="select"] > div {
  padding-left: .7rem !important;
  padding-right: .55rem !important;
}

section[data-testid="stSidebar"] [data-baseweb="select"] svg {
  flex: 0 0 auto !important;
}

/* Download selector and button use the same dark theme */
.export-area [data-testid="stSelectbox"] > div > div,
.export-area .stDownloadButton > button,
.export-area .stDownloadButton > button:hover,
.export-area .stDownloadButton > button:active,
.export-area .stDownloadButton > button:focus {
  width: 100% !important;
  height: 36px !important;
  min-height: 36px !important;
  border-radius: 9px !important;
  box-sizing: border-box !important;
  background: #26262c !important;
  color: #ffffff !important;
  border: 1px solid #26262c !important;
  box-shadow: none !important;
}

.export-area [data-testid="stSelectbox"] span,
.export-area [data-testid="stSelectbox"] svg,
.export-area .stDownloadButton > button *,
.export-area .stDownloadButton > button:hover *,
.export-area .stDownloadButton > button:active *,
.export-area .stDownloadButton > button:focus * {
  color: #ffffff !important;
  fill: #ffffff !important;
  opacity: 1 !important;
}

.export-area [data-testid="stSelectbox"] input {
  opacity: 0 !important;
  width: 1px !important;
  height: 1px !important;
  pointer-events: none !important;
}

/* Market Intelligence extended cards */
.market-signal-card {
  min-height: 280px !important;
}

.market-summary-card {
  min-height: 210px !important;
}

.signal-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: .75rem;
}

.signal-chip {
  padding: .72rem .78rem;
  border-radius: 12px;
  border: 1px solid var(--line);
  background: var(--surface-soft);
}

.signal-name {
  font-size: .72rem;
  color: var(--muted) !important;
  text-transform: uppercase;
  letter-spacing: .055em;
  font-weight: 700;
}

.signal-value {
  margin-top: .2rem;
  font-size: 1rem;
  font-weight: 720;
}

@media(max-width:900px){
  .signal-grid{grid-template-columns:1fr}
  .market-signal-card,.market-summary-card{min-height:auto!important}
}
</style>
""", unsafe_allow_html=True)

st.markdown(r"""
<style>
/* Standard, neutral filter navigation */
section[data-testid="stSidebar"] {
  width: 282px !important;
  min-width: 282px !important;
  max-width: 282px !important;
  background: #1b1b1d !important;
}

section[data-testid="stSidebar"] > div {
  padding: 1rem .9rem 1.2rem !important;
}

.rail-brand {
  padding: .05rem .05rem .85rem !important;
  margin-bottom: .2rem !important;
  border-bottom: 1px solid rgba(255,255,255,.08);
}

.rail-section {
  margin: .72rem 0 .28rem !important;
  color: #a7a7ae !important;
  font-size: .64rem !important;
  font-weight: 700 !important;
  letter-spacing: .055em !important;
  text-transform: uppercase !important;
}

/* Standard control sizing */
section[data-testid="stSidebar"] input,
section[data-testid="stSidebar"] [data-baseweb="select"] > div,
section[data-testid="stSidebar"] [data-baseweb="input"] > div {
  height: 40px !important;
  min-height: 40px !important;
  border-radius: 9px !important;
  background: #27272a !important;
  border: 1px solid #414146 !important;
  box-shadow: none !important;
}

section[data-testid="stSidebar"] input {
  padding-left: .75rem !important;
  font-size: .88rem !important;
}

section[data-testid="stSidebar"] [data-baseweb="select"] > div {
  padding-left: .7rem !important;
  padding-right: .55rem !important;
}

section[data-testid="stSidebar"] [data-baseweb="select"] span {
  font-size: .88rem !important;
  font-weight: 500 !important;
}

section[data-testid="stSidebar"] [data-baseweb="tag"] {
  height: 26px !important;
  margin: 2px 3px 2px 0 !important;
  padding: 0 .45rem !important;
  border-radius: 7px !important;
  background: #3b3b40 !important;
}

section[data-testid="stSidebar"] [data-baseweb="tag"] span {
  font-size: .72rem !important;
}

/* Remove hidden input artifacts inside selects */
section[data-testid="stSidebar"] [data-baseweb="select"] input {
  position: absolute !important;
  width: 1px !important;
  height: 1px !important;
  min-width: 1px !important;
  min-height: 1px !important;
  padding: 0 !important;
  margin: 0 !important;
  border: 0 !important;
  opacity: 0 !important;
  pointer-events: none !important;
  caret-color: transparent !important;
}

section[data-testid="stSidebar"] [data-testid="stCheckbox"] {
  margin: .35rem 0 .2rem !important;
}

section[data-testid="stSidebar"] [data-testid="stCheckbox"] p {
  font-size: .86rem !important;
}

section[data-testid="stSidebar"] [data-testid="stSlider"] {
  margin: -.05rem 0 .2rem !important;
  padding: 0 !important;
}

section[data-testid="stSidebar"] .stButton {
  margin-top: .75rem !important;
}

section[data-testid="stSidebar"] .stButton > button,
section[data-testid="stSidebar"] .stButton > button:hover,
section[data-testid="stSidebar"] .stButton > button:active,
section[data-testid="stSidebar"] .stButton > button:focus {
  height: 42px !important;
  min-height: 42px !important;
  border-radius: 10px !important;
  background: #ffffff !important;
  color: #1d1d1f !important;
  border: 1px solid #ffffff !important;
  box-shadow: none !important;
  transform: none !important;
}

section[data-testid="stSidebar"] .stButton > button * {
  color: #1d1d1f !important;
}

/* Export selector and button: same exact visual treatment */
.export-area div[data-testid="stHorizontalBlock"] {
  gap: .55rem !important;
}

.export-area div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
  flex: 1 1 0 !important;
}

.export-area [data-testid="stSelectbox"],
.export-area .stDownloadButton {
  width: 100% !important;
}

.export-area [data-testid="stSelectbox"] > div > div,
.export-area .stDownloadButton > button,
.export-area .stDownloadButton > button:hover,
.export-area .stDownloadButton > button:active,
.export-area .stDownloadButton > button:focus {
  width: 100% !important;
  height: 38px !important;
  min-height: 38px !important;
  border-radius: 9px !important;
  box-sizing: border-box !important;
  background: #27272a !important;
  color: #ffffff !important;
  border: 1px solid #27272a !important;
  box-shadow: none !important;
  transform: none !important;
  filter: none !important;
}

.export-area [data-testid="stSelectbox"] span,
.export-area [data-testid="stSelectbox"] svg,
.export-area .stDownloadButton > button *,
.export-area .stDownloadButton > button:hover *,
.export-area .stDownloadButton > button:active *,
.export-area .stDownloadButton > button:focus * {
  color: #ffffff !important;
  fill: #ffffff !important;
  opacity: 1 !important;
}

.export-area [data-testid="stSelectbox"] input {
  position: absolute !important;
  width: 1px !important;
  height: 1px !important;
  opacity: 0 !important;
  pointer-events: none !important;
}

/* No hover or click visual changes on download */
.export-area .stDownloadButton > button:hover,
.export-area .stDownloadButton > button:active,
.export-area .stDownloadButton > button:focus {
  background: #27272a !important;
  border-color: #27272a !important;
  color: #ffffff !important;
}

/* Keep the rest of the UI still */
* {
  animation: none !important;
}

@media (max-width: 900px) {
  section[data-testid="stSidebar"] {
    width: auto !important;
    min-width: auto !important;
    max-width: none !important;
  }
}
</style>
""", unsafe_allow_html=True)

st.markdown(r"""
<style>
/* Force export selector and download button to remain visually identical in every state */
.export-area [data-testid="stSelectbox"] > div > div,
.export-area .stDownloadButton > button,
.export-area .stDownloadButton > button:hover,
.export-area .stDownloadButton > button:active,
.export-area .stDownloadButton > button:focus,
.export-area .stDownloadButton > button:focus-visible,
.export-area .stDownloadButton > button:visited,
.export-area .stDownloadButton > button[aria-pressed="true"],
.export-area .stDownloadButton > button[data-testid="stBaseButton-secondary"] {
  width: 100% !important;
  height: 38px !important;
  min-height: 38px !important;
  border-radius: 9px !important;
  box-sizing: border-box !important;
  background: #27272a !important;
  background-color: #27272a !important;
  color: #ffffff !important;
  border: 1px solid #27272a !important;
  box-shadow: none !important;
  transform: none !important;
  filter: none !important;
  opacity: 1 !important;
  outline: none !important;
}

.export-area .stDownloadButton > button *,
.export-area .stDownloadButton > button:hover *,
.export-area .stDownloadButton > button:active *,
.export-area .stDownloadButton > button:focus *,
.export-area .stDownloadButton > button:focus-visible *,
.export-area .stDownloadButton > button:visited * {
  color: #ffffff !important;
  fill: #ffffff !important;
  opacity: 1 !important;
}

.export-area .stDownloadButton > button::before,
.export-area .stDownloadButton > button::after,
.export-area .stDownloadButton > button:hover::before,
.export-area .stDownloadButton > button:hover::after,
.export-area .stDownloadButton > button:active::before,
.export-area .stDownloadButton > button:active::after,
.export-area .stDownloadButton > button:focus::before,
.export-area .stDownloadButton > button:focus::after {
  display: none !important;
  content: none !important;
}

.export-area .stDownloadButton,
.export-area .stDownloadButton:hover,
.export-area .stDownloadButton:active,
.export-area .stDownloadButton:focus {
  background: transparent !important;
  box-shadow: none !important;
  transform: none !important;
}

/* Disable pointer-state styling only; button remains clickable */
.export-area .stDownloadButton > button {
  transition: none !important;
  animation: none !important;
  -webkit-tap-highlight-color: transparent !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown(r"""
<style>
/* Single auto-download menu */
.export-area {
  max-width: 220px !important;
}

.export-area [data-testid="stSelectbox"] {
  width: 100% !important;
}

.export-area [data-testid="stSelectbox"] > div > div,
.export-area [data-testid="stSelectbox"] > div > div:hover,
.export-area [data-testid="stSelectbox"] > div > div:focus-within {
  width: 100% !important;
  height: 38px !important;
  min-height: 38px !important;
  border-radius: 9px !important;
  box-sizing: border-box !important;
  background: #27272a !important;
  color: #ffffff !important;
  border: 1px solid #27272a !important;
  box-shadow: none !important;
  outline: none !important;
}

.export-area [data-testid="stSelectbox"] span,
.export-area [data-testid="stSelectbox"] svg {
  color: #ffffff !important;
  fill: #ffffff !important;
}

.export-area [data-testid="stSelectbox"] input {
  position: absolute !important;
  width: 1px !important;
  height: 1px !important;
  opacity: 0 !important;
  pointer-events: none !important;
}

.export-area [data-testid="stSelectbox"] * {
  transition: none !important;
  animation: none !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown(r"""
<style>
.export-area {
  max-width: 330px !important;
}

.export-area div[data-testid="stHorizontalBlock"] {
  gap: .55rem !important;
  align-items: stretch !important;
}

.export-area div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
  flex: 1 1 0 !important;
}

.export-area [data-testid="stSelectbox"],
.export-area .stDownloadButton {
  width: 100% !important;
}

.export-area [data-testid="stSelectbox"] > div > div,
.export-area .stDownloadButton > button,
.export-area .stDownloadButton > button:hover,
.export-area .stDownloadButton > button:active,
.export-area .stDownloadButton > button:focus,
.export-area .stDownloadButton > button:focus-visible {
  width: 100% !important;
  height: 40px !important;
  min-height: 40px !important;
  border-radius: 10px !important;
  box-sizing: border-box !important;
  background: #27272a !important;
  background-color: #27272a !important;
  color: #ffffff !important;
  border: 1px solid #27272a !important;
  box-shadow: none !important;
  outline: none !important;
  transform: none !important;
  filter: none !important;
  transition: none !important;
  animation: none !important;
  opacity: 1 !important;
  padding: 0 .8rem !important;
  font-size: .82rem !important;
  font-weight: 650 !important;
}

.export-area [data-testid="stSelectbox"] span,
.export-area [data-testid="stSelectbox"] svg,
.export-area .stDownloadButton > button *,
.export-area .stDownloadButton > button:hover *,
.export-area .stDownloadButton > button:active *,
.export-area .stDownloadButton > button:focus *,
.export-area .stDownloadButton > button:focus-visible * {
  color: #ffffff !important;
  fill: #ffffff !important;
  opacity: 1 !important;
}

.export-area [data-testid="stSelectbox"] input {
  position: absolute !important;
  width: 1px !important;
  height: 1px !important;
  min-width: 1px !important;
  min-height: 1px !important;
  opacity: 0 !important;
  pointer-events: none !important;
}

.export-area .stDownloadButton > button::before,
.export-area .stDownloadButton > button::after {
  display: none !important;
  content: none !important;
}

@media (max-width: 900px) {
  .export-area {
    max-width: 100% !important;
  }
}
</style>
""", unsafe_allow_html=True)

st.markdown(r"""
<style>
.export-menu-wrap {
  width: 220px;
  margin-left: auto;
}

.export-title {
  margin-bottom: .22rem;
  color: var(--muted) !important;
  font-size: .6rem;
  font-weight: 750;
  letter-spacing: .075em;
  text-transform: uppercase;
}

.export-menu {
  position: relative;
  width: 100%;
}

.export-menu > summary {
  list-style: none;
  cursor: pointer;
  user-select: none;
  width: 100%;
  height: 40px;
  box-sizing: border-box;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 .9rem;
  border-radius: 10px;
  background: #27272a;
  color: #ffffff !important;
  border: 1px solid #27272a;
  font-size: .84rem;
  font-weight: 650;
}

.export-menu > summary::-webkit-details-marker {
  display: none;
}

.export-menu > summary::after {
  content: "⌄";
  font-size: 1rem;
  line-height: 1;
  color: #ffffff;
}

.export-menu[open] > summary::after {
  content: "⌃";
}

.export-options {
  position: absolute;
  z-index: 999;
  top: 46px;
  left: 0;
  right: 0;
  padding: .35rem;
  border-radius: 10px;
  background: #111216;
  border: 1px solid #27272a;
  box-shadow: 0 12px 28px rgba(0,0,0,.18);
}

.export-option {
  display: block;
  padding: .62rem .7rem;
  border-radius: 8px;
  color: #ffffff !important;
  text-decoration: none !important;
  font-size: .82rem;
  font-weight: 600;
}

.export-option:hover,
.export-option:focus,
.export-option:active {
  background: #27272a;
  color: #ffffff !important;
  text-decoration: none !important;
}

@media (max-width: 900px) {
  .export-menu-wrap {
    width: 100%;
    margin-left: 0;
  }
}
</style>
""", unsafe_allow_html=True)

def safe(value: Any) -> str:
    return escape(str(value))

def html(markup: str) -> None:
    st.markdown(markup.strip(), unsafe_allow_html=True)

def render_kpi(label: str, value: Any) -> None:
    html(
        '<div class="kpi"><div class="kpi-label">{}</div>'
        '<div class="kpi-value">{}</div></div>'.format(
            safe(label), safe(value)
        )
    )

def render_intelligence(
    title: str,
    items: List[Dict[str, Any]],
    note_key: str,
) -> None:
    rows = ""
    for item in items[:5]:
        pct = max(0, min(100, int(item.get("percentage", 0))))
        rows += (
            '<div class="intel-item">'
            '<div class="intel-head"><span class="intel-label">{}</span>'
            '<span class="pct">{}%</span></div>'
            '<div class="track"><div class="fill" style="width:{}%"></div></div>'
            '<div class="note">{}</div></div>'
        ).format(
            safe(item.get("label", "")),
            pct,
            pct,
            safe(item.get(note_key, "")),
        )
    if not rows:
        rows = '<div class="note">No AI-generated evidence is available.</div>'
    html(
        '<div class="card intel-card"><div class="title">{}</div>{}</div>'.format(
            safe(title), rows
        )
    )

def evidence_rows(report: Dict[str, Any]) -> List[Dict[str, Any]]:
    lookup = {
        item["ad_id"]: item for item in report.get("features", [])
    }
    rows = []
    for ad in report.get("ads", []):
        feature = lookup.get(ad.get("source_id"), {})
        rows.append(
            {
                "ID": ad.get("source_id"),
                "Brand": ad.get("brand"),
                "Language": ad.get("language"),
                "Platforms": ", ".join(ad.get("platforms") or []),
                "Hook": feature.get("hook", ""),
                "CTA": feature.get("cta", ""),
                "Format": feature.get("creative_format", ""),
                "Views": ad.get("play_count") or 0,
            }
        )
    return rows

def build_csv(report: Dict[str, Any]) -> str:
    return pd.DataFrame(evidence_rows(report)).to_csv(index=False)

def build_html(report: Dict[str, Any]) -> str:
    intelligence = report.get("intelligence", {})
    market = intelligence.get("market_ai", {})
    brief = report.get("creative_brief", {})
    gaps = "".join(
        "<li><b>{}</b>: {}<br><i>Test:</i> {}</li>".format(
            safe(item.get("gap", "")),
            safe(item.get("evidence", "")),
            safe(item.get("recommended_test", "")),
        )
        for item in market.get("creative_gaps", [])
    )
    brief_items = "".join(
        "<div class='box'><small>{}</small><p>{}</p></div>".format(
            safe(key), safe(value)
        )
        for key, value in brief.items()
        if not isinstance(value, list)
    )
    return """<!doctype html><html><head><meta charset="utf-8">
<title>AdDNA Report</title><style>
body{{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;max-width:980px;margin:40px auto;padding:0 24px;color:#1d1d1f;line-height:1.6}}
section{{margin:24px 0;padding:20px;border:1px solid #ddd;border-radius:16px}}
.grid{{display:grid;grid-template-columns:1fr 1fr;gap:12px}}
.box{{padding:14px;border:1px solid #ddd;border-radius:12px}}
small{{color:#6e6e73;text-transform:uppercase;font-weight:700}}
</style></head><body>
<h1>AdDNA Creative Intelligence Report</h1>
<section><h2>Executive Summary</h2><p>{}</p></section>
<section><h2>Creative Whitespace</h2><ul>{}</ul></section>
<section><h2>Creative Strategy</h2><div class="grid">{}</div></section>
</body></html>""".format(
        safe(report.get("executive_summary", "")),
        gaps,
        brief_items,
    )

def export_payload(
    report: Dict[str, Any],
    export_format: str,
) -> Tuple[Union[bytes, str], str, str]:
    if export_format == "HTML":
        return build_html(report), "addna_report.html", "text/html"
    if export_format == "JSON":
        return (
            json.dumps(report, indent=2, default=str),
            "addna_report.json",
            "application/json",
        )
    if export_format == "CSV":
        return build_csv(report), "addna_evidence.csv", "text/csv"

    bundle = BytesIO()
    with zipfile.ZipFile(bundle, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("addna_report.html", build_html(report))
        archive.writestr(
            "addna_report.json",
            json.dumps(report, indent=2, default=str),
        )
        archive.writestr("addna_evidence.csv", build_csv(report))
    return (
        bundle.getvalue(),
        "addna_complete_report.zip",
        "application/zip",
    )


def _data_uri(data: Union[bytes, str], mime_type: str) -> str:
    raw = data.encode("utf-8") if isinstance(data, str) else data
    encoded = base64.b64encode(raw).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"

def render_export_menu(report: Dict[str, Any]) -> None:
    formats = [
        ("ZIP",) + export_payload(report, "ZIP"),
        ("HTML",) + export_payload(report, "HTML"),
        ("JSON",) + export_payload(report, "JSON"),
        ("CSV",) + export_payload(report, "CSV"),
    ]

    links = []
    for label, data, filename, mime_type in formats:
        links.append(
            f'<a class="export-option" href="{_data_uri(data, mime_type)}" '
            f'download="{safe(filename)}">{safe(label)}</a>'
        )

    html(
        f"""
<div class="export-menu-wrap">
  <div class="export-title">Export</div>
  <details class="export-menu">
    <summary>Download report</summary>
    <div class="export-options">
      {''.join(links)}
    </div>
  </details>
</div>
"""
    )

html(
    '<div class="hero"><h1>🧬 AdDNA: AI Creative Intelligence</h1>'
    '<p>Evidence-led market analysis and campaign strategy.</p></div>'
)

with st.sidebar:
    html(
        '<div class="rail-brand"><div class="rail-logo">🧬</div>'
        '<div><div class="rail-name">AdDNA AI</div>'
        '<div class="rail-sub">Creative Intelligence</div></div></div>'
    )

    html('<div class="rail-section">Market</div>')
    brand = st.text_input(
        "Brand",
        value="",
        placeholder="Brand, e.g. Coca Cola",
        label_visibility="collapsed",
    )
    category = st.text_input(
        "Category",
        value="",
        placeholder="Category, e.g. Cold Drink",
        label_visibility="collapsed",
    )
    html('<div class="rail-section">Region</div>')
    country = st.selectbox(
        "Region",
        ["US", "CA", "UK", "AU", "IN"],
        index=0,
        label_visibility="collapsed",
    )

    html('<div class="rail-section">Source</div>')
    provider = st.selectbox(
        "Source",
        [item.value for item in AdProvider],
        index=0,
        label_visibility="collapsed",
    )
    html('<div class="rail-section">Platforms</div>')
    platforms = st.multiselect(
        "Platforms",
        ["facebook", "instagram", "tiktok"],
        default=["facebook", "instagram", "tiktok"],
        placeholder="Select platforms",
        label_visibility="collapsed",
    )

    html('<div class="rail-divider"></div>')
    english_only = st.checkbox("English only", value=True)
    html('<div class="rail-section">Detection confidence</div>')
    confidence_mode = st.selectbox(
        "Detection confidence",
        [
            "Balanced · 72%",
            "Broad · 60%",
            "Strict · 82%",
            "Very strict · 90%",
        ],
        index=0,
        disabled=not english_only,
        label_visibility="collapsed",
    )
    confidence_values = {
        "Balanced · 72%": 0.72,
        "Broad · 60%": 0.60,
        "Strict · 82%": 0.82,
        "Very strict · 90%": 0.90,
    }
    language_confidence = confidence_values[confidence_mode]

    html('<div class="rail-section">Sample</div>')
    page_size = st.slider(
        "Sample size",
        5,
        50,
        20,
        label_visibility="collapsed",
    )

    run = st.button("Analyze market", use_container_width=True)

if run:
    if not brand.strip() or not category.strip():
        st.error("Enter both a brand and category.")
    else:
        query = MarketQuery(
            brand=brand.strip(),
            category=category.strip(),
            country=country,
            provider=AdProvider(provider),
            platforms=platforms,
            english_only=english_only,
            language_confidence=language_confidence,
            page_size=page_size,
        )
        try:
            with st.spinner("Collecting ads and generating intelligence..."):
                generated_report = AdDNAPipeline().run(query)
            st.session_state["addna_report"] = generated_report
            st.session_state["addna_context"] = {
                "brand": brand.strip(),
                "category": category.strip(),
                "country": country,
                "platforms": platforms,
            }
        except Exception as exc:
            st.error("The analysis could not be completed.")
            st.exception(exc)

report = st.session_state.get("addna_report")
context = st.session_state.get("addna_context", {})

if not report:
    st.info("Complete the market setup in the left navigation and select **Analyze market**.")
    st.stop()

try:
    updated = datetime.fromisoformat(
        report["generated_at"].replace("Z", "+00:00")
    ).strftime("%b %d, %Y · %I:%M %p UTC")
except Exception:
    updated = "Just now"

context_col, export_col = st.columns([3, 1])
with context_col:
    html(
        '<div class="context"><h2>{} · {}</h2>'
        '<p>{} · {} · Updated {}</p></div>'.format(
            safe(context.get("brand", "")),
            safe(context.get("category", "")),
            safe(context.get("country", "")),
            safe(" · ".join(context.get("platforms", [])) or "All platforms"),
            safe(updated),
        )
    )

with export_col:
    render_export_menu(report)

kpis = [
    ("Collected", report["collected_count"]),
    ("English", report.get("filtered_count", report["collected_count"])),
    ("Unique", report["unique_count"]),
    ("Duplicates", "{}%".format(report["duplicate_rate"])),
    ("Active", report["active_count"]),
    ("Views", "{:,}".format(report["total_views"])),
]
for column, metric in zip(st.columns(6), kpis):
    with column:
        render_kpi(metric[0], metric[1])

intelligence = report.get("intelligence", {})
market_ai = intelligence.get("market_ai", {})
ai_available = intelligence.get("ai_available", False)
ai_status = intelligence.get("ai_status", "")
brief = report.get("creative_brief", {})

overview_tab, market_tab, strategy_tab, evidence_tab = st.tabs(
    ["Overview", "Market Intelligence", "Creative Strategy", "Evidence"]
)

with overview_tab:
    scores = [
        (
            "Market opportunity",
            intelligence.get("strategy", {}).get("market_opportunity_score", 0),
            intelligence.get("strategy", {}).get("market_opportunity_level", "Directional"),
        ),
        (
            "Creative quality",
            intelligence.get("creative", {}).get("overall_score", 0),
            intelligence.get("creative", {}).get("overall_level", "Directional"),
        ),
        (
            "Performance",
            intelligence.get("engagement", {}).get("overall_score", 0),
            intelligence.get("engagement", {}).get("overall_level", "Directional"),
        ),
    ]
    for column, item in zip(st.columns(3), scores):
        with column:
            html(
                '<div class="card score-card"><div class="title">{}</div>'
                '<div class="value">{}/100</div><div class="copy">{}</div></div>'.format(
                    safe(item[0]), safe(item[1]), safe(item[2])
                )
            )

    html('<div class="section-title">Executive summary</div>')
    html(
        '<div class="card"><div class="copy">{}</div></div>'.format(
            safe(report.get("executive_summary", ""))
        )
    )

    if report.get("data_quality_notes"):
        with st.expander("Data quality"):
            for note in report["data_quality_notes"]:
                st.write(note)

with market_tab:
    html(
        '<div class="notice"><strong>{}</strong><br>{}</div>'.format(
            "AI intelligence ready" if ai_available else "Fallback intelligence active",
            safe(ai_status),
        )
    )
    if ai_available:
        columns = st.columns(3)
        with columns[0]:
            render_intelligence(
                "Dominant formats",
                market_ai.get("winning_formats", []),
                "why_it_matters",
            )
        with columns[1]:
            render_intelligence(
                "Common hooks",
                market_ai.get("common_hooks", []),
                "interpretation",
            )
        with columns[2]:
            render_intelligence(
                "Product positioning",
                market_ai.get("product_positioning", []),
                "interpretation",
            )

        left, right = st.columns(2)
        with left:
            body = "".join(
                '<div class="intel-item"><div class="intel-label">{}</div>'
                '<div class="note">{}</div></div>'.format(
                    safe(item.get("pattern", "")),
                    safe(item.get("evidence", "")),
                )
                for item in market_ai.get("competitor_patterns", [])
            )
            html(
                '<div class="card split-card"><div class="title">Observed patterns</div>{}</div>'.format(
                    body or '<div class="note">No pattern returned.</div>'
                )
            )
        with right:
            body = "".join(
                '<div class="intel-item"><div class="intel-label">{}</div>'
                '<div class="note">{}</div>'
                '<div class="copy"><strong>Test:</strong> {}</div></div>'.format(
                    safe(item.get("gap", "")),
                    safe(item.get("evidence", "")),
                    safe(item.get("recommended_test", "")),
                )
                for item in market_ai.get("creative_gaps", [])
            )
            html(
                '<div class="card split-card"><div class="title">Creative whitespace</div>{}</div>'.format(
                    body or '<div class="note">No gap returned.</div>'
                )
            )
        html(
            '<div class="card"><div class="title">Strategic takeaway</div>'
            '<div class="copy">{}</div></div>'.format(
                safe(market_ai.get("strategic_takeaway", ""))
            )
        )

        html('<div class="section-title">Audience, emotion, and response signals</div>')
        audience_col, emotion_col, response_col = st.columns(3)

        with audience_col:
            render_intelligence(
                "Audience signals",
                market_ai.get("audience_signals", []),
                "interpretation",
            )

        with emotion_col:
            render_intelligence(
                "Emotional drivers",
                market_ai.get("emotional_drivers", []),
                "interpretation",
            )

        with response_col:
            render_intelligence(
                "CTA and response patterns",
                market_ai.get("response_patterns", []),
                "interpretation",
            )

        html('<div class="section-title">Market health and proof</div>')
        health_col, proof_col = st.columns(2)

        with health_col:
            market_health = market_ai.get("market_health", {})
            health_html = "".join(
                '<div class="signal-chip"><div class="signal-name">{}</div>'
                '<div class="signal-value">{}</div>'
                '<div class="note">{}</div></div>'.format(
                    safe(item.get("label", "")),
                    safe(item.get("value", "")),
                    safe(item.get("interpretation", "")),
                )
                for item in market_health.get("signals", [])
            )
            html(
                '<div class="card market-summary-card">'
                '<div class="title">Market health</div>'
                '<div class="signal-grid">{}</div>'
                '<div class="copy" style="margin-top:.8rem">{}</div>'
                '</div>'.format(
                    health_html or '<div class="note">No market-health signals returned.</div>',
                    safe(market_health.get("summary", "")),
                )
            )

        with proof_col:
            proof_items = market_ai.get("proof_patterns", [])
            proof_html = "".join(
                '<div class="intel-item"><div class="intel-label">{}</div>'
                '<div class="note">{}</div>'
                '<div class="copy"><strong>Recommendation:</strong> {}</div></div>'.format(
                    safe(item.get("pattern", "")),
                    safe(item.get("evidence", "")),
                    safe(item.get("recommendation", "")),
                )
                for item in proof_items
            )
            html(
                '<div class="card market-summary-card">'
                '<div class="title">Proof and trust signals</div>{}</div>'.format(
                    proof_html or '<div class="note">No proof patterns returned.</div>'
                )
            )

        html('<div class="section-title">Priority market actions</div>')
        priority_actions = market_ai.get("priority_actions", [])
        action_cols = st.columns(3)
        for column, item in zip(action_cols, priority_actions[:3]):
            with column:
                html(
                    '<div class="idea-card">'
                    '<div class="idea-name">{}</div>'
                    '<div class="idea-meta">{}</div>'
                    '<div class="idea-line"><strong>Why:</strong> {}</div>'
                    '<div class="idea-line"><strong>Action:</strong> {}</div>'
                    '<div class="idea-line"><strong>Metric:</strong> {}</div>'
                    '</div>'.format(
                        safe(item.get("priority", "Priority action")),
                        safe(item.get("confidence", "Directional")),
                        safe(item.get("why", "")),
                        safe(item.get("action", "")),
                        safe(item.get("success_metric", "")),
                    )
                )
    else:
        html(
            '<div class="card"><div class="copy">'
            'A valid OpenRouter key will enable LLM-generated market intelligence. '
            'Creative Strategy remains available using deterministic evidence-based fallbacks.'
            '</div></div>'
        )

with strategy_tab:
    html('<div class="section-title">Primary campaign direction</div>')
    core_fields = ["Objective", "Audience", "Insight", "Concept", "Hook", "CTA"]
    for start in range(0, len(core_fields), 2):
        columns = st.columns(2)
        for column, key in zip(columns, core_fields[start:start + 2]):
            with column:
                html(
                    '<div class="brief-card"><div class="brief-key">{}</div>'
                    '<div class="brief-value">{}</div></div>'.format(
                        safe(key),
                        safe(brief.get(key, "Not generated")),
                    )
                )

    if brief.get("Why this concept"):
        html(
            '<div class="card"><div class="title">Why this concept</div>'
            '<div class="copy">{}</div></div>'.format(
                safe(brief.get("Why this concept", ""))
            )
        )

    html('<div class="section-title">Alternative ad concepts</div>')
    concepts = brief.get("Ad concepts", [])
    for start in range(0, len(concepts), 3):
        columns = st.columns(3)
        for column, concept in zip(columns, concepts[start:start + 3]):
            with column:
                pills = "".join(
                    '<span class="pill">{}</span>'.format(safe(tag))
                    for tag in concept.get("best_for", [])
                )
                html(
                    '<div class="idea-card"><div class="idea-name">{}</div>'
                    '<div class="idea-meta">{}</div><div>{}</div>'
                    '<div class="idea-line"><strong>Hook:</strong> {}</div>'
                    '<div class="idea-line"><strong>Execution:</strong> {}</div>'
                    '<div class="idea-line"><strong>CTA:</strong> {}</div></div>'.format(
                        safe(concept.get("name", "Ad concept")),
                        safe(concept.get("angle", "")),
                        pills,
                        safe(concept.get("hook", "")),
                        safe(concept.get("execution", "")),
                        safe(concept.get("cta", "")),
                    )
                )

    html('<div class="section-title">Testing, channels, and rollout</div>')
    test_col, channel_col, rollout_col = st.columns(3)

    with test_col:
        tests = brief.get("Messaging tests", [])[:3]
        body = "".join(
            '<div class="intel-item"><div class="intel-label">{}</div>'
            '<div class="idea-line"><strong>A:</strong> {}</div>'
            '<div class="idea-line"><strong>B:</strong> {}</div>'
            '<div class="note">Success metric: {}</div></div>'.format(
                safe(item.get("variable", "Test")),
                safe(item.get("version_a", "")),
                safe(item.get("version_b", "")),
                safe(item.get("success_metric", "")),
            )
            for item in tests
        )
        html(
            '<div class="strategy-card"><div class="title">Messaging tests</div>{}</div>'.format(
                body or '<div class="note">No tests returned.</div>'
            )
        )

    with channel_col:
        channels = brief.get("Channel recommendations", [])[:3]
        body = "".join(
            '<div class="intel-item"><div class="intel-label">{}</div>'
            '<div class="note">{}</div></div>'.format(
                safe(item.get("platform", "Platform")),
                safe(item.get("recommendation", "")),
            )
            for item in channels
        )
        html(
            '<div class="strategy-card"><div class="title">Channel recommendations</div>{}</div>'.format(
                body or '<div class="note">No channel recommendations returned.</div>'
            )
        )

    with rollout_col:
        rollout = brief.get("Experiment roadmap", [])[:3]
        body = "".join(
            '<div class="intel-item"><div class="intel-label">{}</div>'
            '<div class="idea-line"><strong>Objective:</strong> {}</div>'
            '<div class="idea-line"><strong>Decision rule:</strong> {}</div></div>'.format(
                safe(item.get("phase", "Phase")),
                safe(item.get("objective", "")),
                safe(item.get("decision_rule", "")),
            )
            for item in rollout
        )
        html(
            '<div class="strategy-card"><div class="title">Experiment roadmap</div>{}</div>'.format(
                body or '<div class="note">No rollout plan returned.</div>'
            )
        )

    html('<div class="section-title">Production and optimization</div>')
    production_col, optimization_col = st.columns(2)
    with production_col:
        items = brief.get("Production checklist", [])
        html(
            '<div class="strategy-card"><div class="title">Production checklist</div>'
            '<ul class="checklist">{}</ul></div>'.format(
                "".join("<li>{}</li>".format(safe(item)) for item in items)
            )
        )
    with optimization_col:
        items = brief.get("Optimization priorities", [])
        html(
            '<div class="strategy-card"><div class="title">Optimization priorities</div>'
            '<ul class="checklist">{}</ul></div>'.format(
                "".join("<li>{}</li>".format(safe(item)) for item in items)
            )
        )

    with st.expander("Format, proof, and testing details"):
        for key in ["Format", "Proof"]:
            if brief.get(key):
                st.markdown("**{}**".format(key))
                st.write(brief[key])
        if brief.get("Testing plan"):
            st.markdown("**Testing plan**")
            for item in brief["Testing plan"]:
                st.write("• {}".format(item))

    script_tab, shot_tab = st.tabs(["Script", "Shot list"])
    with script_tab:
        st.dataframe(
            pd.DataFrame(report.get("script", [])),
            use_container_width=True,
            hide_index=True,
        )
    with shot_tab:
        st.dataframe(
            pd.DataFrame(report.get("shot_list", [])),
            use_container_width=True,
            hide_index=True,
        )

with evidence_tab:
    st.dataframe(
        pd.DataFrame(evidence_rows(report)),
        use_container_width=True,
        hide_index=True,
    )
