import re
import spacy
import language_tool_python
from collections import defaultdict
from transformers import T5ForConditionalGeneration, T5Tokenizer

nlp = spacy.load("en_core_web_sm")
tool = language_tool_python.LanguageTool('en-US')

# Load T5 paraphrasing model
tokenizer = T5Tokenizer.from_pretrained("Vamsi/T5_Paraphrase_Paws", legacy=False)
model = T5ForConditionalGeneration.from_pretrained("Vamsi/T5_Paraphrase_Paws")

# Patterns to detect good resume bullet structure
ACCOMPLISHMENT_KEYWORDS = r"\b(developed|implemented|created|improved|achieved|designed|optimized)\b"
RESULT_KEYWORDS = r"\b(\d+%|\d+\s*(?:points|percent)|increased|decreased|improved|resulted|reduced)\b"
SKILLS_KEYWORDS = r"\b(using|with|by leveraging|utilized|employed|applied)\b"

def paraphrase_with_t5(text):
    prompt = (
        "Rewrite the following resume line to be professional, concise, and result-driven:\n\n"
        + text + " </s>"
    )
    encoding = tokenizer.encode_plus(
        prompt,
        max_length=256,
        padding="longest",
        return_tensors="pt",
        truncation=True
    )
    outputs = model.generate(
        input_ids=encoding["input_ids"],
        attention_mask=encoding["attention_mask"],
        max_length=256,
        num_beams=5,
        num_return_sequences=1,
        early_stopping=True
    )
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

def lacks_impact_structure(text):
    text = text.lower()
    return not (re.search(ACCOMPLISHMENT_KEYWORDS, text)
                and re.search(SKILLS_KEYWORDS, text)
                and re.search(RESULT_KEYWORDS, text))

def check_grammar_and_strength(text):
    doc = nlp(text)
    style_issues = []
    metrics = defaultdict(int)
    paragraph_suggestions = []

    for token in doc:
        if token.lower_ in {"i", "my", "me"}:
            metrics["first_person"] += 1

    for sent in doc.sents:
        if any(tok.dep_ == "nsubjpass" for tok in sent):
            metrics["passive_voice"] += 1

    meaningful_tokens = [token for token in doc if not token.is_stop and token.is_alpha]
    metrics["content_density"] = len(meaningful_tokens)

    if metrics["first_person"] > 0:
        style_issues.append(f"Avoid first-person pronouns (found {metrics['first_person']})")
    if metrics["passive_voice"] > 2:
        style_issues.append(f"Reduce passive voice (found {metrics['passive_voice']})")
    if metrics["content_density"] < 150:
        style_issues.append("Document seems sparse – add more achievements.")

    # Analyze each bullet line separately
    bullet_lines = text.split("\n")
    for idx, line in enumerate(bullet_lines, start=1):
        clean = line.strip()
        if not clean:
            continue

        matches = tool.check(clean)
        grammar_errors = []

        for match in matches:
            error_text = clean[match.offset: match.offset + match.errorLength]
            context_snippet = clean[max(0, match.offset - 30): match.offset + match.errorLength + 50].strip()

            grammar_errors.append({
                "error_text": error_text,
                "message": match.message,
                "suggestions": match.replacements,
                "context": context_snippet
            })

        improvement = None
        if lacks_impact_structure(clean):
            try:
                improved = paraphrase_with_t5(clean)
                if improved.strip().lower() != clean.strip().lower():
                    improvement = improved
            except Exception as e:
                print(f"[Paraphrasing failed]: {e}")

        paragraph_suggestions.append({
            "line_number": idx,
            "text": clean,
            "grammar_errors": grammar_errors,
            "paraphrased": improvement
        })

    return {
        "style_issues": style_issues,
        "line_analysis": paragraph_suggestions,
        "metrics": dict(metrics)
    }
