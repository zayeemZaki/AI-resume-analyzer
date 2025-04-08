# utils/grammar.py
import spacy
from collections import defaultdict

nlp = spacy.load("en_core_web_sm")

def check_grammar(text):
    """Comprehensive grammar and style analysis"""
    doc = nlp(text)
    issues = []
    metrics = defaultdict(int)
    
    # Check for first-person pronouns
    for token in doc:
        if token.lower_ in {"i", "my", "me"}:
            metrics["first_person"] += 1
    
    # Passive voice detection
    for sent in doc.sents:
        if any(tok.dep_ == "nsubjpass" for tok in sent):
            metrics["passive_voice"] += 1
    
    # Readability metrics
    meaningful_tokens = [token for token in doc if not token.is_stop and token.is_alpha]
    metrics["content_density"] = len(meaningful_tokens)
    
    # Generate human-readable issues
    if metrics["first_person"] > 0:
        issues.append(f"Avoid first-person pronouns (found {metrics['first_person']} instances)")
    if metrics["passive_voice"] > 2:
        issues.append(f"Reduce passive voice (found {metrics['passive_voice']} instances)")
    if metrics["content_density"] < 150:
        issues.append("Document seems sparse - add more quantitative achievements")
    
    return issues