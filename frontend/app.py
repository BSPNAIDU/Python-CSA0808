import streamlit as st
import requests
import os
from pathlib import Path

# =====================================================
# VBCUA Streamlit Frontend
# Voice-Based Concept Understanding Analyser
# =====================================================

st.set_page_config(
    page_title="VBCUA Internship Project",
    page_icon="🎤",
    layout="wide"
)

# =====================================================
# Backend API URLs
# =====================================================

BACKEND_URL = "http://127.0.0.1:8000"

LOGIN_URL = f"{BACKEND_URL}/login"
REGISTER_URL = f"{BACKEND_URL}/register"
ANALYZE_URL = f"{BACKEND_URL}/analyze"
HISTORY_URL = f"{BACKEND_URL}/history"
REPORT_URL = f"{BACKEND_URL}/report"

# =====================================================
# Session State
# =====================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user" not in st.session_state:
    st.session_state.user = None

if "result" not in st.session_state:
    st.session_state.result = None

if "selected_page" not in st.session_state:
    st.session_state.selected_page = "🏠 Home"

# =====================================================
# CSS Styling
# =====================================================

st.markdown("""
<style>

.stApp {
    background:
        radial-gradient(circle at 10% 10%, rgba(37,99,235,.12), transparent 30%),
        radial-gradient(circle at 90% 20%, rgba(124,58,237,.12), transparent 30%),
        #0b0f17;
    color: #f8fafc;
}

.main {
    background: transparent;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1450px;
}

.hero {
    background: linear-gradient(135deg, #2563eb, #4f46e5, #7c3aed);
    padding: 35px 40px;
    border-radius: 22px;
    color: white;
    text-align: center;
    margin-bottom: 28px;
    border: 1px solid rgba(255,255,255,.15);
    box-shadow: 0 18px 45px rgba(0,0,0,.30);
}

.hero h1 {
    font-weight: 800;
    letter-spacing: -.5px;
}

.hero h4 {
    margin-top: 5px;
    opacity: .95;
}

.hero p {
    opacity: .82;
}

.vbcua-title {
    font-size: 42px;
    font-weight: 800;
    letter-spacing: 1px;
    color: #ffffff;
    margin: 0;
}

.vbcua-subtitle {
    margin-top: 8px;
    font-size: 18px;
    font-weight: 500;
    color: #dbeafe;
    letter-spacing: .3px;
}

.card {
    background: rgba(17,24,39,.88);
    padding: 22px;
    border-radius: 18px;
    border: 1px solid rgba(148,163,184,.16);
    margin-bottom: 16px;
    box-shadow: 0 12px 30px rgba(0,0,0,.20);
}

div[data-testid="stVerticalBlockBorderWrapper"] {
    border-color: rgba(148,163,184,.16) !important;
    border-radius: 18px !important;
    background: rgba(15,23,42,.45);
}

div[data-testid="stMetric"] {
    background: linear-gradient(145deg, rgba(17,24,39,.96), rgba(30,41,59,.75));
    border: 1px solid rgba(96,165,250,.18);
    border-radius: 16px;
    padding: 17px 18px;
    box-shadow: 0 10px 26px rgba(0,0,0,.18);
}

div[data-testid="stMetricLabel"] {
    color: #94a3b8 !important;
}

div[data-testid="stMetricValue"] {
    color: #f8fafc !important;
    font-weight: 800;
}

div[data-baseweb="input"] > div,
div[data-baseweb="select"] > div {
    background-color: rgba(15,23,42,.95) !important;
    border-radius: 12px !important;
    border: 1px solid rgba(148,163,184,.22) !important;
}

input {
    color: #f8fafc !important;
}

label {
    color: #e2e8f0 !important;
    font-weight: 600 !important;
}

.stButton > button,
.stDownloadButton > button {
    border-radius: 12px !important;
    min-height: 44px;
    font-weight: 700 !important;
    border: 1px solid rgba(96,165,250,.25) !important;
    background: linear-gradient(135deg, #2563eb, #4f46e5) !important;
    color: white !important;
    box-shadow: 0 8px 20px rgba(37,99,235,.20);
    transition: transform .18s ease, box-shadow .18s ease;
}

.stButton > button:hover,
.stDownloadButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 12px 28px rgba(37,99,235,.30);
}

button[data-baseweb="tab"] {
    font-weight: 700 !important;
}

button[data-baseweb="tab"][aria-selected="true"] {
    color: #60a5fa !important;
}

div[data-testid="stProgress"] > div > div {
    border-radius: 999px;
}

div[data-testid="stAlert"] {
    border-radius: 14px !important;
}

div[data-testid="stExpander"] {
    border: 1px solid rgba(148,163,184,.14) !important;
    border-radius: 15px !important;
    overflow: hidden;
}

section[data-testid="stFileUploaderDropzone"] {
    border: 1px dashed rgba(96,165,250,.35) !important;
    border-radius: 16px !important;
    background: rgba(15,23,42,.55) !important;
}

/* Microphone: styling only; st.audio_input functionality is untouched. */
div[data-testid="stAudioInput"] {
    border: 1px solid rgba(96,165,250,.22);
    border-radius: 16px;
    padding: 8px;
    background: rgba(15,23,42,.50);
}

audio {
    width: 100%;
    border-radius: 12px;
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #20212c 0%, #171923 100%);
    border-right: 1px solid rgba(148,163,184,.10);
}

section[data-testid="stSidebar"] button {
    border-radius: 11px !important;
}

div[data-testid="stJson"] {
    border-radius: 14px;
    border: 1px solid rgba(148,163,184,.12);
}

hr {
    border-color: rgba(148,163,184,.14) !important;
}

.success-box {
    background-color: #064e3b;
    color: #bbf7d0;
    padding: 16px;
    border-radius: 12px;
    margin: 12px 0;
}

.error-box {
    background-color: #7f1d1d;
    color: #fecaca;
    padding: 16px;
    border-radius: 12px;
    margin: 12px 0;
}

.small-text {
    font-size: 14px;
    color: #94a3b8;
}

.footer {
    text-align: center;
    color: #94a3b8;
    padding-top: 25px;
    padding-bottom: 10px;
}

/* Centered login/register presentation. */
.login-brand {
    text-align: center;
    margin-bottom: 22px;
}

.login-brand .icon {
    font-size: 48px;
    margin-bottom: 5px;
}

.login-brand h1 {
    margin: 0;
    font-size: 36px;
    font-weight: 800;
    color: #f8fafc;
}

.login-brand p {
    color: #94a3b8;
    margin-top: 7px;
}

@media (max-width: 900px) {
    .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
    }

    .hero {
        padding: 25px 18px;
    }

    .hero h1 {
        font-size: 26px;
    }

    .vbcua-title {
        font-size: 30px;
    }

    .vbcua-subtitle {
        font-size: 15px;
    }
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# Helper Functions
# =====================================================

def backend_post(url, data=None, files=None, timeout=120):
    try:
        response = requests.post(
            url,
            data=data,
            files=files,
            timeout=timeout
        )
        return response.status_code, response.json()

    except Exception as e:
        return 500, {
            "status": "error",
            "message": f"Backend connection error: {e}"
        }


def backend_get(url, timeout=120):
    try:
        response = requests.get(
            url,
            timeout=timeout
        )
        return response.status_code, response.json()

    except Exception as e:
        return 500, {
            "status": "error",
            "message": f"Backend connection error: {e}"
        }


def safe_score(value):
    try:
        return int(float(value))
    except Exception:
        return 0


def display_score_cards(result):

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Semantic Similarity",
            f'{result.get("similarity_score", 0)}%'
        )

    with col2:
        st.metric(
            "Fluency Score",
            f'{result.get("fluency_score", 0)}%'
        )

    with col3:
        st.metric(
            "Final Score",
            f'{result.get("final_score", 0)}%'
        )


def download_pdf_button(
    pdf_path,
    button_label="📄 Download PDF Report"
):

    if not pdf_path:
        st.warning("PDF path not available.")
        return

    path = Path(pdf_path)

    if not path.exists():
        st.warning("PDF file not found in project folder.")
        st.code(str(pdf_path))
        return

    with open(path, "rb") as pdf:

        st.download_button(
            label=button_label,
            data=pdf,
            file_name=path.name,
            mime="application/pdf",
            use_container_width=True
        )


# =====================================================
# Login and Register Screen
# =====================================================

def login_screen():

    left, center, right = st.columns([1, 1.35, 1])

    with center:

        st.markdown("""
        <div class="login-brand">
            <div class="icon">🎤</div>
            <h1>VBCUA</h1>
            <p>Voice-Based Concept Understanding Analyser</p>
        </div>
        """, unsafe_allow_html=True)

        with st.container(border=True):

            st.markdown("""
            <div style="
                text-align:center;
                margin-bottom:20px;
            ">
                <h2 style="margin-bottom:5px;">
                    Welcome Back
                </h2>
                <p style="
                    color:#94a3b8;
                    margin-top:0;
                ">
                    Sign in to continue your analysis
                </p>
            </div>
            """, unsafe_allow_html=True)

            tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])

            with tab1:

                st.subheader("Login to your account")

                email = st.text_input(
                    "Email",
                    key="login_email"
                )

                password = st.text_input(
                    "Password",
                    type="password",
                    key="login_password"
                )

                if st.button(
                    "Login",
                    use_container_width=True
                ):

                    if not email or not password:

                        st.warning(
                            "Please enter email and password."
                        )

                    else:

                        status_code, result = backend_post(
                            LOGIN_URL,
                            data={
                                "email": email,
                                "password": password
                            },
                            timeout=60
                        )

                        if result.get("status") == "success":

                            st.session_state.logged_in = True
                            st.session_state.user = result.get("user")
                            st.session_state.result = None

                            st.success("Login successful")
                            st.rerun()

                        else:

                            st.error(
                                result.get(
                                    "message",
                                    "Login failed"
                                )
                            )

            with tab2:

                st.subheader("Create new account")

                fullname = st.text_input(
                    "Full Name",
                    key="reg_fullname"
                )

                email = st.text_input(
                    "Email",
                    key="reg_email"
                )

                password = st.text_input(
                    "Password",
                    type="password",
                    key="reg_password"
                )

                confirm = st.text_input(
                    "Confirm Password",
                    type="password",
                    key="reg_confirm"
                )

                if st.button(
                    "Register",
                    use_container_width=True
                ):

                    if (
                        not fullname
                        or not email
                        or not password
                        or not confirm
                    ):

                        st.warning(
                            "Please fill all fields."
                        )

                    elif password != confirm:

                        st.error(
                            "Passwords do not match."
                        )

                    elif len(password) < 4:

                        st.error(
                            "Password should contain at least 4 characters."
                        )

                    else:

                        status_code, result = backend_post(
                            REGISTER_URL,
                            data={
                                "fullname": fullname,
                                "email": email,
                                "password": password
                            },
                            timeout=60
                        )

                        if result.get("status") == "success":

                            st.success(
                                "Registration successful. Now login."
                            )

                        else:

                            st.error(
                                result.get(
                                    "message",
                                    "Registration failed"
                                )
                            )

        st.markdown("""
        <p style="
            text-align:center;
            color:#64748b;
            font-size:13px;
            margin-top:18px;
        ">
            AI-powered spoken concept evaluation
        </p>
        """, unsafe_allow_html=True)

# =====================================================
# Sidebar
# =====================================================

def sidebar():

    st.sidebar.title(
        "🎤 VBCUA"
    )

    st.sidebar.markdown(
        "Internship Project"
    )

    user = st.session_state.user or {}

    st.sidebar.success(
        f"Logged in: {user.get('fullname', 'User')}"
    )

    page = st.sidebar.radio(
        "Navigation",
        [
            "🏠 Home",
            "📤 Upload Audio",
            "📊 Results",
            "📄 Current Report",
            "🕘 History",
            "👤 Profile"
        ],
        key="selected_page"
    )

    if st.sidebar.button(
        "Logout",
        use_container_width=True
    ):

        st.session_state.logged_in = False
        st.session_state.user = None
        st.session_state.result = None

        st.rerun()

    return page


# =====================================================
# Home Page
# =====================================================

def home_page():

    st.markdown("""
    <div class="hero">
        <div class="vbcua-title">🎤 VBCUA</div>
        <div class="vbcua-subtitle">Voice-Based Concept Understanding Analyser</div>
    </div>
    """, unsafe_allow_html=True)

    st.info("""
### 📌 Project Overview

VBCUA evaluates how effectively a user explains a concept through speech.
It converts speech into text, compares the explanation with reference concepts,
extracts audio features, calculates scores, generates feedback, and creates PDF reports.
""")

    c1, c2, c3 = st.columns(3)

    with c1:

        st.success("""
### 🎙 Speech-to-Text

OpenAI Whisper converts uploaded audio into transcript text.
""")

    with c2:

        st.info("""
### 🧠 Semantic Analysis

Sentence-BERT compares the transcript with reference concept meaning.
""")

    with c3:

        st.warning("""
### 📊 Audio Analysis

Librosa extracts speech duration, energy, pause ratio, and fluency features.
""")

    st.divider()

    m1, m2, m3, m4 = st.columns(4)

    with m1:
        st.metric(
            "AI Modules",
            "3"
        )

    with m2:
        st.metric(
            "Database",
            "SQLite"
        )

    with m3:
        st.metric(
            "Backend",
            "FastAPI"
        )

    with m4:
        st.metric(
            "Frontend",
            "Streamlit"
        )

    st.subheader(
        "✅ Completed Features"
    )

    st.success("""
- Register and Login
- SQLite user database
- Password hashing
- Audio upload
- Whisper transcription
- Sentence-BERT semantic similarity
- Librosa speech analysis
- Final score calculation
- Waveform generation
- PDF report generation
- Analysis history storage
""")


# =====================================================
# Upload Audio Page
# =====================================================

def upload_audio_page():

    st.title(
        "📤 Upload Audio for Analysis"
    )

    user = st.session_state.user or {}

    if not user.get("id"):

        st.error(
            "User ID missing. Please logout and login again."
        )

        return

    # -------------------------------------------------
    # Existing topic selection - NOT CHANGED
    # -------------------------------------------------

    topic = st.selectbox(
        "Select Concept Topic",
        [
            "Machine Learning",
            "Cloud Computing",
            "Artificial Intelligence",
            "Data Science"
        ]
    )

    # =================================================
    # NEW: MICROPHONE INPUT
    # =================================================

    st.subheader(
        "🎙️ Record Your Answer"
    )

    recorded_file = st.audio_input(
        "Click here to record your answer"
    )

    # -------------------------------------------------
    # Existing file upload - NOT CHANGED
    # -------------------------------------------------

    st.subheader(
        "📁 Or Upload an Audio File"
    )

    uploaded_file = st.file_uploader(
        "Choose an audio file",
        type=[
            "wav",
            "mp3",
            "m4a"
        ]
    )

    # =================================================
    # SELECT AUDIO SOURCE
    # =================================================

    selected_file = None
    selected_filename = None
    selected_mime_type = None

    # Microphone has priority if recorded
    if recorded_file is not None:

        selected_file = recorded_file

        selected_filename = (
            "microphone_recording.wav"
        )

        selected_mime_type = (
            "audio/wav"
        )

        st.success(
            "✅ Microphone recording received successfully"
        )

        st.audio(
            recorded_file
        )

    # Otherwise use uploaded file
    elif uploaded_file is not None:

        selected_file = uploaded_file

        selected_filename = uploaded_file.name

        selected_mime_type = uploaded_file.type

        st.success(
            "✅ Audio uploaded successfully"
        )

        st.audio(
            uploaded_file
        )

    # =================================================
    # START ANALYSIS
    # =================================================

    if selected_file is not None:

        if st.button(
            "🚀 Start Analysis",
            use_container_width=True
        ):

            with st.spinner(
                "Analyzing audio using AI models... Please wait..."
            ):

                # -----------------------------------------
                # Prepare audio file
                # -----------------------------------------

                files = {
                    "file": (
                        selected_filename,
                        selected_file.getvalue(),
                        selected_mime_type
                    )
                }

                # -----------------------------------------
                # Existing backend data - NOT CHANGED
                # -----------------------------------------

                data = {
                    "topic": topic,
                    "user_id": user["id"]
                }

                # -----------------------------------------
                # Send to existing FastAPI backend
                # -----------------------------------------

                status_code, result = backend_post(
                    ANALYZE_URL,
                    data=data,
                    files=files,
                    timeout=300
                )

                # -----------------------------------------
                # Backend error
                # -----------------------------------------

                if status_code != 200:

                    st.error(
                        "Backend Error"
                    )

                    st.write(
                        result
                    )

                    return

                if result.get("status") == "error":

                    st.error(
                        result.get(
                            "message",
                            "Backend returned an error."
                        )
                    )

                    return

                # -----------------------------------------
                # Save result
                # -----------------------------------------

                st.session_state.result = result

                st.success(
                    "✅ Analysis completed successfully"
                )

                # -----------------------------------------
                # Existing transcript display
                # -----------------------------------------

                st.subheader(
                    "📝 Transcript"
                )

                st.write(
                    result.get(
                        "transcript",
                        ""
                    )
                )

                # -----------------------------------------
                # Existing score cards
                # -----------------------------------------

                display_score_cards(
                    result
                )

                # -----------------------------------------
                # Existing understanding level
                # -----------------------------------------

                st.subheader(
                    "🧠 Understanding Level"
                )

                st.success(
                    result.get(
                        "understanding_level",
                        "Not Available"
                    )
                )

                # -----------------------------------------
                # Existing feedback
                # -----------------------------------------

                st.subheader(
                    "💡 Feedback"
                )

                st.info(
                    result.get(
                        "feedback",
                        "No feedback available."
                    )
                )

                st.info(
                    "Result saved into SQLite history automatically."
                )


# =====================================================
# Results Page
# =====================================================

def results_page():

    st.title(
        "📊 Analysis Results"
    )

    if not st.session_state.result:

        st.warning(
            "Please upload an audio file and analyze first."
        )

        return

    result = st.session_state.result

    st.subheader(
        "📚 Selected Topic"
    )

    st.write(
        result.get(
            "topic",
            "Not Available"
        )
    )

    st.subheader(
        "📝 Transcript"
    )

    st.write(
        result.get(
            "transcript",
            "No transcript available."
        )
    )

    st.subheader(
        "📖 Reference Concept"
    )

    st.write(
        result.get(
            "reference",
            "No reference available."
        )
    )

    st.divider()

    display_score_cards(
        result
    )

    st.divider()

    st.subheader(
        "📈 Overall Performance"
    )

    sim = safe_score(
        result.get(
            "similarity_score",
            0
        )
    )

    flu = safe_score(
        result.get(
            "fluency_score",
            0
        )
    )

    final = safe_score(
        result.get(
            "final_score",
            0
        )
    )

    st.write(
        "Semantic Similarity"
    )

    st.progress(
        min(sim, 100)
    )

    st.write(
        "Fluency Score"
    )

    st.progress(
        min(flu, 100)
    )

    st.write(
        "Final Score"
    )

    st.progress(
        min(final, 100)
    )

    st.divider()

    st.subheader(
        "🎵 Audio Features"
    )

    st.json(
        result.get(
            "audio_features",
            {}
        )
    )

    st.divider()

    st.subheader(
        "🌊 Audio Waveform"
    )

    waveform_path = result.get(
        "waveform"
    )

    if waveform_path and os.path.exists(
        waveform_path
    ):

        st.image(
            waveform_path,
            caption="Uploaded Audio Waveform",
            use_container_width=True
        )

    else:

        st.warning(
            "Waveform not available."
        )

    st.divider()

    st.subheader(
        "💡 AI Feedback"
    )

    st.info(
        result.get(
            "feedback",
            "No feedback available."
        )
    )


# =====================================================
# Current Report Page
# =====================================================

def current_report_page():

    st.title(
        "📄 Current Analysis Report"
    )

    if not st.session_state.result:

        st.warning(
            "No report generated yet. Please analyze audio first."
        )

        return

    result = st.session_state.result

    st.success(
        "✅ Report generated successfully"
    )

    st.subheader(
        "📝 Transcript"
    )

    st.write(
        result.get(
            "transcript",
            "No transcript available."
        )
    )

    st.subheader(
        "📊 Scores"
    )

    similarity = safe_score(
        result.get(
            "similarity_score",
            0
        )
    )

    fluency = safe_score(
        result.get(
            "fluency_score",
            0
        )
    )

    final_score = safe_score(
        result.get(
            "final_score",
            0
        )
    )

    st.write(
        f'Semantic Similarity: '
        f'{result.get("similarity_score", 0)}%'
    )

    st.progress(
        min(similarity, 100)
    )

    st.write(
        f'Fluency Score: '
        f'{result.get("fluency_score", 0)}%'
    )

    st.progress(
        min(fluency, 100)
    )

    st.write(
        f'Final Score: '
        f'{result.get("final_score", 0)}%'
    )

    st.progress(
        min(final_score, 100)
    )

    st.subheader(
        "💡 Feedback"
    )

    st.info(
        result.get(
            "feedback",
            "No feedback available."
        )
    )

    st.subheader(
        "📥 Download Report"
    )

    download_pdf_button(
        result.get(
            "pdf_path"
        )
    )


# =====================================================
# History Page
# =====================================================

def history_page():

    st.title(
        "🕘 My Analysis History"
    )

    user = st.session_state.user or {}

    if not user.get("id"):

        st.error(
            "User ID missing. Please logout and login again."
        )

        return

    status_code, result = backend_get(
        f"{HISTORY_URL}/{user['id']}",
        timeout=120
    )

    if (
        status_code != 200
        or result.get("status") != "success"
    ):

        st.error(
            result.get(
                "message",
                "Unable to fetch history."
            )
        )

        return

    history = result.get(
        "history",
        []
    )

    if not history:

        st.warning(
            "No previous analysis reports found."
        )

        return

    st.success(
        f"Total Reports Found: {len(history)}"
    )

    for item in history:

        with st.expander(
            f"Report #{item.get('id')} | "
            f"{item.get('topic')} | "
            f"{item.get('created_at')}"
        ):

            c1, c2, c3 = st.columns(3)

            with c1:

                st.metric(
                    "Semantic Score",
                    f"{item.get('semantic_score', 0)}%"
                )

            with c2:

                st.metric(
                    "Fluency Score",
                    f"{item.get('fluency_score', 0)}%"
                )

            with c3:

                st.metric(
                    "Overall Score",
                    f"{item.get('overall_score', 0)}%"
                )

            st.subheader(
                "📝 Transcription"
            )

            st.write(
                item.get(
                    "transcription",
                    ""
                )
            )

            st.subheader(
                "💡 Feedback"
            )

            st.info(
                item.get(
                    "feedback",
                    "No feedback available."
                )
            )

            pdf_path = item.get(
                "pdf_path"
            )

            if pdf_path:

                download_pdf_button(
                    pdf_path,
                    button_label=(
                        f"📄 Download Report "
                        f"#{item.get('id')}"
                    )
                )


# =====================================================
# Profile Page
# =====================================================

def profile_page():

    st.title(
        "👤 Profile"
    )

    user = st.session_state.user or {}

    st.info(f"""
### User Details

**Name:** {user.get("fullname", "User")}  
**Email:** {user.get("email", "Not Available")}  
**User ID:** {user.get("id", "Not Available")}

### Internship Project Details

**Project Name:** Voice-Based Concept Understanding Analyser (VBCUA)  
**Project Type:** Internship Project  
**Purpose:** To evaluate spoken conceptual explanations using speech-to-text, semantic similarity, audio feature extraction, scoring, and report generation.
""")

    c1, c2, c3 = st.columns(3)

    with c1:

        st.success("""
### Frontend

Python  
Streamlit  
HTML/CSS Styling
""")

    with c2:

        st.info("""
### AI Modules

Whisper  
Sentence-BERT  
Librosa
""")

    with c3:

        st.warning("""
### Backend

FastAPI  
SQLite  
ReportLab
""")

    st.progress(
        100
    )

    st.success("""
✅ Register/Login  
✅ SQLite Database  
✅ Streamlit Frontend  
✅ FastAPI Backend  
✅ Audio Upload  
✅ Whisper Speech-to-Text  
✅ Sentence-BERT Similarity  
✅ Librosa Audio Features  
✅ Intelligent Scoring  
✅ PDF Report Download  
✅ Analysis History
""")


# =====================================================
# Main App Controller
# =====================================================

def main():

    if not st.session_state.logged_in:

        login_screen()

        st.stop()

    page = sidebar()

    if page == "🏠 Home":

        home_page()

    elif page == "📤 Upload Audio":

        upload_audio_page()

    elif page == "📊 Results":

        results_page()

    elif page == "📄 Current Report":

        current_report_page()

    elif page == "🕘 History":

        history_page()

    elif page == "👤 Profile":

        profile_page()

    st.markdown(
        "---"
    )

    st.markdown(
        '<div class="footer">'
        '© 2026 VBCUA Internship Project | '
        'Streamlit + FastAPI + SQLite'
        '</div>',
        unsafe_allow_html=True
    )


main()