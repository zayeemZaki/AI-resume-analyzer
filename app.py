from flask import Flask, request, jsonify, render_template
import os
import re
from pathlib import Path
from utils.text_processing import extract_text, preprocess_text, rank_resume
from utils.formatting import check_consistency, analyze_pdf_formatting
from utils.grouping import get_hybrid_grouping_analysis
from utils.grammar import check_grammar
from utils.parsing import extract_resume_sections
from utils.paraphrasing import always_paraphrase_description

app = Flask(__name__)
UPLOAD_FOLDER = "uploaded_resumes"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ACCOMPLISHMENT_KEYWORDS = r"\b(developed|implemented|created|improved|achieved|designed|optimized)\b"
RESULT_KEYWORDS = r"\b(\d+%|\d+\s*(?:points|percent)|increased|decreased|improved|resulted|reduced)\b"

@app.route("/")
def index():
    return render_template("index.html")

def is_experience_bullet(text):
    text_lower = text.lower()
    return (re.search(ACCOMPLISHMENT_KEYWORDS, text_lower) 
            and re.search(RESULT_KEYWORDS, text_lower)
            and len(text.split()) >= 5)

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
        # Step 1: Extract text with line breaks preserved
        raw_text = extract_text(resume_path)

        # Step 2: Group bullet lines into paragraphs for grammar context
        grouped_lines = []
        current_para = []

        lines = raw_text.splitlines()

        for line in lines:
            stripped = line.strip()
            
            # Skip empty lines
            if not stripped:
                if current_para:
                    grouped_lines.append(" ".join(current_para))
                    current_para = []
                continue

            # Detect resume section headers (like EDUCATION, EXPERIENCE)
            if stripped.isupper() and len(stripped.split()) <= 4:
                if current_para:
                    grouped_lines.append(" ".join(current_para))
                    current_para = []
                grouped_lines.append(stripped)
                continue

            # If line looks like contact info, break it into its own
            if "@" in stripped or "|" in stripped or stripped.lower().startswith("zayeem"):
                if current_para:
                    grouped_lines.append(" ".join(current_para))
                    current_para = []
                grouped_lines.append(stripped)
                continue

            current_para.append(stripped)

        if current_para:
            grouped_lines.append(" ".join(current_para))

        grouped_text = "\n\n".join(grouped_lines)



        preprocessed_text = preprocess_text(grouped_text)
        

        # Export grouped_text to a .txt file for debugging
        debug_path = Path(app.config["UPLOAD_FOLDER"]) / "grouped_output_debug.txt"
        with open(debug_path, "w", encoding="utf-8") as f:
            f.write(grouped_text)
        print(f"[DEBUG] Grouped text written to {debug_path}")


        # Step 3: Analyze
        sections = extract_resume_sections(raw_text)
        analysis_results = {
            "sections": sections,
            "formatting": analyze_pdf_formatting(resume_path),
            "grammar": check_grammar(grouped_text),
            "keyword_analysis": rank_resume(preprocessed_text, preprocess_text(job_desc)),
            "grouping_analysis": get_hybrid_grouping_analysis(str(resume_path))[1]
        }

        paraphrased_suggestions = []
        try:
            all_bullets = [bullet for section in sections.values() for bullet in section]
            for bullet in all_bullets[:5]:
                if is_experience_bullet(bullet):
                    try:
                        paraphrased = always_paraphrase_description(bullet)
                        paraphrased_suggestions.append({
                            "original": bullet,
                            "suggestion": paraphrased
                        })
                    except Exception as e:
                        print(f"Paraphrasing failed for bullet: {bullet}\nError: {str(e)}")
        except Exception as e:
            print(f"Paraphrasing process failed: {str(e)}")

        # print("Printing Grammmamrmmagnagiaehgiuaehpgae", analysis_results["grammar"])

        return jsonify({
            "score": analysis_results["keyword_analysis"].get("score", 0),
            "missing_keywords": analysis_results["keyword_analysis"].get("missing_keywords", []),
            "sections": analysis_results["sections"],
            "formatting_feedback": format_formatting_results(analysis_results["formatting"]),
            "grammar_issues": analysis_results["grammar"],
            "grouping_issues": analysis_results["grouping_analysis"],
            "feedback": analysis_results["keyword_analysis"].get("feedback", "No feedback available"),
            "paraphrased_suggestions": paraphrased_suggestions
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
    print("Loading ML models...")
    app.run(host="0.0.0.0", port=5001, debug=True)
