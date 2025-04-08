# app.py
from flask import Flask, request, jsonify, render_template
import os
from pathlib import Path
from utils.text_processing import extract_text, preprocess_text, rank_resume
from utils.formatting import check_consistency, analyze_pdf_formatting
from utils.grouping import get_hybrid_grouping_analysis
from utils.grammar import check_grammar
from utils.parsing import extract_resume_sections

app = Flask(__name__)
UPLOAD_FOLDER = "uploaded_resumes"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/analyze_resume", methods=["POST"])
def analyze_resume():
    if "resume" not in request.files:
        return jsonify({"error": "No resume uploaded"}), 400
    
    resume_file = request.files["resume"]
    job_desc = request.form.get("job_description", "")
    
    if not job_desc:
        return jsonify({"error": "Job description required"}), 400

    resume_path = Path(app.config["UPLOAD_FOLDER"]) / resume_file.filename
    resume_file.save(resume_path)

    try:
        # Extract and preprocess text
        raw_text = extract_text(resume_path)
        preprocessed_text = preprocess_text(raw_text)
        
        # Core analysis
        analysis_results = {
            "sections": extract_resume_sections(raw_text),
            "formatting": analyze_pdf_formatting(resume_path),
            "grammar": check_grammar(raw_text),
            "keyword_analysis": rank_resume(preprocessed_text, preprocess_text(job_desc)),
            "grouping_analysis": get_hybrid_grouping_analysis(str(resume_path))[1]
        }

        # Build response
        return jsonify({
            "score": analysis_results["keyword_analysis"].get("score", 0),
            "missing_keywords": analysis_results["keyword_analysis"].get("missing_keywords", []),
            "sections": analysis_results["sections"],
            "formatting_feedback": format_formatting_results(analysis_results["formatting"]),
            "grammar_issues": analysis_results["grammar"],
            "grouping_issues": analysis_results["grouping_analysis"],
            "feedback": analysis_results["keyword_analysis"].get("feedback", "No feedback available")
        })

    except Exception as e:
        return jsonify({"error": f"Analysis failed: {str(e)}"}), 500

def format_formatting_results(formatting_data):
    messages = []
    if formatting_data.get("unique_font_names", 0) > 3:
        messages.append(f"Too many fonts ({formatting_data['unique_font_names']}) - Use 2-3 maximum")
    if formatting_data.get("bullet_percentage", 0) < 30:
        messages.append("Low bullet point usage - Increase to ≥40% for better readability")
    return messages

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)