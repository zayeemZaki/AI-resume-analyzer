# AI Resume Analyzer – README
An AI-powered tool that analyzes resumes and compares them with job descriptions using NLP techniques. It checks formatting, grammar, keyword relevance, and ATS compatibility.

---

## How to Run the Application

1. Clone the Repository:
      `git clone https://github.com/zayeemZaki/AI-resume-analyzer.git`
2. Set Up the Virtual Environment:
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
8. Run the Application
   `python app.py`
9. Then, click on the generated local address http://127.0.0.1:5000/, which will open the landing page of the web application in your browser.

#Notes
On first run, the app may download:
SpaCy models (en_core_web_lg, en_core_web_sm)
NLTK stopwords
LanguageTool grammar checker backend (~250MB)
Hugging Face tokenizer dependencies (e.g., protobuf)
All files are cached locally and won’t be re-downloaded in future runs.
