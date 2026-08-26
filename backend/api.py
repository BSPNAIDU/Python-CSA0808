from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os

from backend.whisper_module import transcribe_audio
from backend.semantic_module import calculate_similarity
from backend.audio_analysis import analyze_audio as extract_audio_features
from backend.scoring import calculate_final_score
from backend.report_generator import generate_pdf
from backend.waveform import generate_waveform

from backend.database import (
    register_user,
    login_user,
    save_analysis,
    get_user_history,
    get_analysis
)


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="Voice-Based Concept Understanding Analyser API"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# DIRECTORIES
# ============================================================

UPLOAD_DIR = "uploads"
REPORT_DIR = "reports"

os.makedirs(
    UPLOAD_DIR,
    exist_ok=True
)

os.makedirs(
    REPORT_DIR,
    exist_ok=True
)


# ============================================================
# HOME
# ============================================================

@app.get("/")
def home():

    return {
        "status": "running",
        "project": (
            "Voice-Based Concept "
            "Understanding Analyser"
        ),
        "type": "Internship Project",
        "version": "2.0"
    }


# ============================================================
# REGISTER
# ============================================================

@app.post("/register")
def register(
    fullname: str = Form(...),
    email: str = Form(...),
    password: str = Form(...)
):

    return register_user(
        fullname,
        email,
        password
    )


# ============================================================
# LOGIN
# ============================================================

@app.post("/login")
def login(
    email: str = Form(...),
    password: str = Form(...)
):

    return login_user(
        email,
        password
    )


# ============================================================
# ANALYZE AUDIO
# ============================================================

