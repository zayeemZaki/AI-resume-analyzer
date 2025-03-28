from flask import Flask, request, jsonify, render_template
import os
import subprocess
import json
from pathlib import Path
from utils.text_processing import extract_text, preprocess_text, rank_resume
from utils.formatting import check_consistency
from utils.grouping import get_hybrid_grouping_analysis

app = Flask(__name__)
UPLOAD_FOLDER = "uploaded_resumes"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
CSHARP_CLI_PATH = Path("ResumeAnalyzerCLI/bin/Release/net9.0/ResumeAnalyzerCLI.dll")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def run_csharp(command, file_path):
    try:
        cli_path = str(CSHARP_CLI_PATH.absolute())
        file_path = str(file_path.absolute())
        
        result = subprocess.run(
            ["dotnet", cli_path, command, file_path],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=30
        )
        print("C# Output:", result.stdout)
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        print("C# Error:", e.stderr)
        return {"error": f"C# Error: {e.stderr}"}
    except Exception as e:
        print("General Error:", str(e))
        return {"error": f"Unexpected error: {str(e)}"}

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

    # Initialize analysis results
    analysis_results = {
        "csharp": {},
        "python": {
            "formatting": [],
            "grouping": []
        }
    }

    try:
        # C# Analysis
        analysis_results["csharp"]["parse"] = run_csharp("parse", resume_path)
        analysis_results["csharp"]["validate"] = run_csharp("validate", resume_path)
        analysis_results["csharp"]["grammar"] = run_csharp("grammar", resume_path)

        # Python Analysis
        resume_text = extract_text(resume_path)
        keyword_result = rank_resume(preprocess_text(resume_text), preprocess_text(job_desc))
        
        # Formatting and Grouping Analysis
        analysis_results["python"]["formatting"] = check_consistency(str(resume_path))
        _, group_messages = get_hybrid_grouping_analysis(str(resume_path))
        analysis_results["python"]["grouping"] = group_messages

    except Exception as e:
        return jsonify({"error": f"Analysis failed: {str(e)}"}), 500

    # Build response
    response = {
        "score": keyword_result.get("score", 0),
        "missing_keywords": keyword_result.get("missing_keywords", []),
        "sections": analysis_results["csharp"]["parse"].get("Sections", {}),
        "formatting_feedback": [
            *analysis_results["csharp"]["validate"].get("FormattingErrors", []),
            *analysis_results["python"]["formatting"],
            *analysis_results["python"]["grouping"]
        ],
        "grammar_issues": analysis_results["csharp"]["grammar"].get("GrammarIssues", []),
        "feedback": keyword_result.get("feedback", "No feedback available"),
        "errors": [
            err for err in [
                analysis_results["csharp"]["parse"].get("Error"),
                analysis_results["csharp"]["validate"].get("Error"),
                analysis_results["csharp"]["grammar"].get("Error")
            ] if err
        ]
    }

    # Debug logging
    print("C# Parse Result:", analysis_results["csharp"]["parse"])
    print("Python Formatting:", analysis_results["python"]["formatting"])
    print("Python Grouping:", analysis_results["python"]["grouping"])
    print("Keyword Result:", keyword_result)

    if any(response["errors"]):
        return jsonify({"error": "Analysis partial failure", "details": response}), 500

    return jsonify(response)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)