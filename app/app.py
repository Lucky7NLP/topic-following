# app.py
# Run with:  streamlit run app.py
# Dependencies: pip install streamlit pandas

import os
import json
import time
import random
from typing import List, Dict, Optional

import pandas as pd
import streamlit as st

from utils import normalize_headers, parse_conversation_any, ensure_data_dir, safe_append_row


# -------------------------
# App config
# -------------------------
st.set_page_config(page_title="Distractor Builder", layout="wide")
DATA_DIR = "data/distractors"  # where domain.csv files will be saved
REQUIRED_CORE = ["domain", "scenario", "system_instruction", "conversation"]


# -------------------------
# Helpers
# -------------------------
def validate_columns(df: pd.DataFrame) -> Optional[str]:
    missing = [c for c in REQUIRED_CORE if c not in df.columns]
    if missing:
        return f"Missing required columns: {', '.join(missing)}"
    return None


def select_random_index(df: pd.DataFrame) -> int:
    # pick a random valid row index
    return int(df.sample(1, random_state=random.randint(0, 10_000)).index[0])


def render_conversation(conv_value):
    """
    Renders a conversation in Streamlit.
    Accepts: list[dict] with {'role', 'content'}.
    If parsing fails, prints raw text.
    """
    conv = parse_conversation_any(conv_value)
    if isinstance(conv, list) and all(isinstance(x, dict) and "role" in x and "content" in x for x in conv):
        for turn in conv:
            role = str(turn.get("role", "user")).lower()
            role = "assistant" if role == "assistant" else "user"  # only allow user/assistant for st.chat_message
            with st.chat_message(role):
                st.write(turn.get("content", ""))
    else:
        st.info("Conversation (raw):")
        st.code(str(conv_value), language="json")


def save_distractor_row(domain: str, src_row: dict, distractor_text: str):
    """
    Saves one row to data/distractors/<domain>.csv, creating headers if needed.
    """
    ensure_data_dir(DATA_DIR)
    out_path = os.path.join(DATA_DIR, f"{domain}.csv")

    record = {
        "timestamp": pd.Timestamp.utcnow().isoformat(),
        "domain": src_row.get("domain", ""),
        "scenario": src_row.get("scenario", ""),
        "system_instruction": src_row.get("system_instruction", ""),
        "conversation_json": json.dumps(parse_conversation_any(src_row.get("conversation", "")), ensure_ascii=False),
        "distractor": distractor_text.strip(),
    }
    safe_append_row(out_path, record,
                    header_columns=["timestamp", "domain", "scenario", "system_instruction", "conversation_json", "distractor"])


# -------------------------
# Session state
# -------------------------
if "dataset_df" not in st.session_state:
    st.session_state.dataset_df = None
if "current_idx" not in st.session_state:
    st.session_state.current_idx = None
if "last_saved" not in st.session_state:
    st.session_state.last_saved = None


# -------------------------
# Sidebar: CSV loader
# -------------------------
st.sidebar.title("Dataset")
uploaded = st.sidebar.file_uploader("Upload CSV with columns: domain, scenario, system_instruction, conversation",
                                    type=["csv"])

if uploaded is not None:
    try:
        df = pd.read_csv(uploaded)
        df = normalize_headers(df)
        err = validate_columns(df)
        if err:
            st.sidebar.error(err)
        else:
            st.session_state.dataset_df = df
            st.sidebar.success(f"Loaded {len(df):,} rows.")
    except Exception as e:
        st.sidebar.error(f"Failed to read CSV: {e}")

# For convenience: show a small preview
if st.session_state.dataset_df is not None:
    with st.sidebar.expander("Preview (first 6 rows)"):
        st.dataframe(st.session_state.dataset_df.head(6), use_container_width=True)


# -------------------------
# Main UI
# -------------------------
st.title("Distractor Builder (Streamlit)")

if st.session_state.dataset_df is None:
    st.info("Upload a CSV to get started.")
    st.stop()

col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    if st.button("🎲 Generate Random Scenario", use_container_width=True):
        st.session_state.current_idx = select_random_index(st.session_state.dataset_df)
        st.session_state.last_saved = None

with col2:
    seed = st.number_input("Optional random seed", min_value=0, value=0, step=1, help="If non-zero, influences the next random pick.")
    if seed:
        random.seed(int(seed))

with col3:
    st.write("")  # spacer
    st.write("")  # spacer
    st.caption("Tip: Click the dice again to get another example.")

if st.session_state.current_idx is None:
    st.warning("Click **Generate Random Scenario** to begin.")
    st.stop()

row = st.session_state.dataset_df.loc[st.session_state.current_idx]
domain = str(row.get("domain", "")).strip() or "unknown"

# Show scenario + system instruction
st.subheader(f"Domain: `{domain}`")
with st.expander("Scenario", expanded=True):
    st.write(row.get("scenario", ""))

with st.expander("System Instruction", expanded=False):
    st.code(str(row.get("system_instruction", "")), language="markdown")

st.markdown("### Conversation")
render_conversation(row.get("conversation", ""))

# Distractor input
st.markdown("---")
st.markdown("### Add your distractor")
distractor_text = st.text_area(
    "Write a short distractor that subtly deviates from the system instructions but stays close enough to test topic adherence.",
    height=180,
    placeholder="Type the distractor here..."
)

save_col1, save_col2 = st.columns([1, 2])
with save_col1:
    can_save = bool(distractor_text.strip())
    if st.button("💾 Save Distractor", type="primary", use_container_width=True, disabled=not can_save):
        try:
            save_distractor_row(domain, row.to_dict(), distractor_text)
            st.session_state.last_saved = time.time()
            st.success(f"Saved to `{os.path.join(DATA_DIR, f'{domain}.csv')}`")
        except Exception as e:
            st.error(f"Failed to save: {e}")

with save_col2:
    if st.session_state.last_saved:
        st.caption("Last save just now ✅")


# Footer hint
st.markdown("---")
st.caption("Files are saved per domain in the `data/` folder (created automatically).")
