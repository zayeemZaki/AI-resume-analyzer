import pdfplumber
import docx2txt
import spacy
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import os
from collections import Counter
import re

# Load the NLP model
nlp = spacy.load("en_core_web_sm")

# Load the SentenceTransformer model
model = SentenceTransformer('all-MiniLM-L6-v2')



def normalize_font_name(font_name):
    """
    Normalize font names by removing common style indicators such as Bold, Italic, Regular, MT,
    and any hyphens or underscores. This ensures that fonts from the same family are treated identically.
    """
    if '+' in font_name:
        font_name = font_name.split('+')[-1]
    normalized = re.sub(r'(Bold|Italic|Regular|MT)', '', font_name, flags=re.IGNORECASE)
    normalized = normalized.replace('-', '').replace('_', '')
    return normalized.strip().lower()

def analyze_pdf_formatting(pdf_path):
    """
    Analyzes a PDF resume for font consistency, bullet usage, etc.
    Fonts that normalize to 'symbol' are ignored.
    Returns a dictionary with overall formatting statistics.
    """
    font_usage = set()
    bullet_count = 0
    total_lines = 0

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue

            lines = text.split("\n")
            total_lines += len(lines)
            for line in lines:
                line_stripped = line.strip()
                if line_stripped.startswith("-") or line_stripped.startswith("•") or line_stripped.startswith("*"):
                    bullet_count += 1

            for char in page.chars:
                raw_font = char.get("fontname", "")
                normalized_font = normalize_font_name(raw_font)
                if normalized_font == "symbol":
                    continue
                size = round(char.get("size", 0), 1)
                font_usage.add((normalized_font, size))

    unique_font_names = len({f[0] for f in font_usage})
    unique_font_sizes = len({f[1] for f in font_usage})
    bullet_percentage = (bullet_count / total_lines) * 100 if total_lines else 0

    return {
        "total_lines": total_lines,
        "bullet_count": bullet_count,
        "bullet_percentage": round(bullet_percentage, 2),
        "font_variations": len(font_usage),
        "unique_font_names": unique_font_names,
        "unique_font_sizes": unique_font_sizes,
        "all_fonts_and_sizes": list(font_usage),
    }

def get_line_info(pdf_path, y_threshold=2):
    """
    Extracts lines from the PDF along with their average font size, common font, and vertical position.
    Groups characters by similar y coordinates.
    """
    lines_info = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            # Sort characters by their y coordinate
            chars = sorted(page.chars, key=lambda c: float(c['top']))
            current_line = []
            last_top = None
            for char in chars:
                top = float(char['top'])
                if last_top is None or abs(top - last_top) < y_threshold:
                    current_line.append(char)
                    last_top = top
                else:
                    if current_line:
                        text = ''.join(c['text'] for c in current_line).strip()
                        sizes = [float(c['size']) for c in current_line]
                        avg_size = sum(sizes) / len(sizes)
                        fonts = [normalize_font_name(c['fontname']) for c in current_line]
                        common_font = max(set(fonts), key=fonts.count)
                        lines_info.append({
                            'text': text,
                            'avg_size': avg_size,
                            'font': common_font,
                            'top': last_top
                        })
                    current_line = [char]
                    last_top = top
            if current_line:
                text = ''.join(c['text'] for c in current_line).strip()
                sizes = [float(c['size']) for c in current_line]
                avg_size = sum(sizes) / len(sizes)
                fonts = [normalize_font_name(c['fontname']) for c in current_line]
                common_font = max(set(fonts), key=fonts.count)
                lines_info.append({
                    'text': text,
                    'avg_size': avg_size,
                    'font': common_font,
                    'top': last_top
                })
    return lines_info

def check_spacing_consistency(pdf_path, y_threshold=2):
    """
    Checks for consistency in vertical spacing between lines in the PDF.
    Returns a dictionary containing:
      - avg_spacing: Average spacing between consecutive lines.
      - min_spacing: Minimum spacing found.
      - max_spacing: Maximum spacing found.
      - messages: Specific feedback messages.
    """
    lines_info = get_line_info(pdf_path, y_threshold)
    if len(lines_info) < 2:
        return {
            "avg_spacing": None,
            "min_spacing": None,
            "max_spacing": None,
            "messages": ["Not enough lines to analyze vertical spacing."]
        }
    
    # Sort lines by their vertical position (top value)
    sorted_lines = sorted(lines_info, key=lambda x: x['top'])
    # Calculate spacing (difference in top values) between consecutive lines
    spacings = [sorted_lines[i+1]['top'] - sorted_lines[i]['top'] for i in range(len(sorted_lines)-1)]
    avg_spacing = sum(spacings) / len(spacings)
    min_spacing = min(spacings)
    max_spacing = max(spacings)
    spacing_range = max_spacing - min_spacing
    
    messages = []
    messages.append(f"Average vertical spacing is {avg_spacing:.2f} points (min: {min_spacing:.2f}, max: {max_spacing:.2f}).")
    
    # If the range of spacing variations is more than 50% of the average, flag it.
    if spacing_range > (avg_spacing * 0.5):
        messages.append("The vertical spacing varies significantly; consider standardizing line spacing for a consistent look.")
    else:
        messages.append("Vertical spacing is consistent.")
    
    return {
        "avg_spacing": avg_spacing,
        "min_spacing": min_spacing,
        "max_spacing": max_spacing,
        "messages": messages
    }

def check_consistency(pdf_path):
    """
    Checks for consistency in headings and vertical spacing.
    Headings are identified heuristically as lines in all uppercase (with more than 2 characters).
    Returns a list of detailed consistency warnings.
    """
    messages = []
    lines_info = get_line_info(pdf_path)
    # Identify potential headings
    headings = [line for line in lines_info if line['text'].isupper() and len(line['text']) > 2]
    if headings:
        sizes = [h['avg_size'] for h in headings]
        fonts = [h['font'] for h in headings]
        unique_sizes = set(round(s, 1) for s in sizes)
        unique_fonts = set(fonts)
        if len(unique_sizes) > 1:
            messages.append("Inconsistent font sizes among headings: " + ", ".join(str(s) for s in unique_sizes))
        if len(unique_fonts) > 1:
            messages.append("Inconsistent font families among headings: " + ", ".join(unique_fonts))
    else:
        messages.append("No headings identified to check consistency.")
    
    # Get vertical spacing details and extend the messages list
    spacing_info = check_spacing_consistency(pdf_path)
    messages.extend(spacing_info["messages"])
    
    return messages





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
