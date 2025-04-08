from collections import Counter
from sklearn.metrics.pairwise import cosine_similarity
import spacy
from .models import bert_model

nlp = spacy.load("en_core_web_sm")

def filter_generic_keywords(keywords, generic_words, threshold=0.6):
    """
    Filters out keywords that are semantically similar to generic words.
    """
    filtered_keywords = []
    generic_embeddings = bert_model.encode(list(generic_words))
    for word in keywords:
        word_embedding = bert_model.encode([word])[0]
        similarities = cosine_similarity([word_embedding], generic_embeddings)[0]
        if max(similarities) < threshold:
            filtered_keywords.append(word)
    return filtered_keywords

def extract_keywords(text, top_n=15, must_include=None):
    """
    Extracts the top_n frequent keywords (nouns and proper nouns) from the text.
    Also adds any must-include keywords if found.
    """
    if must_include is None:
        must_include = {"flask", "python", "nlp", "developer"}
    doc = nlp(text.lower())
    keywords = [token.lemma_ for token in doc if token.pos_ in ['NOUN', 'PROPN']]
    common_keywords = [word for word, _ in Counter(keywords).most_common(top_n * 2)]
    generic_words = {"experience", "look", "job", "candidate", "skill", "information", "data", "system", "project", "resume"}
    filtered_keywords = filter_generic_keywords(common_keywords, generic_words, threshold=0.6)
    keyword_set = set(filtered_keywords[:top_n])
    for word in must_include:
        if word in text.lower():
            keyword_set.add(word)
    return list(keyword_set)

def analyze_keywords(resume_text, job_text):
    """
    Compares resume keywords with job description keywords.
    """
    job_keywords = set(extract_keywords(job_text, top_n=15))
    resume_keywords = set(extract_keywords(resume_text, top_n=15))
    missing_keywords = job_keywords - resume_keywords
    return list(missing_keywords)