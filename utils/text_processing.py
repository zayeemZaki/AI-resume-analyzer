import pdfplumber
import docx2txt
import spacy
from pathlib import Path
from sklearn.metrics.pairwise import cosine_similarity
from .models import bert_model

nlp = spacy.load("en_core_web_sm")

def extract_text(file_path):
    """
    Extracts text from a resume file (PDF or DOCX) using Path objects.
    """
    path = Path(file_path)
    suffix = path.suffix.lower()
    
    if suffix == '.pdf':
        with pdfplumber.open(str(path)) as pdf:  # Convert Path to string for opening
            return ' '.join([page.extract_text() for page in pdf.pages if page.extract_text()])
    elif suffix == '.docx':
        return docx2txt.process(str(path))  # Convert Path to string for processing
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