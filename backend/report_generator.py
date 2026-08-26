from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
import os

REPORT_FOLDER = "reports"
os.makedirs(REPORT_FOLDER, exist_ok=True)

styles = getSampleStyleSheet()

def generate_pdf(result):

    filename = f"{result['topic'].replace(' ','_')}_Report.pdf"

    pdf_path = os.path.join(REPORT_FOLDER, filename)

    doc = SimpleDocTemplate(pdf_path)

    elements = []

    elements.append(Paragraph("<b>Voice-Based Concept Understanding Analyser</b>", styles["Title"]))

    elements.append(Paragraph("<br/>", styles["BodyText"]))

    elements.append(Paragraph(f"<b>Topic:</b> {result['topic']}", styles["BodyText"]))

    elements.append(Paragraph(f"<b>Transcript:</b> {result['transcript']}", styles["BodyText"]))

    elements.append(Paragraph(f"<b>Semantic Similarity:</b> {result['similarity_score']}%", styles["BodyText"]))

    elements.append(Paragraph(f"<b>Fluency Score:</b> {result['fluency_score']}%", styles["BodyText"]))

    elements.append(Paragraph(f"<b>Final Score:</b> {result['final_score']}%", styles["BodyText"]))

    elements.append(Paragraph(f"<b>Understanding Level:</b> {result['understanding_level']}", styles["BodyText"]))

    elements.append(Paragraph(f"<b>Feedback:</b> {result['feedback']}", styles["BodyText"]))

    doc.build(elements)

    return pdf_path