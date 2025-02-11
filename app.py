from flask import Flask, request, jsonify
from utils import extract_text, preprocess_text, rank_resume

app = Flask(__name__)

@app.route('/analyze_resume', methods=['POST'])
def analyze_resume():
    """Analyze resume and compare it to job description."""
    data = request.json
    resume_text = preprocess_text(data['resume_text'])
    job_desc = preprocess_text(data['job_description'])
    result = rank_resume(resume_text, job_desc)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
