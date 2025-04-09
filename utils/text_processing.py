import pdfplumber
import docx2txt
import spacy
from pathlib import Path
from sklearn.metrics.pairwise import cosine_similarity
from .models import bert_model

nlp = spacy.load("en_core_web_sm")

def extract_text(file_path):
    """
    Extracts and formats text from PDF/DOCX resumes.
    Enhances grouping by separating headers, links, and sections.
    """
    path = Path(file_path)
    suffix = path.suffix.lower()

    if suffix == '.pdf':
        text = ""
        with pdfplumber.open(str(path)) as pdf:
            for page in pdf.pages:
                lines = page.extract_text().splitlines()
                for line in lines:
                    clean = line.strip()
                    if clean.isupper() and len(clean.split()) <= 4:
                        text += f"\n\n{clean}\n"
                    elif "@" in clean or "|" in clean or "http" in clean:
                        text += f"{clean}\n"
                    else:
                        text += f"{clean}\n"
        return text.strip()

    elif suffix == '.docx':
        return docx2txt.process(str(path))

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
