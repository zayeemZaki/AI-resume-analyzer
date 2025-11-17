# 🚀 AI Resume Analyzer

[![Python](https://img.shields.io/badge/Python-63.3%25-blue.svg)](https://www.python.org/)
[![JavaScript](https://img.shields.io/badge/JavaScript-17.7%25-yellow.svg)](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
[![CSS](https://img.shields.io/badge/CSS-14.7%25-purple.svg)](https://www.w3.org/Style/CSS/)
[![HTML](https://img.shields.io/badge/HTML-4.3%25-orange.svg)](https://html.spec.whatwg.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Flask](https://img.shields.io/badge/Flask-2.3.3-black.svg)](https://flask.palletsprojects.com/)

An intelligent, AI-powered resume analysis tool that helps job seekers optimize their resumes for Applicant Tracking Systems (ATS). This application uses advanced Natural Language Processing (NLP) techniques to analyze resume content, formatting, grammar, and keyword relevance against job descriptions.

## ✨ Key Features

- **🎯 ATS Compatibility Analysis**: Evaluate how well your resume passes through Applicant Tracking Systems
- **🔍 Keyword Matching**: Compare your resume against job descriptions to identify missing critical keywords
- **📊 Smart Scoring**: Get a comprehensive ATS compatibility score based on multiple factors
- **✍️ Grammar & Style Checking**: Identify grammatical errors and weak writing using LanguageTool and NLP
- **📄 Format Analysis**: Detect formatting issues including font consistency, bullet point usage, and document structure
- **💡 AI-Powered Suggestions**: Receive intelligent recommendations to strengthen your resume bullet points
- **📈 Detailed Metrics**: View comprehensive analytics including keyword density, formatting scores, and more
- **🔄 Multi-Format Support**: Upload resumes in PDF or DOCX format

## 🛠️ Tech Stack

### Backend
- **Python 3.x** - Core programming language
- **Flask 2.3.3** - Web framework for API endpoints
- **spaCy 3.7.2** - Advanced NLP library for text processing
- **NLTK 3.8.1** - Natural Language Toolkit for text analysis
- **Transformers 4.41.2** - Hugging Face library for BERT embeddings
- **PyTorch 2.1.0+** - Deep learning framework
- **LanguageTool Python 2.7.1** - Grammar and style checking
- **skillNer 1.0.3** - Skill extraction from text
- **pdfplumber 0.11.0** - PDF text extraction
- **python-docx 1.1.0** - DOCX file processing

### Frontend
- **HTML5** - Markup structure
- **CSS3** - Styling and responsive design
- **JavaScript (ES6+)** - Client-side interactivity
- **Fetch API** - Asynchronous HTTP requests

### Data Science & ML
- **pandas 2.2.2** - Data manipulation
- **numpy 1.26.4** - Numerical computing
- **scikit-learn** - Machine learning utilities (cosine similarity)
- **BERT** - Bidirectional Encoder Representations from Transformers for semantic analysis

## 📋 Prerequisites

- **Python 3.8+**
- **Java 17+** (Required for LanguageTool grammar checking)
- **pip** (Python package manager)

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/zayeemZaki/AI-resume-analyzer.git
cd AI-resume-analyzer
```

### 2. Check Java Installation (Required)

The grammar checking feature requires Java 17 or later. Check your Java version:

```bash
java -version
```

If Java is not installed or the version is below 17, install it:

**macOS (Homebrew):**
```bash
brew install openjdk@17
```

**Windows:**
Download Java 17+ from [Adoptium](https://adoptium.net/) and follow the installation guide.

**Linux (Ubuntu/Debian):**
```bash
sudo apt install openjdk-17-jdk
```

**Note:** Without Java 17+, the grammar checking feature will not work, but other features (keyword matching, ATS scoring, formatting analysis) will still function.

### 3. Set Up Virtual Environment

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

### 4. Install Python Dependencies

```bash
pip install -r requirements.txt
```

Or if you're using Python 3 explicitly:

```bash
pip3 install -r requirements.txt
```

### 5. Download Required NLP Models

```bash
python -m spacy download en_core_web_lg
python -m spacy download en_core_web_sm
```

### 6. Run the Application

```bash
python app.py
```

The application will start on `http://127.0.0.1:5001/`. Open this URL in your web browser.

## 📖 Usage Guide

### Analyzing a Resume

1. **Navigate to the Application**: Open `http://127.0.0.1:5001/` in your web browser

2. **Upload Your Resume**: 
   - Click on the file upload area
   - Select your resume file (PDF or DOCX format)

3. **Paste Job Description**:
   - Copy the job description from the job posting
   - Paste it into the text area provided

4. **Analyze**:
   - Click the "🔍 Analyze ATS Compatibility" button
   - Wait for the analysis to complete (usually 10-30 seconds)

5. **Review Results**:
   - **ATS Compatibility Score**: Overall score out of 100
   - **Missing Keywords**: Critical keywords from the job description not found in your resume
   - **Formatting Feedback**: Issues with font consistency, bullet points, etc.
   - **Grammar & Style Issues**: Grammatical errors and weak writing patterns
   - **Line-by-Line Analysis**: Detailed feedback on individual resume bullet points

### Example Analysis Output

```json
{
  "score": 75,
  "missing_keywords": ["Python", "Machine Learning", "Docker"],
  "formatting_feedback": [
    "Too many different fonts (5) - use 2-3 maximum.",
    "Low bullet usage (25%) - Increase to ~40% or more for clarity."
  ],
  "style_issues": [
    "Overuse of weak verbs like 'helped', 'worked'"
  ],
  "metrics": {
    "total_lines": 12,
    "strong_bullets": 8,
    "weak_bullets": 4
  }
}
```

## 📁 Project Structure

```
AI-resume-analyzer/
│
├── app.py                          # Main Flask application and API endpoints
├── requirements.txt                # Python dependencies
├── LICENSE                         # MIT License
├── README.md                       # Project documentation
│
├── utils/                          # Utility modules
│   ├── __init__.py
│   ├── text_processing.py         # Text extraction and preprocessing
│   ├── formatting.py               # PDF formatting analysis
│   ├── keywords.py                 # Keyword extraction and matching
│   ├── models.py                   # BERT model initialization
│   └── enhanced_grammar_and_paraphrasing.py  # Grammar checking
│
├── static/                         # Frontend static files
│   ├── style.css                   # Application styles
│   ├── script.js                   # Client-side JavaScript
│   └── generic_words.txt           # List of generic words to filter
│
├── templates/                      # HTML templates
│   └── index.html                  # Main application page
│
├── uploaded_resumes/               # Temporary storage for uploaded files
├── resume_samples/                 # Sample resumes for testing
├── skill_db_relax_20.json         # Skills database for keyword extraction
└── token_dist.json                 # Token distribution data for analysis
```

## 🔌 API Documentation

### Endpoint: `/analyze_resume`

**Method:** `POST`

**Content-Type:** `multipart/form-data`

**Parameters:**
- `resume` (file): Resume file in PDF or DOCX format
- `job_description` (string): Job description text for comparison

**Response:** JSON object containing:

```json
{
  "score": 85,                      // ATS compatibility score (0-100)
  "missing_keywords": [...],        // Array of missing keywords
  "formatting_feedback": [...],     // Array of formatting issues
  "feedback": "...",                // General feedback text
  "style_issues": [...],            // Array of writing style issues
  "line_analysis": [...],           // Detailed line-by-line analysis
  "metrics": {                      // Analysis metrics
    "total_lines": 15,
    "strong_bullets": 12,
    "weak_bullets": 3
  }
}
```

**Error Responses:**
- `400 Bad Request`: Missing resume file or job description
- `500 Internal Server Error`: Analysis processing error

### Example cURL Request

```bash
curl -X POST http://127.0.0.1:5001/analyze_resume \
  -F "resume=@/path/to/resume.pdf" \
  -F "job_description=Software Engineer position requiring Python, Flask, and NLP experience..."
```

## ⚙️ First Run Notes

On the first run, the application may download several dependencies:

- **SpaCy models** (`en_core_web_lg`, `en_core_web_sm`) - ~500MB
- **NLTK stopwords** - ~1MB
- **LanguageTool grammar checker backend** - ~250MB
- **Hugging Face tokenizer dependencies** (protobuf, etc.) - ~100MB

All files are cached locally and won't be re-downloaded in future runs.

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

### Reporting Issues

- Use the [GitHub Issues](https://github.com/zayeemZaki/AI-resume-analyzer/issues) page
- Check if the issue already exists before creating a new one
- Provide detailed information including:
  - Steps to reproduce
  - Expected vs actual behavior
  - Environment details (OS, Python version, etc.)

### Submitting Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Test thoroughly
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Code Style Guidelines

- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add comments for complex logic
- Update documentation for new features

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2025 Zayeem Zaki

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction...
```

## 👨‍💻 Author

**Zayeem Zaki**

- GitHub: [@zayeemZaki](https://github.com/zayeemZaki)
- Project Link: [https://github.com/zayeemZaki/AI-resume-analyzer](https://github.com/zayeemZaki/AI-resume-analyzer)

## 🙏 Acknowledgments

- [spaCy](https://spacy.io/) - Industrial-strength NLP library
- [Hugging Face Transformers](https://huggingface.co/transformers/) - State-of-the-art NLP models
- [LanguageTool](https://languagetool.org/) - Grammar and style checking
- [Flask](https://flask.palletsprojects.com/) - Lightweight web framework
- [skillNer](https://github.com/AnasAito/SkillNER) - Skill extraction library

## 📞 Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/zayeemZaki/AI-resume-analyzer/issues) page
2. Review the documentation above
3. Open a new issue with detailed information

---

<p align="center">Made with ❤️ by Zayeem Zaki</p>
<p align="center">⭐ Star this repository if you find it helpful!</p>
