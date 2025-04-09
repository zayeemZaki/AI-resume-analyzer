import pdfplumber
import docx2txt
import spacy
from pathlib import Path
from sklearn.metrics.pairwise import cosine_similarity
from .models import bert_model

nlp = spacy.load("en_core_web_sm")

def extract_text(file_path):
    """
    Extracts and formats text from PDF/DOCX resumes with enhanced grouping.
    """
    path = Path(file_path)
    suffix = path.suffix.lower()

    def is_section(line):
        return line.isupper() and len(line.split()) <= 5 and not line.startswith("•")

    def is_contact(line):
        return "@" in line or "|" in line or "http" in line

    def is_bullet(line):
        return line.strip().startswith(("•", "-", "*"))

    text = ""
    if suffix == '.pdf':
        with pdfplumber.open(str(path)) as pdf:
            for page in pdf.pages:
                raw_lines = page.extract_text().splitlines()
                for line in raw_lines:
                    line = line.strip()
                    if not line:
                        text += "\n"
                        continue

                    if is_section(line):
                        text += f"\n\n{line}\n"
                    elif is_contact(line):
                        text += f"{line}\n"
                    elif is_bullet(line):
                        text += f"\n{line}"
                    else:
                        text += f" {line}"
        return text.strip()

    elif suffix == '.docx':
        return docx2txt.process(str(path)).strip()

    return None


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
