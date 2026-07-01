"""
app.py
DisasterAid AI — Streamlit frontend.
Offline-first, CPU-only multi-modal disaster report ingestion.
"""

import os

import pandas as pd
import streamlit as st

from database import (
    get_all_incidents,
    get_incident_by_id,
    init_db,
    insert_incident,
    insert_report,
    search_incidents,
)
from utils.extractor import extract_structured_data
from utils.ocr import extract_text_from_image, extract_text_from_video
from utils.parser import clean_text, extract_text_from_pdf
from utils.speech import transcribe_audio

st.set_page_config(page_title="DisasterAid AI", page_icon="🌍", layout="wide")
init_db()

SEVERITY_COLORS = {
    "Critical": "#ff4b4b",
    "High": "#ff9800",
    "Medium": "#ffd600",
    "Low": "#4caf50",
}

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def process_input(source_type: str, file_path: str | None, text_input: str | None) -> dict:
    """Route input to the correct extraction pipeline and return structured data."""
    if source_type == "image":
        raw_text = extract_text_from_image(file_path)
    elif source_type == "video":
        raw_text = extract_text_from_video(file_path)
    elif source_type == "audio":
        raw_text = transcribe_audio(file_path)
    elif source_type == "pdf":
        raw_text = extract_text_from_pdf(file_path)
    elif source_type == "text":
        raw_text = clean_text(text_input or "")
    else:
        raw_text = ""

    structured = extract_structured_data(raw_text)
    incident_id = insert_incident(structured)
    insert_report(incident_id, source_type, file_path or "direct_text", raw_text)
    return {**structured, "incident_id": incident_id}


# --- Sidebar navigation ---
page = st.sidebar.radio(
    "Navigate", ["🏠 Home", "📊 Dashboard", "🔍 Search", "⬇️ Export"]
)

st.sidebar.markdown("---")
st.sidebar.caption("🌍 DisasterAid AI — fully offline, CPU-only")

# --- Home: Upload ---
if page == "🏠 Home":
    st.title("🌍 DisasterAid AI")
    st.caption("Upload a disaster report — image, audio, video, PDF, or text.")

    input_type = st.selectbox(
        "Input type", ["Text", "Image", "Audio", "Video", "PDF"]
    )

    if input_type == "Text":
        text_input = st.text_area("Disaster report text", height=150)
        if st.button("Process Report", type="primary"):
            if text_input.strip():
                with st.spinner("Extracting structured data..."):
                    result = process_input("text", None, text_input)
                st.success(f"Incident #{result['incident_id']} saved.")
                st.json(result)
            else:
                st.warning("Please enter some text first.")
    else:
        type_map = {
            "Image": ("image", ["jpg", "jpeg", "png", "webp"]),
            "Audio": ("audio", ["wav", "mp3", "ogg"]),
            "Video": ("video", ["mp4", "avi"]),
            "PDF": ("pdf", ["pdf"]),
        }
        source_type, extensions = type_map[input_type]
        uploaded_file = st.file_uploader(f"Upload {input_type}", type=extensions)

        if uploaded_file and st.button("Process Report", type="primary"):
            file_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            with st.spinner(f"Processing {input_type.lower()} locally (CPU)..."):
                result = process_input(source_type, file_path, None)

            st.success(f"Incident #{result['incident_id']} saved.")
            st.json(result)

# --- Dashboard ---
elif page == "📊 Dashboard":
    st.title("📊 Incident Dashboard")
    incidents = get_all_incidents()

    if not incidents:
        st.info("No incidents recorded yet. Upload a report on the Home page.")
    else:
        cols = st.columns(3)
        for idx, incident in enumerate(incidents):
            color = SEVERITY_COLORS.get(incident.get("severity"), "#9e9e9e")
            with cols[idx % 3]:
                st.markdown(
                    f"""
                    <div style="border-left: 6px solid {color}; padding: 10px;
                                margin-bottom: 10px; background-color: #f9f9f9;
                                border-radius: 4px; color: #111111;">
                        <b>#{incident['id']} — {incident.get('disaster_type', 'Unknown')}</b><br>
                        Severity: <b>{incident.get('severity', 'N/A')}</b><br>
                        Location: {incident.get('location', 'N/A')}<br>
                        Trapped: {incident.get('people_trapped', 0)}<br>
                        Priority: {incident.get('priority_score', 0)}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

# --- Search ---
elif page == "🔍 Search":
    st.title("🔍 Search Incidents")
    keyword = st.text_input("Search by disaster type or location")
    if keyword:
        results = search_incidents(keyword)
        st.write(f"Found {len(results)} result(s)")
        for r in results:
            st.json(r)

# --- Export ---
elif page == "⬇️ Export":
    st.title("⬇️ Export Data")
    incidents = get_all_incidents()

    if not incidents:
        st.info("No data to export yet.")
    else:
        df = pd.DataFrame(incidents)
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                "Download CSV",
                df.to_csv(index=False),
                file_name="incidents.csv",
                mime="text/csv",
            )
        with col2:
            st.download_button(
                "Download JSON",
                df.to_json(orient="records", indent=2),
                file_name="incidents.json",
                mime="application/json",
            )
        st.dataframe(df)
