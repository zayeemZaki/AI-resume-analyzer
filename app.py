from flask import Flask, request, jsonify
import os
from utils.text_processing import extract_text, preprocess_text, rank_resume
from utils.formatting import analyze_pdf_formatting, check_consistency
from utils.grouping import get_hybrid_grouping_analysis
from utils.paraphrasing import always_paraphrase_description

app = Flask(__name__)
RESUME_DIR = "resume_samples"  # Directory where resume PDFs are stored

@app.route('/analyze_resume', methods=['POST'])
def analyze_resume():
    data = request.json
    resume_filename = data.get('resume_filename')
    job_desc = data.get('job_description')
    if not resume_filename or not job_desc:
        return jsonify({"error": "Missing resume filename or job description"}), 400

    resume_path = os.path.join(RESUME_DIR, resume_filename)
    if not os.path.exists(resume_path):
        return jsonify({"error": "Resume file not found"}), 404

    resume_text = extract_text(resume_path)
    if not resume_text:
        return jsonify({"error": "Could not extract text from resume"}), 500

    # Keyword Analysis
    resume_text_processed = preprocess_text(resume_text)
    job_desc_processed = preprocess_text(job_desc)
    keyword_result = rank_resume(resume_text_processed, job_desc_processed)

    # Formatting Analysis
    formatting_results = analyze_pdf_formatting(resume_path)
    formatting_messages = []
    if formatting_results["unique_font_names"] > 1:
        formatting_messages.append("Multiple font families detected; consider using a single font.")
    if formatting_results["unique_font_sizes"] > 2:
        formatting_messages.append("More than two font sizes used; keep it to 1-2 for consistency.")
    if formatting_results["bullet_percentage"] < 5:
        formatting_messages.append("Few or no bullet points detected; consider using bullets for clarity.")
    if not formatting_messages:
        formatting_messages.append("Overall formatting looks good!")
    
    consistency_messages = check_consistency(resume_path)
    formatting_messages.extend(consistency_messages)

    # Hybrid Grouping Analysis
    grouping_analysis, grouping_messages = get_hybrid_grouping_analysis(resume_path, num_clusters=3)

    # For each description in groups that likely contain project/experience text,
    # always generate a paraphrased suggestion.
    improved_descriptions = {}
    for group_label, details in grouping_analysis.items():
        if "Body Text" in group_label or "Sub-heading" in group_label:
            suggestions = []
            for line in details["lines"]:
                suggested = always_paraphrase_description(line["text"])
                suggestions.append({
                    "page": line["page"],
                    "original": line["text"],
                    "suggested": suggested
                })
            if suggestions:
                improved_descriptions[group_label] = suggestions

    response = {
        "score": keyword_result["score"],
        "feedback": keyword_result["feedback"],
        "missing_keywords": keyword_result["missing_keywords"],
        "formatting_analysis": formatting_results,
        "formatting_feedback": formatting_messages,
        "grouping_analysis": grouping_analysis,
        "grouping_feedback": grouping_messages,
        "improved_descriptions": improved_descriptions  # Suggestions for paraphrasing
    }
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