@app.post("/analyze")
async def analyze_audio_api(

    file: UploadFile = File(...),

    topic: str = Form(...),

    user_id: int = Form(...)
):

    try:

        # ----------------------------------------------------
        # STEP 1: SAVE UPLOADED AUDIO
        # ----------------------------------------------------

        safe_filename = os.path.basename(
            file.filename
        )

        file_path = os.path.join(
            UPLOAD_DIR,
            safe_filename
        )

        with open(
            file_path,
            "wb"
        ) as buffer:

            shutil.copyfileobj(
                file.file,
                buffer
            )


        # ----------------------------------------------------
        # STEP 2: SPEECH TO TEXT
        # ----------------------------------------------------

        transcript = transcribe_audio(
            file_path
        )


        # ----------------------------------------------------
        # STEP 3: AI + SEMANTIC EVALUATION
        #
        # calculate_similarity() now:
        #
        # 1. Sends topic + transcript to Gemini
        # 2. Gets the correct conceptual answer
        # 3. Evaluates the student's answer
        # 4. Uses Sentence-BERT for semantic similarity
        # 5. Returns the combined semantic score
        # ----------------------------------------------------

        semantic_result = calculate_similarity(
            transcript,
            topic
        )


        # ----------------------------------------------------
        # STEP 4: AUDIO ANALYSIS
        #
        # Existing Librosa/audio analysis is kept.
        # ----------------------------------------------------

        audio_features = extract_audio_features(
            file_path,
            transcript
        )


        # ----------------------------------------------------
        # STEP 5: WAVEFORM
        #
        # Existing waveform generation is kept.
        # ----------------------------------------------------

        waveform_path = generate_waveform(
            file_path
        )


        # ----------------------------------------------------
        # STEP 6: EXISTING FINAL SCORING
        # ----------------------------------------------------

        score_result = calculate_final_score(

            semantic_result[
                "similarity_score"
            ],

            audio_features
        )


        # ====================================================
        # STEP 7: GET LLM RESULTS
        # ====================================================

        llm_status = semantic_result.get(
            "llm_status",
            "Not Available"
        )

        llm_score = semantic_result.get(
            "llm_score",
            0
        )

        correct_answer = semantic_result.get(
            "correct_answer",
            ""
        )

        explanation = semantic_result.get(
            "explanation",
            ""
        )

        missing_points = semantic_result.get(
            "missing_points",
            []
        )

        llm_feedback = semantic_result.get(
            "llm_feedback",
            ""
        )


        # ----------------------------------------------------
        # STEP 8: FORMAT MISSING CONCEPTS
        # ----------------------------------------------------

        if missing_points:

            missing_text = "\n".join(

                f"- {point}"

                for point in missing_points
            )

        else:

            missing_text = (
                "No major missing concepts identified."
            )


        # ====================================================
        # STEP 9: COMBINED FEEDBACK
        #
        # This is sent to the existing UI.
        #
        # We are NOT changing the UI.
        # ====================================================

        combined_feedback = f"""
AI Answer Evaluation

Status:
{llm_status}

LLM Score:
{llm_score}%

Correct Answer:
{correct_answer}

Explanation:
{explanation}

Missing Concepts:
{missing_text}

AI Feedback:
{llm_feedback}

Speech Analysis:
{score_result["feedback"]}
"""


        # ====================================================
        # STEP 10: GENERATE PDF
        # ====================================================

        pdf_path = generate_pdf({

            "topic": topic,

            "transcript": transcript,

            "similarity_score": (
                semantic_result[
                    "similarity_score"
                ]
            ),

            "fluency_score": (
                score_result[
                    "fluency_score"
                ]
            ),

            "final_score": (
                score_result[
                    "final_score"
                ]
            ),

            "understanding_level": (
                semantic_result[
                    "understanding_level"
                ]
            ),

            "feedback": combined_feedback

        })


        # ====================================================
        # STEP 11: SAVE TO DATABASE
        # ====================================================

        save_result = save_analysis(

            user_id=user_id,

            topic=topic,

            transcription=transcript,

            semantic_score=(
                semantic_result[
                    "similarity_score"
                ]
            ),

            fluency_score=(
                score_result[
                    "fluency_score"
                ]
            ),

            overall_score=(
                score_result[
                    "final_score"
                ]
            ),

            feedback=combined_feedback,

            pdf_path=pdf_path

        )


        # ====================================================
        # STEP 12: RETURN RESULT
        #
        # Existing fields are preserved.
        # New AI fields are added.
        # ====================================================

        return {

            "status": "success",

            "filename": file.filename,

            "user_id": user_id,

            "topic": topic,

            # ----------------------------------------------
            # SPEECH TO TEXT
            # ----------------------------------------------

            "transcript": transcript,


            # ----------------------------------------------
            # SEMANTIC / AI EVALUATION
            # ----------------------------------------------

            "reference": semantic_result.get(
                "reference",
                correct_answer
            ),

            "similarity_score": (
                semantic_result[
                    "similarity_score"
                ]
            ),

            "understanding_level": (
                semantic_result[
                    "understanding_level"
                ]
            ),


            # ----------------------------------------------
            # NEW LLM INFORMATION
            # ----------------------------------------------

            "llm_status": llm_status,

            "llm_score": llm_score,

            "correct_answer": correct_answer,

            "explanation": explanation,

            "missing_points": missing_points,

            "llm_feedback": llm_feedback,


            # ----------------------------------------------
            # AUDIO ANALYSIS
            # ----------------------------------------------

            "audio_features": audio_features,

            "fluency_score": (
                score_result[
                    "fluency_score"
                ]
            ),


            # ----------------------------------------------
            # EXISTING FINAL SCORE
            # ----------------------------------------------

            "final_score": (
                score_result[
                    "final_score"
                ]
            ),


            # ----------------------------------------------
            # COMBINED FEEDBACK
            # ----------------------------------------------

            "feedback": combined_feedback,


            # ----------------------------------------------
            # WAVEFORM
            # ----------------------------------------------

            "waveform": waveform_path,


            # ----------------------------------------------
            # PDF
            # ----------------------------------------------

            "pdf_path": pdf_path,


            # ----------------------------------------------
            # DATABASE
            # ----------------------------------------------

            "database_save": save_result

        }


    # ========================================================
    # ERROR HANDLING
    # ========================================================

    except Exception as e:

        return {

            "status": "error",

            "message": str(e)

        }


# ============================================================
# SAVE ANALYSIS
# ============================================================

@app.post("/save-analysis")
def save_analysis_api(

    user_id: int = Form(...),

    topic: str = Form(...),

    transcription: str = Form(...),

    semantic_score: float = Form(...),

    fluency_score: float = Form(...),

    overall_score: float = Form(...),

    feedback: str = Form(...),

    pdf_path: str = Form(...)

):

    return save_analysis(

        user_id=user_id,

        topic=topic,

        transcription=transcription,

        semantic_score=semantic_score,

        fluency_score=fluency_score,

        overall_score=overall_score,

        feedback=feedback,

        pdf_path=pdf_path

    )


# ============================================================
# HISTORY
# ============================================================

@app.get("/history/{user_id}")
def history(user_id: int):

    records = get_user_history(
        user_id
    )

    return {

        "status": "success",

        "history": [
            dict(row)
            for row in records
        ]

    }


# ============================================================
# REPORT
# ============================================================

@app.get("/report/{report_id}")
def report(report_id: int):

    record = get_analysis(
        report_id
    )

    if record is None:

        return {

            "status": "error",

            "message": "Report not found"

        }


    return {

        "status": "success",

        "report": dict(record)

    }