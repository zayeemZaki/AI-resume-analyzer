from flask import Flask, request, jsonify, render_template
import os
import subprocess
import json
from pathlib import Path
from utils.text_processing import extract_text, preprocess_text, rank_resume

app = Flask(__name__)
UPLOAD_FOLDER = "uploaded_resumes"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
CSHARP_CLI_PATH = Path("ResumeAnalyzerCLI/bin/Release/net9.0/ResumeAnalyzerCLI.dll")  # Fixed path

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def run_csharp(command, file_path):
    try:
        # Convert Path to string and use absolute path
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
        print("C# Output:", result.stdout)  # Debug logging
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        print("C# Error:", e.stderr)  # Debug logging
        return {"error": f"C# Error: {e.stderr}"}
    except Exception as e:
        print("General Error:", str(e))  # Debug logging
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

    # C# Analysis
    csharp_parse = run_csharp("parse", resume_path)
    csharp_validate = run_csharp("validate", resume_path)
    csharp_grammar = run_csharp("grammar", resume_path)

    # Python Analysis
    resume_text = extract_text(resume_path)
    keyword_result = rank_resume(preprocess_text(resume_text), preprocess_text(job_desc))

    # Build response
    response = {
        "score": keyword_result.get("score", 0),
        "missing_keywords": keyword_result.get("missing_keywords", []),
        "sections": csharp_parse.get("Sections", {}),  # Capital S
        "formatting_issues": csharp_validate.get("FormattingErrors", []),
        "grammar_issues": csharp_grammar.get("GrammarIssues", []),
        "keyword_feedback": keyword_result.get("feedback", []),
        "errors": [
            err for err in [
                csharp_parse.get("Error"),
                csharp_validate.get("Error"),
                csharp_grammar.get("Error")
            ] if err
        ]
    }
    
    # Add debug info
    print("C# Parse Result:", csharp_parse)
    print("Keyword Result:", keyword_result)


    if any(response["errors"]):
        return jsonify({"error": "Analysis partial failure", "details": response}), 500

    return jsonify(response)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)