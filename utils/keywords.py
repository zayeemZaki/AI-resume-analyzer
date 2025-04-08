from collections import Counter
from sklearn.metrics.pairwise import cosine_similarity
import spacy
from spacy.matcher import PhraseMatcher
from skillNer.general_params import SKILL_DB
from skillNer.skill_extractor_class import SkillExtractor
from .models import bert_model  # Make sure this points to your actual BERT model instance

# Initialize spaCy and SkillNER
nlp = spacy.load("en_core_web_sm")
skill_extractor = SkillExtractor(nlp, SKILL_DB, PhraseMatcher)

def filter_generic_keywords(keywords, generic_words, threshold=0.6):
    """Filter out generic keywords using semantic similarity"""
    filtered_keywords = []
    generic_embeddings = bert_model.encode(list(generic_words))
    
    for word in keywords:
        word_embedding = bert_model.encode([word])[0]
        similarities = cosine_similarity([word_embedding], generic_embeddings)[0]
        if max(similarities) < threshold:
            filtered_keywords.append(word)
    return filtered_keywords

def extract_keywords(text, top_n=15, must_include=None):
    """Extract keywords using SkillNER with enhanced filtering"""
    if must_include is None:
        must_include = {"flask", "python", "nlp", "developer"}

    doc = nlp(text.lower())

    # Extract skills using SkillNER
    annotations = skill_extractor.annotate(text)
    
    skill_keywords = [
        skill['doc_node_value'].lower()
        for skill in annotations['results']['full_matches'] + annotations['results']['ngram_scored']
    ]
    
    # Add must-include keywords if present in text
    skill_keywords += [word for word in must_include if word in text.lower()]
    
    # Filter generic terms
    generic_words = {
        "experience", "job", "skill", "data",
        "system", "project", "resume", "candidate"
    }
    
    top_candidates = [word for word, _ in Counter(skill_keywords).most_common(top_n * 2)]
    
    filtered = filter_generic_keywords(top_candidates, generic_words)

    return list(set(filtered[:top_n]))  # Deduplicate and limit to top_n

def analyze_keywords(resume_text, job_text):
    """Compare resume and job description keywords"""
    job_keywords = set(extract_keywords(job_text))
    resume_keywords = set(extract_keywords(resume_text))
    return list(job_keywords - resume_keywords)
