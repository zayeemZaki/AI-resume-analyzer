import pdfplumber
import re
from .models import bert_model  # not actively used, but kept for consistency

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
    Analyzes a PDF resume for:
     - overall font consistency
     - bullet usage
     - bullet line font/style consistency (NEW)
     - etc.

    Returns a dictionary with overall formatting statistics, plus bullet font consistency feedback
    in "bullet_font_consistency".
    """
    font_usage = set()
    bullet_count = 0
    total_lines = 0

    # For bullet font consistency checks (NEW)
    bullet_fonts = []
    bullet_sizes = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue

            # Count lines for bullet percentage
            lines = text.split("\n")
            total_lines += len(lines)

            # Count bullet lines (simple text-based detection)
            for line in lines:
                line_stripped = line.strip()
                if line_stripped.startswith(("•", "-", "*")):
                    bullet_count += 1

            # We also gather all per-character info to detect bullet line font usage
            chars = sorted(page.chars, key=lambda c: float(c['top']))

            # Group characters by line "top" value
            line_map = {}
            for c in chars:
                top_val = round(float(c['top']))
                line_map.setdefault(top_val, []).append(c)

            for top_val, char_list in line_map.items():
                # Sort by x0 to get correct reading order
                char_list.sort(key=lambda c: float(c['x0']))
                line_text = "".join(ch["text"] for ch in char_list).strip()

                # If text starts with bullet symbol, gather fonts/sizes (NEW)
                if line_text.startswith(("•", "-", "*")):
                    line_fonts = set()
                    line_sizes = set()
                    for ch in char_list:
                        raw_font = ch.get("fontname", "")
                        norm_font = normalize_font_name(raw_font)
                        if norm_font == "symbol":
                            continue
                        size = round(ch.get("size", 0), 1)
                        line_fonts.add(norm_font)
                        line_sizes.add(size)

                    # For simplicity, store the first font and size (or entire set)
                    # We'll do a simpler approach: pick any one from the set
                    if line_fonts and line_sizes:
                        bullet_fonts.append(list(line_fonts)[0])
                        bullet_sizes.append(list(line_sizes)[0])

            # Also track global font usage
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

    # NEW: Check bullet font/style consistency
    bullet_font_consistency_msg = check_bullet_font_consistency(bullet_fonts, bullet_sizes)

    return {
        "total_lines": total_lines,
        "bullet_count": bullet_count,
        "bullet_percentage": round(bullet_percentage, 2),
        "font_variations": len(font_usage),
        "unique_font_names": unique_font_names,
        "unique_font_sizes": unique_font_sizes,
        "all_fonts_and_sizes": list(font_usage),
        "bullet_font_consistency": bullet_font_consistency_msg  # NEW
    }

def check_bullet_font_consistency(bullet_fonts, bullet_sizes):
    """
    If bullet_fonts / bullet_sizes are not uniform, we generate warnings.
    If they're all the same, we say "All bullet lines share the same font and size."
    """
    if not bullet_fonts:
        return "No bullet lines detected or no font data for bullet lines."

    unique_fonts = set(bullet_fonts)
    unique_sizes = set(bullet_sizes)

    if len(unique_fonts) == 1 and len(unique_sizes) == 1:
        # Perfect consistency
        font = list(unique_fonts)[0]
        size = list(unique_sizes)[0]
        return f"All bullet lines share the same font '{font}' and size {size}."
    else:
        # Mismatch
        msgs = []
        if len(unique_fonts) > 1:
            msgs.append(f"Bullet lines use multiple fonts: {', '.join(unique_fonts)}.")
        if len(unique_sizes) > 1:
            msgs.append(f"Bullet lines use multiple font sizes: {', '.join(map(str, unique_sizes))}.")
        return " ".join(msgs)

# The rest of the file (for spacing, line info, etc.) remains unchanged
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
