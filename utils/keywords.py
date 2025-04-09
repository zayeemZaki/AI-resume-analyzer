from collections import Counter
from sklearn.metrics.pairwise import cosine_similarity
import spacy
from spacy.matcher import PhraseMatcher
from skillNer.general_params import SKILL_DB
from skillNer.skill_extractor_class import SkillExtractor
from .models import bert_model  # Ensure bert_model is properly loaded
import nltk
from nltk.corpus import stopwords

# Load nltk stopwords
nltk.download('stopwords')

# Load spaCy models
nlp_skillner = spacy.load("en_core_web_lg")
nlp_nouns = spacy.load("en_core_web_sm")

# Initialize SkillNER
skill_extractor = SkillExtractor(nlp_skillner, SKILL_DB, PhraseMatcher)

# Function to load custom generic words from a file
def load_generic_words(filepath="static/generic_words.txt"):
    with open(filepath, "r") as file:
        custom_words = {line.strip().lower() for line in file if line.strip()}
    nltk_words = set(stopwords.words('english'))
    return custom_words.union(nltk_words)

# Load generic words once (efficient)
GENERIC_WORDS = load_generic_words()

def filter_generic_keywords(keywords, generic_words, threshold=0.6):
    filtered_keywords = []
    generic_embeddings = bert_model.encode(list(generic_words))
    
    for word in keywords:
        word_embedding = bert_model.encode([word])[0]
        similarities = cosine_similarity([word_embedding], generic_embeddings)[0]
        if max(similarities) < threshold:
            filtered_keywords.append(word)
    return filtered_keywords

def extract_skills_skillner(text):
    annotations = skill_extractor.annotate(text)
    skills = {
        skill['doc_node_value'].lower()
        for skill in annotations['results']['full_matches'] + annotations['results']['ngram_scored']
    }
    return skills

def extract_nouns_spacy(text):
    doc = nlp_nouns(text.lower())
    nouns = {token.text for token in doc if token.pos_ in ("NOUN", "PROPN") and token.pos_ != "VERB"}
    return nouns

def extract_resume_keywords(text, top_n=20, must_include=None):
    if must_include is None:
        must_include = {"flask", "python", "nlp", "developer"}

    skillner_skills = extract_skills_skillner(text)
    spacy_nouns = extract_nouns_spacy(text)

    combined_keywords = skillner_skills.union(spacy_nouns, must_include)

    # Use the loaded GENERIC_WORDS set
    filtered_keywords = filter_generic_keywords(combined_keywords, GENERIC_WORDS)

    keyword_freq = Counter({kw: text.lower().count(kw) for kw in filtered_keywords})
    top_keywords = [word for word, _ in keyword_freq.most_common(top_n)]

    return set(top_keywords)

def extract_job_keywords(text, top_n=20):
    skillner_skills = extract_skills_skillner(text)
    spacy_nouns = extract_nouns_spacy(text)

    combined_keywords = skillner_skills.intersection(spacy_nouns)

    # Use the loaded GENERIC_WORDS set
    filtered_keywords = filter_generic_keywords(combined_keywords, GENERIC_WORDS)

    keyword_freq = Counter({kw: text.lower().count(kw) for kw in filtered_keywords})
    top_keywords = [word for word, _ in keyword_freq.most_common(top_n)]

    return set(top_keywords)

def analyze_keywords(resume_text, job_text):
    resume_keywords = extract_resume_keywords(resume_text)
    job_keywords = extract_job_keywords(job_text)
    return list(job_keywords - resume_keywords)
