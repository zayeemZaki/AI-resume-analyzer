# AI Resume Analyzer

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-2.3.3-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An intelligent AI-powered resume analysis tool that leverages Natural Language Processing (NLP) to evaluate resumes against job descriptions. The application provides comprehensive insights including formatting analysis, grammar checking, keyword relevance scoring, and ATS (Applicant Tracking System) compatibility assessment.

## ✨ Features

- **Resume Parsing**: Supports PDF and DOCX file formats
- **ATS Compatibility Scoring**: Evaluates how well your resume matches ATS requirements
- **Keyword Analysis**: Compares resume content with job description keywords
- **Grammar & Style Checking**: Advanced grammar validation using LanguageTool
- **Formatting Analysis**: Assesses resume structure and formatting quality
- **Bullet Point Strength**: Analyzes the effectiveness of accomplishment statements
- **Skills Extraction**: Identifies and matches technical and soft skills

## 🛠️ Technology Stack

- **Backend Framework**: Flask
- **NLP Libraries**: 
  - spaCy (Language processing)
  - NLTK (Natural language toolkit)
  - Transformers (Hugging Face models)
- **Grammar Checking**: LanguageTool Python
- **Document Processing**: 
  - PDFPlumber (PDF parsing)
  - python-docx (DOCX parsing)
- **Data Processing**: Pandas, NumPy
- **Skills Recognition**: skillNer

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- **Python**: Version 3.8 or higher
- **Java**: Version 17 or higher (required for grammar checking)
  - Check your Java version: `java -version`
  - **Note**: The application will function without Java, but grammar checking features will be disabled

### Installing Java (if needed)

#### macOS
```bash
brew install openjdk@17
```

#### Windows
Download and install Java 17+ from [Adoptium](https://adoptium.net/)

#### Linux
```bash
sudo apt install openjdk-17-jdk
```

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/zayeemZaki/AI-resume-analyzer.git
cd AI-resume-analyzer
```

### 2. Create a Virtual Environment

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

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Download Required Language Models

```bash
python -m spacy download en_core_web_lg
python -m spacy download en_core_web_sm
```

## 💻 Usage

### Starting the Application

1. Ensure your virtual environment is activated
2. Run the Flask application:

```bash
python app.py
```

3. Open your web browser and navigate to:
```
http://127.0.0.1:5000/
```

4. Upload your resume (PDF or DOCX) and paste the job description to receive a comprehensive analysis

## 📁 Project Structure

```
AI-resume-analyzer/
├── app.py                      # Main Flask application
├── requirements.txt            # Python dependencies
├── utils/                      # Utility modules
│   ├── text_processing.py     # Text extraction and preprocessing
│   ├── formatting.py          # Resume formatting analysis
│   ├── keywords.py            # Keyword extraction
│   ├── enhanced_grammar_and_paraphrasing.py
│   └── models.py              # Model configurations
├── templates/                  # HTML templates
├── static/                     # Static assets (CSS, JS)
├── uploaded_resumes/          # Uploaded resume storage
└── resume_samples/            # Sample resumes for testing
```

## 📝 Notes

On the first run, the application will automatically download the following components:

- **SpaCy models** (`en_core_web_lg`, `en_core_web_sm`)
- **NLTK stopwords** dataset
- **LanguageTool** grammar checker backend (~250MB)
- **Hugging Face tokenizer** dependencies (e.g., protobuf)

All downloaded files are cached locally and will not be re-downloaded on subsequent runs.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👤 Author

**Zayeem Zaki**

- GitHub: [@zayeemZaki](https://github.com/zayeemZaki)

## 🙏 Acknowledgments

- Built with open-source NLP libraries and frameworks
- Utilizes state-of-the-art language models for analysis

---

**Note**: This tool is designed to assist in resume optimization. Always review suggestions carefully and maintain the authenticity of your resume content.
