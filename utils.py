import pdfplumber
import docx2txt
import spacy
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Load the BERT model
model = SentenceTransformer('all-MiniLM-L6-v2')

def get_similarity(resume, job_desc):
    embeddings = model.encode([resume, job_desc])
    return cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]

nlp = spacy.load("en_core_web_sm")

def extract_text(file_path):
    """Extracts text from a resume file."""
    if file_path.endswith('.pdf'):
        with pdfplumber.open(file_path) as pdf:
            return ' '.join([page.extract_text() for page in pdf.pages if page.extract_text()])
    elif file_path.endswith('.docx'):
        return docx2txt.process(file_path)
    return None

def preprocess_text(text):
    """Cleans and tokenizes text."""
    doc = nlp(text.lower())
    return " ".join([token.lemma_ for token in doc if not token.is_stop and token.is_alpha])

def rank_resume(resume_text, job_text):
    score = float(get_similarity(resume_text, job_text))  # Convert float32 to float
    feedback = "Good Match" if score > 0.7 else "Needs Improvement"
    return {"score": round(score * 100, 2), "feedback": feedback}
