# AI Resume Analyzer – README
An AI-powered tool that analyzes resumes and compares them with job descriptions using NLP techniques. It checks formatting, grammar, keyword relevance, and ATS compatibility.

---

## How to Run the Application

1. Clone the Repository:
      `git clone https://github.com/zayeemZaki/AI-resume-analyzer.git`
   
3. Set Up the Virtual Environment:
   ### for macOS/Linux
   `python3 -m venv venv`
   
   `source venv/bin/activate`
   
   ---
   ### for windows
   `python -m venv venv`
   
   `venv\Scripts\activate`
   
   ---
5. Install Dependencies
   
   `pip install -r requirements.txt` or
   
   `pip3 install -r requirements.txt`
7. Download Required Language Models
   
   `python -m spacy download en_core_web_lg`
   
   `python -m spacy download en_core_web_sm`
9. Run the Application

   `python app.py`
11. Then, click on the generated local address http://127.0.0.1:5000/, which will open the landing page of the web application in your browser.

Skip the steps below if you already have Java 17 or later installed.

#Important Note about Grammar Checking (Java 17 Requirement)
This application uses language_tool_python for grammar and writing analysis.
language_tool_python requires Java 17 or higher to be installed on the system.

You can check your Java version with:
 java -version

If you don't have Java installed, you can install it using:
- macOS (Homebrew):
 brew install openjdk@17
- Windows:
 Download Java 17+ from https://adoptium.net/ and follow the installer guides.
- Linux:
 sudo apt install openjdk-17-jdk

Without Java 17+, the grammar checking feature will not work, but other parts of the application (resume
keyword matching, ATS scoring, etc.) will still function.
---

---
#Notes
On first run, the app may download:
SpaCy models (en_core_web_lg, en_core_web_sm)
NLTK stopwords
LanguageTool grammar checker backend (~250MB)
Hugging Face tokenizer dependencies (e.g., protobuf)
All files are cached locally and won’t be re-downloaded in future runs.
