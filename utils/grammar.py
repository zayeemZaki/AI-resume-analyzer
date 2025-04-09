import spacy
from collections import defaultdict
import language_tool_python

nlp = spacy.load("en_core_web_sm")
tool = language_tool_python.LanguageTool('en-US')

def check_grammar(text):
    doc = nlp(text)
    style_issues = []
    metrics = defaultdict(int)

    # --- Style checks ---
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

    # --- Grammar issues per paragraph ---
    lines_with_grammar_errors = []
    paragraphs = text.split("\n\n")

    for idx, para in enumerate(paragraphs, start=1):
        matches = tool.check(para)
        
        # print(f"\n[DEBUG] Paragraph {idx}:")
        # print(para)
        # print(f"[DEBUG] Matches found: {len(matches)}")

        if matches:
            errors = []
            for match in matches:
                error_text = para[match.offset : match.offset + match.errorLength]
                # print(f"  ✏️ {match.message} | Error: '{error_text}' | Suggestions: {match.replacements}")

                errors.append({
                    "error_text": error_text,
                    "message": match.message,
                    "suggestions": match.replacements
                })
            lines_with_grammar_errors.append({
                "line_number": idx,
                "text": para,
                "errors": errors
            })


    return {
        "style_issues": style_issues,
        "lines_with_grammar_errors": lines_with_grammar_errors,
        "metrics": dict(metrics)
    }
