import streamlit as st
import os
import json
import pandas as pd
import tempfile
from utils import db, parser, ocr, speech, video

# Initialize database
db.init_db()

# Page configuration
st.set_page_config(
    page_title="DisasterAid AI",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for high-quality dark-themed layout
st.markdown(
    """
<style>
    .main-title {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(90deg, #ff4b4b, #ff7676);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.1rem;
    }
    .sub-title {
        font-size: 1.15rem;
        color: #aaaaaa;
        margin-bottom: 2rem;
    }
    .card-style {
        border-radius: 12px;
        padding: 20px;
        background-color: #1e1e1e;
        border: 1px solid #333333;
        margin-bottom: 20px;
    }
    .banner-style {
        padding: 10px 15px;
        background-color: #3b2222;
        color: #ff8888;
        border-left: 5px solid #ff4b4b;
        border-radius: 4px;
        margin-bottom: 20px;
        font-weight: 500;
    }
</style>
""",
    unsafe_allow_html=True,
)

# Languages configuration
LANGUAGES = {"en": "English", "hi": "हिन्दी", "ta": "தமிழ்", "te": "తెలుగు"}


def load_translations(lang):
    path = os.path.join("static", "i18n", f"{lang}.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        # Fallback to defaults
        return {
            "nav.home": "Home",
            "nav.dashboard": "Dashboard",
            "title": "Offline Disaster Intelligence",
            "subtitle": "Upload an image, video, audio recording, PDF, or type a report. Everything is processed locally.",
            "text.heading": "Text Report",
            "text.placeholder": "Describe the situation...",
            "text.button": "Analyze Text",
            "file.heading": "Image / Audio / Video / PDF",
            "file.button": "Analyze File",
            "result.heading": "Structured Result",
            "result.mockBanner": "Demo mode: install OCR/Whisper locally for live model output (see README).",
            "loading": "Processing locally...",
            "dash.heading": "Rescue Dashboard",
            "dash.exportJson": "Export JSON",
            "dash.exportCsv": "Export CSV",
            "table.id": "ID",
            "table.type": "Type",
            "table.severity": "Severity",
            "table.trapped": "Trapped",
            "table.location": "Location",
            "table.priority": "Priority",
            "table.status": "Status",
            "table.actions": "Actions",
        }


# Sidebar - Language and Navigation
st.sidebar.markdown("### 🌍 Language / भाषा")
lang_code = st.sidebar.selectbox(
    "Select Language",
    options=list(LANGUAGES.keys()),
    format_func=lambda x: LANGUAGES[x],
    label_visibility="collapsed",
)
t = load_translations(lang_code)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🧭 Navigation")
nav_choice = st.sidebar.radio(
    "Go to",
    [t.get("nav.home", "Home"), t.get("nav.dashboard", "Dashboard")],
    label_visibility="collapsed",
)


def _extract_pdf_text(pdf_path):
    """Lightweight offline PDF text extraction using pypdf, with mock fallback."""
    try:
        from pypdf import PdfReader

        reader = PdfReader(pdf_path)
        text = "\n".join((page.extract_text() or "") for page in reader.pages)
        if text.strip():
            return {"text": text, "engine": "pypdf", "mock": False}
    except Exception:
        pass
    return {
        "text": "Government relief notice: Camp established for flood-affected "
        "families. Approximately 80 people sheltered, food and clean "
        "water urgently required.",
        "engine": "mock",
        "mock": True,
    }


if nav_choice == t.get("nav.home", "Home"):
    # Main Header
    st.markdown(
        f'<div class="main-title">{t.get("title")}</div>', unsafe_allow_html=True
    )
    st.markdown(
        f'<div class="sub-title">{t.get("subtitle")}</div>', unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f'### 📝 {t.get("text.heading")}')
        text_input = st.text_area(
            "Report Description",
            placeholder=t.get("text.placeholder"),
            height=200,
            label_visibility="collapsed",
        )
        submit_text = st.button(
            t.get("text.button"), type="primary", use_container_width=True
        )

        if submit_text:
            if not text_input.strip():
                st.error("Please enter some text description.")
            else:
                with st.spinner(t.get("loading")):
                    # Parse and save
                    record = parser.parse_text(text_input)
                    record["extraction_engine"] = "raw_text"
                    record["mock_mode"] = False
                    record["extracted_text"] = text_input

                    incident_id = db.save_incident(
                        record, source_type="text", raw_text=text_input
                    )
                    record["incident_id"] = incident_id

                    st.success("Successfully analyzed and saved text report!")
                    st.markdown(f'### 📊 {t.get("result.heading")}')
                    st.json(record)

    with col2:
        st.markdown(f'### 📁 {t.get("file.heading")}')
        uploaded_file = st.file_uploader(
            "Upload file",
            type=[
                "png",
                "jpg",
                "jpeg",
                "bmp",
                "webp",
                "wav",
                "mp3",
                "m4a",
                "ogg",
                "flac",
                "mp4",
                "mov",
                "avi",
                "mkv",
                "pdf",
            ],
            label_visibility="collapsed",
        )
        submit_file = st.button(
            t.get("file.button"), type="primary", use_container_width=True
        )

        if submit_file:
            if uploaded_file is None:
                st.error("Please select a file to upload first.")
            else:
                with st.spinner(t.get("loading")):
                    # Save uploaded file to a temporary location
                    suffix = os.path.splitext(uploaded_file.name)[1]
                    with tempfile.NamedTemporaryFile(
                        suffix=suffix, delete=False
                    ) as temp_f:
                        temp_f.write(uploaded_file.read())
                        temp_path = temp_f.name

                    # Detect category based on suffix
                    ext = suffix.lower().strip(".")
                    category = "none"
                    if ext in ["png", "jpg", "jpeg", "bmp", "webp"]:
                        category = "image"
                    elif ext in ["wav", "mp3", "m4a", "ogg", "flac"]:
                        category = "audio"
                    elif ext in ["mp4", "mov", "avi", "mkv"]:
                        category = "video"
                    elif ext == "pdf":
                        category = "document"

                    try:
                        if category == "image":
                            res = ocr.extract_text_from_image(temp_path)
                        elif category == "audio":
                            res = speech.transcribe_audio(temp_path)
                        elif category == "video":
                            res = video.process_video(temp_path)
                        elif category == "document":
                            res = _extract_pdf_text(temp_path)
                        else:
                            res = {"text": "", "engine": "none", "mock": False}

                        extracted_text = res["text"]
                        record = parser.parse_text(extracted_text)
                        record["extraction_engine"] = res["engine"]
                        record["mock_mode"] = res["mock"]
                        record["extracted_text"] = extracted_text

                        incident_id = db.save_incident(
                            record,
                            source_type=category,
                            source_file=uploaded_file.name,
                            raw_text=extracted_text,
                        )
                        record["incident_id"] = incident_id

                        st.success(f"Successfully processed {category} file!")

                        if res["mock"]:
                            st.markdown(
                                f'<div class="banner-style">⚠️ {t.get("result.mockBanner")}</div>',
                                unsafe_allow_html=True,
                            )

                        st.markdown(f'### 📊 {t.get("result.heading")}')
                        st.json(record)

                    except Exception as e:
                        st.error(f"Error processing file: {e}")
                    finally:
                        if os.path.exists(temp_path):
                            os.remove(temp_path)

else:
    # Dashboard View
    st.markdown(
        f'<div class="main-title">{t.get("dash.heading", "Rescue Dashboard")}</div>',
        unsafe_allow_html=True,
    )
    st.markdown("---")

    incidents = db.get_all_incidents()

    if not incidents:
        st.info(
            "No incident reports found in the database. Go back to Home to submit a report."
        )
    else:
        # Metrics Row
        total_reports = len(incidents)
        total_trapped = sum(r.get("people_trapped", 0) for r in incidents)
        critical_count = sum(1 for r in incidents if r.get("severity") == "Critical")

        m_col1, m_col2, m_col3 = st.columns(3)
        m_col1.metric("🚨 Total Incidents", total_reports)
        m_col2.metric("👥 Total People Trapped", total_trapped)
        m_col3.metric("🔴 Critical Cases", critical_count)

        st.markdown("### 📋 Incident Records")

        # Format list to Pandas DataFrame
        df = pd.DataFrame(incidents)

        # Keep clean view columns
        cols_to_show = [
            "incident_id",
            "source_type",
            "disaster_type",
            "severity",
            "people_trapped",
            "location",
            "priority_score",
            "status",
            "created_at",
        ]
        df_clean = df[cols_to_show].copy()

        # Rename columns to match translations
        df_clean.columns = [
            t.get("table.id", "ID"),
            t.get("table.type", "Type"),
            "Disaster",
            t.get("table.severity", "Severity"),
            t.get("table.trapped", "Trapped"),
            t.get("table.location", "Location"),
            t.get("table.priority", "Priority"),
            t.get("table.status", "Status"),
            "Timestamp",
        ]

        st.dataframe(df_clean, use_container_width=True)

        # Actions & Exports Row
        st.markdown("### ⚙️ Actions & Exports")

        exp_col1, exp_col2, del_col = st.columns([1, 1, 2])

        with exp_col1:
            # Export JSON
            json_str = json.dumps(incidents, indent=2)
            st.download_button(
                label=f"📥 {t.get('dash.exportJson', 'Export JSON')}",
                data=json_str,
                file_name="incidents_export.json",
                mime="application/json",
                use_container_width=True,
            )

        with exp_col2:
            # Export CSV
            csv_data = df.to_csv(index=False)
            st.download_button(
                label=f"📥 {t.get('dash.exportCsv', 'Export CSV')}",
                data=csv_data,
                file_name="incidents_export.csv",
                mime="text/csv",
                use_container_width=True,
            )

        with del_col:
            # Delete selection
            del_id = st.selectbox(
                "Delete Incident ID",
                options=[r["incident_id"] for r in incidents],
                format_func=lambda x: f"Incident ID: {x}",
            )
            if st.button(
                "🗑️ Delete Selected Incident",
                type="secondary",
                use_container_width=True,
            ):
                db.delete_incident(del_id)
                st.success(f"Deleted Incident ID {del_id} successfully.")
                st.rerun()
