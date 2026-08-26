import os
from typing import List

from dotenv import load_dotenv

from sentence_transformers import SentenceTransformer, util

from google import genai
from google.genai import types

from pydantic import BaseModel


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


# ============================================================
# SENTENCE TRANSFORMER
# ============================================================

model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


# ============================================================
# GEMINI CLIENT
# ============================================================

client = None

if GEMINI_API_KEY:

    client = genai.Client(
        api_key=GEMINI_API_KEY
    )


# ============================================================
# RESPONSE MODEL
# ============================================================

class AnswerEvaluation(BaseModel):

    status: str

    score: float

    correct_answer: str

    explanation: str

    missing_points: List[str]

    feedback: str


# ============================================================
# GEMINI EVALUATION
# ============================================================

def evaluate_answer_with_llm(
    transcript,
    topic
):

    if not GEMINI_API_KEY or not client:

        return {

            "status": "LLM Not Configured",

            "score": 0,

            "correct_answer": "",

            "explanation": "",

            "missing_points": [],

            "feedback": (
                "Gemini API key is not configured."
            )

        }


    prompt = f"""
You are an educational answer evaluator.

Evaluate the student's spoken answer about the topic.

TOPIC:
{topic}

STUDENT ANSWER:
{transcript}

Evaluate the answer based on conceptual understanding.

Important rules:

1. Judge meaning, not exact wording.
2. Accept different valid explanations.
3. Do not heavily penalize grammar mistakes.
4. Identify important correct concepts.
5. Identify incorrect concepts.
6. Identify important missing concepts.
7. Give a score from 0 to 100.
8. Give a simple educational explanation.
9. Give useful feedback to the student.

Use these status values:

Correct
Partially Correct
Incorrect

Scoring:

90-100 = Excellent understanding
75-89 = Good understanding
50-74 = Partial understanding
25-49 = Limited understanding
0-24 = Incorrect or unrelated

Return:

status
score
correct_answer
explanation
missing_points
feedback
"""


    try:

        response = client.models.generate_content(

            model="gemini-3.6-flash",

            contents=prompt,

            config=types.GenerateContentConfig(

                response_mime_type="application/json",

                response_schema=AnswerEvaluation

            )

        )


        evaluation = response.parsed


        if evaluation is None:

            evaluation = (
                AnswerEvaluation.model_validate_json(
                    response.text
                )
            )


        return {

            "status": evaluation.status,

            "score": float(
                evaluation.score
            ),

            "correct_answer": (
                evaluation.correct_answer
            ),

            "explanation": (
                evaluation.explanation
            ),

            "missing_points": (
                evaluation.missing_points
            ),

            "feedback": (
                evaluation.feedback
            )

        }


    except Exception as e:

        # ----------------------------------------------------
        # Gemini failed.
        #
        # DO NOT stop the application.
        #
        # Return a special status so calculate_similarity()
        # can automatically use Sentence-BERT.
        # ----------------------------------------------------

        return {

            "status": "LLM Unavailable",

            "score": 0,

            "correct_answer": "",

            "explanation": "",

            "missing_points": [],

            "feedback": (
                "Gemini is currently unavailable. "
                "Using local semantic analysis instead."
            ),

            "error": str(e)

        }


# ============================================================
# LOCAL FALLBACK EVALUATION
# ============================================================

