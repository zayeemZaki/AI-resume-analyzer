from flask import Flask, request, jsonify, render_template
import os
from utils.text_processing import extract_text, preprocess_text, rank_resume
from utils.formatting import analyze_pdf_formatting, check_consistency
from utils.grouping import get_hybrid_grouping_analysis
from utils.paraphrasing import always_paraphrase_description

app = Flask(__name__)
UPLOAD_FOLDER = "uploaded_resumes"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/analyze_resume", methods=["POST"])
def analyze_resume():
    if "resume" not in request.files:
        return jsonify({"error": "No resume file uploaded"}), 400

    resume_file = request.files["resume"]
    job_desc = request.form.get("job_description")

    if not job_desc:
        return jsonify({"error": "Job description is required"}), 400

    # Save the uploaded file
    resume_path = os.path.join(app.config["UPLOAD_FOLDER"], resume_file.filename)
    resume_file.save(resume_path)

    # Extract text
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

    response = {
        "score": keyword_result["score"],
        "feedback": keyword_result["feedback"],
        "missing_keywords": keyword_result["missing_keywords"],
        "formatting_feedback": formatting_messages,
    }
    return jsonify(response)

if __name__ == "__main__":
    app.run(debug=True)
