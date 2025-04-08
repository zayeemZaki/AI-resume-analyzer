# keywords.py
import re
import spacy
import requests
import numpy as np
from collections import defaultdict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Set

# Initialize core NLP models
nlp = spacy.load("en_core_web_lg")
sentence_model = SentenceTransformer('all-MiniLM-L6-v2')

class SkillOntology:
    """Enterprise skill database connector"""
    def __init__(self):
        self.ESCO_API = "https://ec.europa.eu/esco/api"
        self.OCCUPATION_MAP = {
            'IT': 'http://data.europa.eu/esco/occupation/26453a5c-0b46-4fca-80b9-9116b679a2c3',
            'Engineering': 'http://data.europa.eu/esco/occupation/0f40c7e3-0e7c-4a04-aa6d-b27e801daa42'
        }
        self.cache = defaultdict(dict)

    def get_skills(self, industry: str = 'IT') -> Dict[str, List[str]]:
        """Fetch skills from ESCO API with caching"""
        if industry in self.cache:
            return self.cache[industry]
            
        try:
            response = requests.get(
                f"{self.ESCO_API}/resource/occupation?uri={self.OCCUPATION_MAP[industry]}"
            )
            skills_data = response.json()['hasEssentialSkill']
            skills = {}
            
            for skill in skills_data:
                term = skill['preferredLabel']['en']
                alt_terms = [alt['en'] for alt in skill['altLabels']]
                skills[term.lower()] = [t.lower() for t in alt_terms]
            
            self.cache[industry] = skills
            return skills
            
        except Exception as e:
            # Fallback to local ontology
            return {
                'cloud': ['azure', 'aws', 'gcp', 'cloud computing'],
                'containerization': ['docker', 'kubernetes', 'openshift'],
                'cybersecurity': ['kali linux', 'penetration testing', 'ethical hacking']
            }

class KeywordAnalyzer:
    """Production-grade keyword analysis engine"""
    def __init__(self):
        self.ontology = SkillOntology()
        self.generic_terms = self._load_generic_terms()
    
    def _load_generic_terms(self) -> Set[str]:
        """Dynamic generic term detection using semantic similarity"""
        base_terms = {
            'culture', 'opportunity', 'benefit', 'environment', 
            'growth', 'team', 'company', 'experience'
        }
        
        # Expand using semantic similarity
        base_embeddings = sentence_model.encode(list(base_terms))
        similar_terms = set()
        
        for term in base_terms:
            sims = cosine_similarity(
                [sentence_model.encode(term)],
                base_embeddings
            )[0]
            similar_terms.update(
                [list(base_terms)[i] for i in np.where(sims > 0.7)[0]]  # Fixed line
            )
        
        return similar_terms

    def _extract_technical_terms(self, text: str) -> Set[str]:
        """Advanced technical term extraction pipeline"""
        doc = nlp(text.lower())
        terms = set()

        # Custom entity ruler for tech terms
        ruler = nlp.add_pipe("entity_ruler", config={"overwrite_ents": True})
        patterns = [
            {"label": "CLOUD", "pattern": [{"LOWER": {"IN": ["azure", "aws", "gcp"]}}]},
            {"label": "DEV_OPS", "pattern": [{"LOWER": {"IN": ["docker", "kubernetes", "jenkins"]}}]}
        ]
        ruler.add_patterns(patterns)

        # Extract entities and noun chunks
        for ent in doc.ents:
            if ent.label_ in ["CLOUD", "DEV_OPS", "ORG", "PRODUCT"]:
                terms.add(ent.text.lower())
        
        # Extract meaningful noun phrases
        for chunk in doc.noun_chunks:
            if 1 <= len(chunk) <= 3 and any(t.pos_ in ["NOUN", "PROPN"] for t in chunk):
                terms.add(chunk.text.lower())
        
        return terms

    def _expand_terms(self, terms: Set[str], industry: str) -> Set[str]:
        """Expand terms using skill ontology and semantic similarity"""
        ontology_skills = self.ontology.get_skills(industry)
        expanded = set()
        
        for term in terms:
            # Direct synonyms
            expanded.update(ontology_skills.get(term, []))
            
            # Semantic expansion
            term_embed = sentence_model.encode([term])
            for skill, aliases in ontology_skills.items():
                skill_embed = sentence_model.encode([skill])
                if cosine_similarity(term_embed, skill_embed)[0][0] > 0.65:
                    expanded.update(aliases)
        
        return expanded

    def analyze(self, resume_text: str, job_text: str, industry: str = 'IT') -> List[str]:
        """Main analysis pipeline"""
        # Extract base terms
        job_terms = self._extract_technical_terms(job_text)
        resume_terms = self._extract_technical_terms(resume_text)
        
        # Expand using ontology
        expanded_job = self._expand_terms(job_terms, industry)
        
        # TF-IDF prioritization
        tfidf = TfidfVectorizer(ngram_range=(1, 3), stop_words='english')
        try:
            tfidf.fit([' '.join(expanded_job)])
            important_terms = [
                term for term in expanded_job
                if term in tfidf.vocabulary_
            ]
        except ValueError:
            important_terms = list(expanded_job)
        
        # Calculate missing keywords
        missing = [
            term for term in important_terms
            if term not in resume_terms
            and term not in self.generic_terms
            and not re.match(r'^\d+$', term)
        ]
        
        return missing[:15]

def analyze_keywords(resume_text: str, job_text: str, industry: str = 'IT') -> List[str]:
    """Public-facing keyword analysis function"""
    analyzer = KeywordAnalyzer()
    return analyzer.analyze(resume_text, job_text, industry)
