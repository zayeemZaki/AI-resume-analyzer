# parsing.py (updated)
import re
import spacy
from .grouping import get_hybrid_grouping_analysis

# Load specialized resume NER model
nlp = spacy.load("en_core_web_sm")  # Replace with actual ResumeNER model if available

COMMON_SECTIONS = {
    "experience", "education", "skills", "projects",
    "certifications", "summary", "objective"
}

SECTION_PATTERNS = {
    'experience': [
        r"(?i)\b(work\s*history|professional\s*experience|employment\s*background)\b",
        r"(?i)\b(experience|positions|roles)\b"
    ],
    'education': [
        r"(?i)\b(academic\s*background|degrees?|qualifications|education)\b",
        r"(?i)\b(university|college|school)\b"
    ],
    'skills': [
        r"(?i)\b(technical\s*skills|competencies|proficiencies)\b",
        r"(?i)\b(languages|frameworks|tools)\b"
    ]
}

def detect_section_with_ner(line):
    """Use NER to detect section headers"""
    doc = nlp(line)
    for ent in doc.ents:
        if ent.label_ == "SECTION_HEADER":  # Requires custom NER model
            return ent.text.lower()
    return None

def normalize_section_name(text):
    """Map variations to standard section names"""
    text = text.lower().strip()
    for section, patterns in SECTION_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, text):
                return section
    return None

def merge_lines(lines, current_idx):
    """Handle multi-line section headers"""
    merged = lines[current_idx]
    next_idx = current_idx + 1
    while next_idx < len(lines):
        if len(lines[next_idx].split()) < 3:  # Assume section headers are short
            merged += " " + lines[next_idx]
            next_idx += 1
        else:
            break
    return merged, next_idx - current_idx - 1

def extract_resume_sections(text):
    """Enhanced section extraction with hybrid approach"""
    sections = {s: [] for s in COMMON_SECTIONS}
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    current_section = None
    skip = 0

    for i, line in enumerate(lines):
        if skip > 0:
            skip -= 1
            continue
            
        # Try merged lines first
        merged_line, lines_skipped = merge_lines(lines, i)
        skip = lines_skipped
        
        # Detection methods in priority order
        detected = (
            normalize_section_name(merged_line) or
            detect_section_with_ner(merged_line) or
            normalize_section_name(line)
        )
        
        if detected and detected in COMMON_SECTIONS:
            current_section = detected
        elif current_section:
            sections[current_section].append(line)

    # Fallback to regex patterns
    if not any(sections.values()):
        for section in COMMON_SECTIONS:
            for pattern in SECTION_PATTERNS.get(section, [rf"(?i)\b{section}\b"]):
                matches = [i for i, line in enumerate(lines) if re.search(pattern, line)]
                if matches:
                    start = matches[0] + 1
                    end = matches[1] if len(matches) > 1 else len(lines)
                    sections[section] = lines[start:end]

    return {k: v for k, v in sections.items() if v}