from flask import Flask, request, jsonify
import os
from utils import extract_text, preprocess_text, rank_resume, analyze_pdf_formatting, check_consistency

app = Flask(__name__)

RESUME_DIR = "resume_samples"  # Directory to store resumes

@app.route('/analyze_resume', methods=['POST'])
def analyze_resume():
    """
    Analyze a resume against a job description by performing:
    1. Keyword and similarity analysis.
    2. Overall formatting analysis.
    3. Consistency checks (including headings and vertical spacing).
    Returns a combined JSON response with detailed feedback.
    """
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

    # Preprocess texts for keyword analysis
    resume_text_processed = preprocess_text(resume_text)
    job_desc_processed = preprocess_text(job_desc)
    keyword_result = rank_resume(resume_text_processed, job_desc_processed)

    # Overall formatting analysis
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
    
    # Detailed consistency checks (headings and vertical spacing)
    consistency_messages = check_consistency(resume_path)
    formatting_messages.extend(consistency_messages)

    response = {
        "score": keyword_result["score"],
        "feedback": keyword_result["feedback"],
        "missing_keywords": keyword_result["missing_keywords"],
        "formatting_analysis": formatting_results,
        "formatting_feedback": formatting_messages
    }

    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
