# utils/parsing.py
import re
from .grouping import get_hybrid_grouping_analysis

COMMON_SECTIONS = {
    "experience", "education", "skills", "projects",
    "certifications", "summary", "objective"
}

def extract_resume_sections(text):
    """Extract sections using hybrid ML+regex approach"""
    sections = {s: [] for s in COMMON_SECTIONS}
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    # First pass: ML-based section detection
    for line in lines:
        if line.upper() in COMMON_SECTIONS:
            section = line.lower()
            sections[section] = []
            current_section = section
        elif 'current_section' in locals():
            sections[current_section].append(line)
    
    # Fallback: Regex pattern matching
    if not any(sections.values()):
        for section in COMMON_SECTIONS:
            pattern = re.compile(fr'^\s*{section}\s*$', re.IGNORECASE)
            matches = [i for i, line in enumerate(lines) if pattern.match(line)]
            if matches:
                start = matches[0] + 1
                end = matches[1] if len(matches) > 1 else len(lines)
                sections[section] = lines[start:end]
    
    return {k: v for k, v in sections.items() if v}