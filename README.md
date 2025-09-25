# AI Resume Analyzer

An **AI-powered web application** that evaluates resumes for **ATS (Applicant Tracking System) compatibility**.  
It uses **Natural Language Processing (NLP)** to compare resumes against job descriptions and provides feedback on:

- ✅ Keyword relevance and coverage
- ✅ Grammar and writing quality
- ✅ Formatting consistency
- ✅ Overall ATS score

---

## 🚀 Features
- Upload resumes in **PDF** or **DOCX** format
- Compare against any job description
- Keyword extraction using **SkillNER**
- Grammar checking powered by **LanguageTool** (Java backend)
- ATS scoring with **spaCy** and **transformers**
- Simple, responsive Flask-based web UI

---

## ⚙️ Requirements

- **Python 3.9 – 3.12**  
- **pip** (latest version recommended)  
- **Java 17+** (required only for grammar checking via LanguageTool)  

Check versions:
```bash
python --version
java -version