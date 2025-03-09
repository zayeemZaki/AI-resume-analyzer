import pdfplumber
import re
from .models import bert_model  # kept for consistency, though not used here

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
    Extracts lines from the PDF along with their average font size, common font, vertical position,
    page number, and left margin (x-coordinate of the first character).
    Groups characters by similar y coordinates.
    """
    lines_info = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_number = page.page_number
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
                        left_margin = min(float(c.get('x0', 0)) for c in current_line)
                        lines_info.append({
                            'text': text,
                            'avg_size': avg_size,
                            'font': common_font,
                            'top': last_top,
                            'page': page_number,
                            'left': left_margin
                        })
                    current_line = [char]
                    last_top = top
            if current_line:
                text = ''.join(c['text'] for c in current_line).strip()
                sizes = [float(c['size']) for c in current_line]
                avg_size = sum(sizes) / len(sizes)
                fonts = [normalize_font_name(c['fontname']) for c in current_line]
                common_font = max(set(fonts), key=fonts.count)
                left_margin = min(float(c.get('x0', 0)) for c in current_line)
                lines_info.append({
                    'text': text,
                    'avg_size': avg_size,
                    'font': common_font,
                    'top': last_top,
                    'page': page_number,
                    'left': left_margin
                })
    return lines_info

def check_spacing_consistency_grouped(pdf_path, y_threshold=2, spacing_threshold=0.6, margin_threshold=5):
    """
    Groups lines by similar left margins (within margin_threshold) and checks vertical spacing
    consistency within each group.
    
    Returns detailed messages for each group.
    """
    from .grouping import extract_features  # in case needed
    lines_info = get_line_info(pdf_path, y_threshold)
    
    groups = {}
    for line in lines_info:
        left = line['left']
        found_group = None
        for key in groups.keys():
            if abs(key - left) <= margin_threshold:
                found_group = key
                break
        if found_group is not None:
            groups[found_group].append(line)
        else:
            groups[left] = [line]
    
    messages = []
    overall_spacings = []
    for group_left, group_lines in groups.items():
        if len(group_lines) < 2:
            messages.append(f"Not enough lines with left margin ~{group_left:.2f} to analyze spacing.")
            continue
        sorted_group = sorted(group_lines, key=lambda x: x['top'])
        spacings = [sorted_group[i+1]['top'] - sorted_group[i]['top'] for i in range(len(sorted_group)-1)]
        avg_spacing = sum(spacings) / len(spacings)
        min_spacing = min(spacings)
        max_spacing = max(spacings)
        overall_spacings.extend(spacings)
        spacing_range = max_spacing - min_spacing
        messages.append(
            f"Group with left margin ~{group_left:.2f}: Average spacing = {avg_spacing:.2f} points (min: {min_spacing:.2f}, max: {max_spacing:.2f})."
        )
        if spacing_range > (avg_spacing * spacing_threshold):
            messages.append(
                f"Group with left margin ~{group_left:.2f} shows significant spacing variation; consider standardizing spacing within this section."
            )
        else:
            messages.append(
                f"Group with left margin ~{group_left:.2f} spacing appears consistent."
            )
    if overall_spacings:
        overall_avg = sum(overall_spacings) / len(overall_spacings)
        messages.insert(0, f"Overall average spacing across groups: {overall_avg:.2f} points.")
    else:
        messages.insert(0, "No overall spacing data available.")
    
    return messages

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
        messages.append("The vertical spacing varies significantly; consider standardizing line spacing (e.g., use a consistent leading value).")
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
    Returns detailed consistency warnings including:
      - Specific headings (with page numbers and text) that deviate from the reference style.
      - Detailed spacing metrics for groups based on left margin.
    """
    messages = []
    lines_info = get_line_info(pdf_path)
    # Identify headings: lines that are all uppercase and longer than 2 characters
    headings = [line for line in lines_info if line['text'].isupper() and len(line['text']) > 2]
    if headings:
        font_counts = {}
        size_counts = {}
        for h in headings:
            font = h['font']
            size = round(h['avg_size'], 1)
            font_counts[font] = font_counts.get(font, 0) + 1
            size_counts[size] = size_counts.get(size, 0) + 1
        ref_font = max(font_counts, key=font_counts.get)
        ref_size = max(size_counts, key=size_counts.get)
        messages.append(f"Reference heading style: font '{ref_font}' at size {ref_size}.")
        for h in headings:
            current_size = round(h['avg_size'], 1)
            current_font = h['font']
            page = h.get('page', 'N/A')
            text = h['text']
            if current_font != ref_font or current_size != ref_size:
                messages.append(
                    f"Heading on page {page} - '{text}': font '{current_font}', size {current_size} deviates from reference; consider changing it to font '{ref_font}' at size {ref_size}."
                )
    else:
        messages.append("No headings identified to check consistency.")
    
    # Incorporate grouped spacing feedback
    spacing_messages = check_spacing_consistency_grouped(pdf_path)
    messages.extend(spacing_messages)
    
    return messages
