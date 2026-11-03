from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate


def build_report_pdf(role, questions_answered, duration, report):
    buffer = BytesIO()
    document = SimpleDocTemplate(
        buffer, pagesize = A4, title = "Crack interview Report"
    )
    styles = getSampleStyleSheet()
    minutes, seconds = divmod(duration, 60)

    story = [
        Paragraph("Crack Interview Report", styles["Title"]),
        Paragraph(
            f"{escape(role)} | {questions_answered} questions answered"
            f" | {minutes}:{seconds:02d}",
            styles["Normal"],
        ),
        Paragraph("Scores", styles["Heading2"]),
    ]

    for label, key in [
        ("Overall performance", "overall_score"),
        ("Technical accuracy", "technical_accuracy"),
        ("Communication", "communication"),
        ("Confidence", "confidence"),
    ]:
        score = report.get(key)
        display_score = "Unavailable" if score is None else f"{score}/100"
        story.append(Paragraph(
            f"{label}: {escape(display_score)}", styles["Normal"]
        ))

    story.append(Paragraph("Summary", styles["Heading2"]))
    story.append(Paragraph(
        escape(report.get("summary") or "No summary available."),
        styles["BodyText"], 
    ))

    for label, key in [
        ("Strengths", "strengths"),
        ("Weaknesses", "weaknesses"),
        ("Recommendation", "recommendation"),
    ]:
        story.append(Paragraph(label, styles["Heading2"]))
        for item in report.get(key) or ["None recorded."]:
            story.append(Paragraph(
                escape(str(item)), styles["BodyText"], bulletText = "•"
            ))

    document.build(story)
    buffer.seek(0)
    return buffer