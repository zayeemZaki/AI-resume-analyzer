import pdfplumber
import docx2txt
import spacy
import re
from pathlib import Path
from sklearn.metrics.pairwise import cosine_similarity
from .models import bert_model

nlp = spacy.load("en_core_web_sm")

# Month keywords to ignore date lines
MONTH_KEYWORDS = {
    "jan", "january", "feb", "february", "mar", "march", "apr", "april",
    "may", "jun", "june", "jul", "july", "aug", "august",
    "sep", "sept", "september", "oct", "october", "nov", "november", "dec", "december"
}

def contains_date_word(line):
    return any(month in line.lower() for month in MONTH_KEYWORDS)

def is_bullet_point(line):
    return line.strip().startswith(("•", "-", "*"))

def extract_text(file_path):
    path = Path(file_path)
    suffix = path.suffix.lower()
    bullet_lines = []

    if suffix == '.pdf':
        with pdfplumber.open(str(path)) as pdf:
            current_bullet = ""
            for page in pdf.pages:
                lines = page.extract_text().splitlines()
                for line in lines:
                    clean = line.strip()
                    if not clean or contains_date_word(clean):
                        continue
                    if is_bullet_point(clean):
                        if current_bullet:
                            bullet_lines.append(current_bullet.strip())
                        current_bullet = clean  # start new bullet
                    else:
                        current_bullet += " " + clean  # continuation
            if current_bullet:
                bullet_lines.append(current_bullet.strip())
        return "\n".join(bullet_lines).strip()

def preprocess_text(text):
    """
    Cleans and tokenizes text.
    """
    doc = nlp(text.lower())
    return " ".join([token.lemma_ for token in doc if not token.is_stop and token.is_alpha])

def get_similarity(resume, job_desc):
    """
    Computes similarity score using BERT embeddings.
    """
    embeddings = bert_model.encode([resume, job_desc])
    return cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]

def rank_resume(resume_text, job_text):
    """Ranks the resume against the job description"""
    try:
        if not resume_text or not job_text:
            return {"score": 0, "feedback": "Invalid input", "missing_keywords": []}

        score = float(get_similarity(resume_text, job_text))
        feedback = "Good Match" if score > 0.7 else "Needs Improvement"
        from .keywords import analyze_keywords
        missing_keywords = analyze_keywords(resume_text, job_text)
        return {
            "score": round(score * 100, 2),
            "feedback": feedback,
            "missing_keywords": missing_keywords
        }
    except Exception as e:
        print(f"Ranking Error: {str(e)}")
        return {"score": 0, "feedback": "Analysis failed", "missing_keywords": []}
