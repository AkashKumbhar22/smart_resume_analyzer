import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, render_template, request

from resume_parser.pdf_parser import extract_text_from_pdf
from resume_parser.docx_parser import extract_text_from_docx
from nlp_engine.preprocess import clean_text
from nlp_engine.skill_extractor import extract_skills
from matcher.similarity import calculate_similarity

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        resume_file = request.files.get("resume")
        job_desc = request.form.get("job_description")

        if not resume_file or not job_desc:
            return render_template("index.html", score=None)

        resume_path = os.path.join(UPLOAD_FOLDER, resume_file.filename)
        resume_file.save(resume_path)

        # -------- TEXT EXTRACTION --------
        if resume_file.filename.lower().endswith(".pdf"):
            resume_text = extract_text_from_pdf(resume_path)
        elif resume_file.filename.lower().endswith(".docx"):
            resume_text = extract_text_from_docx(resume_path)
        else:
            return "Unsupported file format"

        # -------- PREPROCESSING --------
        resume_clean = clean_text(resume_text)
        job_clean = clean_text(job_desc)

        # -------- SKILL EXTRACTION --------
        resume_skills = extract_skills(resume_clean)
        job_skills = extract_skills(job_clean)

        resume_skills = list(set(resume_skills))
        job_skills = list(set(job_skills))

        # -------- SKILL MATCHING --------
        matched_skills = list(set(resume_skills).intersection(set(job_skills)))
        missing_skills = list(set(job_skills) - set(resume_skills))

        if len(job_skills) > 0:
            skill_match_score = (len(matched_skills) / len(job_skills)) * 100
        else:
            skill_match_score = 0

        # -------- TEXT SIMILARITY (SECONDARY) --------
        text_similarity = calculate_similarity(resume_clean, job_clean) * 100

        # -------- FINAL HYBRID SCORE --------
        final_score = (0.7 * skill_match_score) + (0.3 * text_similarity)

        return render_template(
            "index.html",
            score=round(final_score, 2),
            resume_skills=resume_skills,
            job_skills=job_skills,
            matched_skills=matched_skills,
            missing_skills=missing_skills
        )

    return render_template("index.html", score=None)

if __name__ == "__main__":
    app.run(debug=True)
