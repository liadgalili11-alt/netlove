"""
Netlove – entry point for Streamlit Cloud.
Streamlit Cloud looks for streamlit_app.py in the repo root by default.
"""

import sys
import os

# Allow imports from project root
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
from frontend.pages import upload, content_editor, publisher
from frontend import api_client

st.set_page_config(
    page_title="Netlove – AI Content Studio",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS (Netflix-inspired dark theme) ──────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #141414; color: #e5e5e5; }
    .stButton > button[kind="primary"] {
        background-color: #E50914 !important; color: white !important;
        border: none !important; font-weight: 700 !important;
        border-radius: 4px !important; font-size: 1rem !important;
        padding: 0.6rem 1.2rem !important;
    }
    .stExpander { background-color: #1f1f1f !important; border: 1px solid #333 !important; border-radius: 8px !important; }
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background-color: #2a2a2a !important; color: #e5e5e5 !important;
        border: 1px solid #444 !important; border-radius: 4px !important;
    }
    hr { border-color: #333 !important; }
    .stFileUploader { background-color: #1f1f1f !important; border: 2px dashed #E50914 !important; border-radius: 8px !important; padding: 1rem !important; }
    .stSuccess { background-color: #1a3a1a !important; }
    .stError   { background-color: #3a1a1a !important; }
</style>
""", unsafe_allow_html=True)

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; padding: 1.5rem 0 0.5rem;">
    <h1 style="color:#E50914; font-size:3rem; font-weight:900; letter-spacing:-1px; margin:0;">
        🎬 NETLOVE
    </h1>
    <p style="color:#aaa; font-size:1.1rem; margin-top:0.3rem;">
        AI Content Studio – מסגרות בעיצוב אישי | יצירת תוכן אוטומטי לרשתות חברתיות
    </p>
</div>
""", unsafe_allow_html=True)

# Backend health check
if not api_client.check_health():
    st.error("⚠️ השרת אינו פעיל כרגע, אנא המתן מספר שניות ורענן את הדף.")
    st.stop()

st.markdown("---")

# ── Workflow ───────────────────────────────────────────────────────────────────
col_left, col_center, col_right = st.columns([1.2, 1.4, 1.4], gap="large")

with col_left:
    upload.render()

with col_center:
    content_editor.render()

with col_right:
    publisher.render()

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<p style='text-align:center; color:#555; font-size:0.8rem;'>"
    "Netlove AI Content Studio © 2024 | Powered by GPT-4o + Meta Graph API"
    "</p>",
    unsafe_allow_html=True,
)
