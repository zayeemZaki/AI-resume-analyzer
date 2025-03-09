import numpy as np
from sklearn.cluster import KMeans
from .formatting import get_line_info

# Predefined set of common section headings (adjust as needed)
COMMON_SECTION_HEADINGS = {"EDUCATION", "EXPERIENCE", "PROJECTS", "SKILLS", "CERTIFICATIONS", "SUMMARY", "OBJECTIVE"}

def extract_features(lines):
    """
    Extracts features for each line.
    Features: average font size, left margin, uppercase flag, and text length.
    Returns a numpy array of feature vectors.
    """
    features = []
    for line in lines:
        font_size = float(line['avg_size'])
        left_margin = float(line['left'])
        uppercase_flag = 1.0 if line['text'].isupper() else 0.0
        text_length = float(len(line['text']))
        features.append([font_size, left_margin, uppercase_flag, text_length])
    return np.array(features)

def cluster_lines(lines, num_clusters=3):
    """
    Clusters the given lines using KMeans.
    Returns an array of cluster labels.
    """
    features = extract_features(lines)
    kmeans = KMeans(n_clusters=num_clusters, random_state=42)
    labels = kmeans.fit_predict(features)
    return labels

def label_clusters(labels, lines):
    """
    Uses simple heuristics on the cluster's average features to assign a human-readable label.
    Returns a dictionary mapping cluster indices to labels and a dictionary grouping the lines.
    """
    cluster_dict = {}
    for label, line in zip(labels, lines):
        cluster_dict.setdefault(label, []).append(line)
    
    cluster_labels = {}
    for label, group in cluster_dict.items():
        avg_font = np.mean([line['avg_size'] for line in group])
        avg_left = np.mean([line['left'] for line in group])
        uppercase_ratio = np.mean([1 if line['text'].isupper() else 0 for line in group])
        avg_length = np.mean([len(line['text']) for line in group])
        if uppercase_ratio > 0.8 and avg_length < 20:
            cluster_labels[label] = "Section Heading"
        elif avg_left > 50:
            cluster_labels[label] = "Sub-heading"
        else:
            cluster_labels[label] = "Body Text"
    return cluster_labels, cluster_dict

def get_hybrid_grouping_analysis(pdf_path, num_clusters=3, y_threshold=2, 
                                 font_deviation=0.2, margin_deviation=10, 
                                 min_font_diff=0.5, min_margin_diff=10,
                                 deviation_reporting_threshold=0.2):
    """
    Performs hybrid grouping analysis:
      1. Pre-classify lines that exactly match common section headings.
      2. Cluster the remaining lines using KMeans.
      3. For each group, compute average and standard deviation for font size and left margin.
         Then, count how many lines deviate beyond a given threshold (both relative and absolute).
         If more than deviation_reporting_threshold fraction of lines deviate,
         a summary message is generated.
    
    Returns:
      analysis: A dict mapping group labels to details.
      messages: A list of aggregated feedback messages.
    """
    lines_info = get_line_info(pdf_path, y_threshold)
    preclassified = []
    remaining = []
    for line in lines_info:
        if line['text'].strip().upper() in COMMON_SECTION_HEADINGS:
            preclassified.append(line)
        else:
            remaining.append(line)
    
    analysis = {}
    messages = []
    
    # Process preclassified section headings
    if preclassified:
        fonts = [line['avg_size'] for line in preclassified]
        lefts = [line['left'] for line in preclassified]
        avg_font = np.mean(fonts)
        avg_left = np.mean(lefts)
        std_font = np.std(fonts)
        std_left = np.std(lefts)
        analysis["Section Heading"] = {
            "num_lines": len(preclassified),
            "avg_font_size": round(float(avg_font), 2),
            "avg_left_margin": round(float(avg_left), 2),
            "lines": [
                {
                    "page": int(line['page']),
                    "text": line['text'],
                    "font_size": round(float(line['avg_size']), 2),
                    "left_margin": round(float(line['left']), 2)
                }
                for line in preclassified
            ]
        }
        font_deviations = sum(1 for line in preclassified 
                              if abs(line['avg_size'] - avg_font) > (avg_font * font_deviation) and abs(line['avg_size'] - avg_font) > min_font_diff)
        margin_deviations = sum(1 for line in preclassified 
                                if abs(line['left'] - avg_left) > margin_deviation and abs(line['left'] - avg_left) > min_margin_diff)
        fraction_font = font_deviations / len(preclassified)
        fraction_margin = margin_deviations / len(preclassified)
        if fraction_font > deviation_reporting_threshold:
            messages.append(f"{fraction_font*100:.0f}% of Section Headings deviate in font size from the average.")
        if fraction_margin > deviation_reporting_threshold:
            messages.append(f"{fraction_margin*100:.0f}% of Section Headings deviate in left margin from the average.")
    else:
        analysis["Section Heading"] = {"num_lines": 0}
    
    # Process remaining lines via clustering
    if remaining:
        labels = cluster_lines(remaining, num_clusters)
        cluster_labels, cluster_dict = label_clusters(labels, remaining)
        for cluster, group_lines in cluster_dict.items():
            label = cluster_labels[cluster]
            fonts = [line['avg_size'] for line in group_lines]
            lefts = [line['left'] for line in group_lines]
            avg_font = np.mean(fonts)
            avg_left = np.mean(lefts)
            std_font = np.std(fonts)
            std_left = np.std(lefts)
            group_key = f"{label} (Cluster {cluster})"
            analysis[group_key] = {
                "cluster_index": int(cluster),
                "num_lines": int(len(group_lines)),
                "avg_font_size": round(float(avg_font), 2),
                "avg_left_margin": round(float(avg_left), 2),
                "lines": [
                    {
                        "page": int(line['page']),
                        "text": line['text'],
                        "font_size": round(float(line['avg_size']), 2),
                        "left_margin": round(float(line['left']), 2)
                    }
                    for line in group_lines
                ]
            }
            font_deviations = sum(1 for line in group_lines 
                                  if abs(line['avg_size'] - avg_font) > (avg_font * font_deviation) and abs(line['avg_size'] - avg_font) > min_font_diff)
            margin_deviations = sum(1 for line in group_lines 
                                    if abs(line['left'] - avg_left) > margin_deviation and abs(line['left'] - avg_left) > min_margin_diff)
            fraction_font = font_deviations / len(group_lines)
            fraction_margin = margin_deviations / len(group_lines)
            if fraction_font > deviation_reporting_threshold:
                messages.append(f"In {label} (Cluster {cluster}), {fraction_font*100:.0f}% of lines deviate in font size from the group average.")
            if fraction_margin > deviation_reporting_threshold:
                messages.append(f"In {label} (Cluster {cluster}), {fraction_margin*100:.0f}% of lines deviate in left margin from the group average.")
    else:
        analysis["Other"] = {"num_lines": 0}
    
    return analysis, messages
