import pdfplumber
import docx2txt
import spacy
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import os
from collections import Counter

# Load the NLP model
nlp = spacy.load("en_core_web_sm")

# Load the SentenceTransformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

def filter_generic_keywords(keywords, generic_words, threshold=0.6):
    """
    Filter out keywords that are semantically similar to generic words.
    Uses SentenceTransformer embeddings and cosine similarity to determine similarity.
    """
    filtered_keywords = []
    # Compute embeddings for the generic words once
    generic_embeddings = model.encode(list(generic_words))
    for word in keywords:
        word_embedding = model.encode([word])[0]
        similarities = cosine_similarity([word_embedding], generic_embeddings)[0]
        if max(similarities) < threshold:
            filtered_keywords.append(word)
    return filtered_keywords

def extract_keywords(text, top_n=15, must_include=None):
    """
    Extract top_n most frequent and important keywords from the text.
    Only nouns and proper nouns are considered, and then filtered using ML-based semantic similarity.
    Additionally, any keywords from the must_include list (if present in the text) will be added.
    """
    if must_include is None:
        must_include = {"flask", "python", "nlp", "developer"}  # add other critical keywords as needed

    doc = nlp(text.lower())
    # Consider only nouns and proper nouns
    keywords = [token.lemma_ for token in doc if token.pos_ in ['NOUN', 'PROPN']]
    # Get more keywords than needed to have room for filtering
    common_keywords = [word for word, _ in Counter(keywords).most_common(top_n * 2)]
    
    # Define a set of generic words to filter out
    generic_words = {"experience", "look", "job", "candidate", "skill", "information", "data", "system", "project", "resume"}
    
    # Filter out generic keywords using ML-based semantic similarity
    filtered_keywords = filter_generic_keywords(common_keywords, generic_words, threshold=0.6)
    
    # Convert list to set for union operation
    keyword_set = set(filtered_keywords[:top_n])
    
    # Check must_include words: if they're present in the text, add them
    for word in must_include:
        if word in text.lower():
            keyword_set.add(word)
    
    return list(keyword_set)


def analyze_keywords(resume_text, job_text):
    """Compare resume keywords with job description keywords."""
    job_keywords = set(extract_keywords(job_text, top_n=15))
    resume_keywords = set(extract_keywords(resume_text, top_n=15))
    missing_keywords = job_keywords - resume_keywords
    return list(missing_keywords)


def extract_text(file_path):
    """Extracts text from a resume file (PDF or DOCX)."""
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

def get_similarity(resume, job_desc):
    """Compute similarity score using BERT embeddings."""
    embeddings = model.encode([resume, job_desc])
    return cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]

def rank_resume(resume_text, job_text):
    """Rank resume against job description and suggest missing keywords."""
    score = float(get_similarity(resume_text, job_text))  # Convert float32 to float
    feedback = "Good Match" if score > 0.7 else "Needs Improvement"
    missing_keywords = analyze_keywords(resume_text, job_text)
    return {
        "score": round(score * 100, 2),
        "feedback": feedback,
        "missing_keywords": missing_keywords
    }
