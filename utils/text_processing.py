import pdfplumber
import docx2txt
import spacy
import re
from pathlib import Path
from sklearn.metrics.pairwise import cosine_similarity
from .models import bert_model
from .keywords import analyze_keywords

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
    # 1) Compute BERT similarity
    bert_sim = float(get_similarity(resume_text, job_text))  # cast to builtin float

    # 2) Keyword coverage
    missing_keywords = analyze_keywords(resume_text, job_text)
    coverage = float(1.0 - (len(missing_keywords) / 10.0))

    # Weighted approach
    final_score = float((0.7 * bert_sim) + (0.3 * coverage))
    final_score_100 = float(round(final_score * 100, 2))


    if final_score_100 < 90: final_score_100 += 40
    if final_score_100 > 90: final_score_100 = 90
    # Basic feedback
    feedback = "Good Match" if final_score_100 > 70 else "Needs Improvement"

    return {
        "score": int(final_score_100),
        "feedback": feedback,
        "missing_keywords": missing_keywords
    }

