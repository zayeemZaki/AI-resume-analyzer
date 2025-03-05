from flask import Flask, request, jsonify
import os
from utils import extract_text, preprocess_text, rank_resume

app = Flask(__name__)

RESUME_DIR = "resume_samples"  # Directory to store resumes

@app.route('/analyze_resume', methods=['POST'])
def analyze_resume():
    """Analyze a PDF resume from /resume_samples and compare it to a pasted job description."""
    data = request.json
    resume_filename = data.get('resume_filename')  # Resume filename (must be inside resume_samples)
    job_desc = data.get('job_description')

    if not resume_filename or not job_desc:
        return jsonify({"error": "Missing resume filename or job description"}), 400

    resume_path = os.path.join(RESUME_DIR, resume_filename)

    if not os.path.exists(resume_path):
        return jsonify({"error": "Resume file not found"}), 404

    # Extract text from resume PDF
    resume_text = extract_text(resume_path)

    if not resume_text:
        return jsonify({"error": "Could not extract text from resume"}), 500

    # Preprocess texts
    resume_text = preprocess_text(resume_text)
    job_desc = preprocess_text(job_desc)

    # Get ranking
    result = rank_resume(resume_text, job_desc)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
