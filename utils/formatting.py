import pdfplumber
import re
from .models import bert_model  # (if needed for further processing; otherwise, this file focuses on PDF data)
# No spaCy needed here

def normalize_font_name(font_name):
    """
    Normalize font names by removing common style indicators (Bold, Italic, Regular, MT)
    and hyphens/underscores so that fonts from the same family are treated identically.
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
    Checks vertical spacing between consecutive lines.
    Returns average, minimum, maximum spacing and feedback messages.
    """
    lines_info = get_line_info(pdf_path, y_threshold)
    if len(lines_info) < 2:
        return {
            "avg_spacing": None,
            "min_spacing": None,
            "max_spacing": None,
            "messages": ["Not enough lines to analyze vertical spacing."]
        }
    sorted_lines = sorted(lines_info, key=lambda x: x['top'])
    spacings = [sorted_lines[i+1]['top'] - sorted_lines[i]['top'] for i in range(len(sorted_lines)-1)]
    avg_spacing = sum(spacings) / len(spacings)
    min_spacing = min(spacings)
    max_spacing = max(spacings)
    spacing_range = max_spacing - min_spacing

    messages = []
    messages.append(f"Average vertical spacing is {avg_spacing:.2f} points (min: {min_spacing:.2f}, max: {max_spacing:.2f}).")
    if spacing_range > (avg_spacing * 0.5):
        messages.append("The vertical spacing varies significantly; consider standardizing line spacing for consistency.")
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
    Checks for consistency in headings (heuristically, uppercase lines) and vertical spacing.
    Returns detailed consistency warnings.
    """
    messages = []
    lines_info = get_line_info(pdf_path)
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
    
    spacing_info = check_spacing_consistency(pdf_path)
    messages.extend(spacing_info["messages"])
    
    return messages