def local_semantic_evaluation(
    transcript,
    topic
):

    """
    Local fallback.

    This does not use hardcoded topic answers.

    It compares the student's answer against the topic
    itself using Sentence-BERT.

    This allows the application to continue working when
    Gemini quota/API access is unavailable.
    """

    try:

        student_embedding = model.encode(

            transcript,

            convert_to_tensor=True

        )

        topic_embedding = model.encode(

            topic,

            convert_to_tensor=True

        )

        similarity = util.cos_sim(

            student_embedding,

            topic_embedding

        ).item()


        similarity_score = round(

            max(
                0,
                min(
                    similarity * 100,
                    100
                )
            ),

            2

        )


        if similarity_score >= 75:

            level = "Strong Understanding"

        elif similarity_score >= 50:

            level = "Moderate Understanding"

        else:

            level = "Poor Understanding"


        return {

            "reference": topic,

            "similarity_score": similarity_score,

            "understanding_level": level,

            "llm_status": "LLM Unavailable",

            "llm_score": similarity_score,

            "correct_answer": (
                "AI evaluation is temporarily unavailable. "
                "The answer was evaluated using local "
                "semantic similarity."
            ),

            "explanation": (
                "The system compared the student's "
                "transcript with the selected topic "
                "using Sentence-BERT."
            ),

            "missing_points": [],

            "llm_feedback": (
                "Gemini is currently unavailable because "
                "of API quota or connectivity. "
                "Local semantic analysis was used instead."
            )

        }


    except Exception as e:

        return {

            "reference": topic,

            "similarity_score": 0,

            "understanding_level": "Unable to Evaluate",

            "llm_status": "Evaluation Error",

            "llm_score": 0,

            "correct_answer": "",

            "explanation": "",

            "missing_points": [],

            "llm_feedback": (
                f"Evaluation failed: {str(e)}"
            )

        }


# ============================================================
# MAIN SEMANTIC ANALYSIS
# ============================================================

def calculate_similarity(
    transcript,
    topic
):

    # --------------------------------------------------------
    # STEP 1
    # Try Gemini
    # --------------------------------------------------------

    llm_result = evaluate_answer_with_llm(

        transcript,

        topic

    )


    llm_status = llm_result.get(
        "status",
        ""
    )


    # --------------------------------------------------------
    # STEP 2
    # If Gemini failed, use local fallback
    # --------------------------------------------------------

    if llm_status in [

        "LLM Unavailable",

        "LLM Not Configured"

    ]:

        return local_semantic_evaluation(

            transcript,

            topic

        )


    # --------------------------------------------------------
    # STEP 3
    # Gemini was successful
    # --------------------------------------------------------

    correct_answer = llm_result.get(

        "correct_answer",

        ""

    )


    llm_score = float(

        llm_result.get(

            "score",

            0

        )

    )


    # --------------------------------------------------------
    # Sentence-BERT comparison
    # --------------------------------------------------------

    if correct_answer:

        student_embedding = model.encode(

            transcript,

            convert_to_tensor=True

        )

        answer_embedding = model.encode(

            correct_answer,

            convert_to_tensor=True

        )

        similarity = util.cos_sim(

            student_embedding,

            answer_embedding

        ).item()


        similarity_score = round(

            max(
                0,
                min(
                    similarity * 100,
                    100
                )
            ),

            2

        )

    else:

        similarity_score = 0


    # --------------------------------------------------------
    # Combine AI + semantic score
    # --------------------------------------------------------

    combined_score = round(

        (
            llm_score * 0.70
        )
        +
        (
            similarity_score * 0.30
        ),

        2

    )


    # --------------------------------------------------------
    # Understanding level
    # --------------------------------------------------------

    if combined_score >= 75:

        understanding_level = (
            "Strong Understanding"
        )

    elif combined_score >= 50:

        understanding_level = (
            "Moderate Understanding"
        )

    else:

        understanding_level = (
            "Poor Understanding"
        )


    # --------------------------------------------------------
    # Return result
    # --------------------------------------------------------

    return {

        "reference": correct_answer,

        "similarity_score": combined_score,

        "understanding_level": (
            understanding_level
        ),

        "llm_status": llm_status,

        "llm_score": llm_score,

        "correct_answer": correct_answer,

        "explanation": llm_result.get(

            "explanation",

            ""

        ),

        "missing_points": llm_result.get(

            "missing_points",

            []

        ),

        "llm_feedback": llm_result.get(

            "feedback",

            ""

        )

    }