def calculate_final_score(similarity_score, audio_features):
    fluency_score = 100

    if audio_features["filler_count"] > 5:
        fluency_score -= 20
    elif audio_features["filler_count"] > 2:
        fluency_score -= 10

    if audio_features["pause_ratio"] > 50:
        fluency_score -= 20
    elif audio_features["pause_ratio"] > 30:
        fluency_score -= 10

    if audio_features["speech_rate"] < 80 or audio_features["speech_rate"] > 180:
        fluency_score -= 10

    fluency_score = max(0, fluency_score)

    final_score = round((similarity_score * 0.7) + (fluency_score * 0.3), 2)

    if final_score >= 75:
        feedback = "Excellent explanation with strong concept understanding and good fluency."
    elif final_score >= 50:
        feedback = "Good attempt, but explanation needs more clarity and better fluency."
    else:
        feedback = "Needs improvement in both concept understanding and speech delivery."

    return {
        "fluency_score": fluency_score,
        "final_score": final_score,
        "feedback": feedback
    }