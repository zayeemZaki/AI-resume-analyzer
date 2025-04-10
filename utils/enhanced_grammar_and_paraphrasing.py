import language_tool_python
import spacy
from transformers import T5ForConditionalGeneration, T5Tokenizer
import difflib  # ✅ We'll use this for highlighting changes

nlp = spacy.load("en_core_web_sm")
tool = language_tool_python.LanguageTool('en-US')

tokenizer = T5Tokenizer.from_pretrained("google/flan-t5-base", legacy=False)
model = T5ForConditionalGeneration.from_pretrained("google/flan-t5-base")


def highlight_changes(original, improved):
    """
    Compare original vs. improved text token by token,
    highlighting additions (green) and deletions (red).
    Return HTML snippet or None if no changes.
    """
    if not improved:
        return None
    # If they're basically the same, skip highlighting
    if original.strip().lower() == improved.strip().lower():
        return None

    diff = difflib.ndiff(original.split(), improved.split())
    highlighted_tokens = []
    for token in diff:
        code = token[0]  # '-', '+', or ' '
        word = token[2:]
        if code == ' ':
            # unchanged
            highlighted_tokens.append(word)
        elif code == '-':
            # deletion (in the original but not in improved)
            highlighted_tokens.append(f'<span style="background:#ffdce0;">{word}</span>')
        elif code == '+':
            # addition (in the improved text)
            highlighted_tokens.append(f'<span style="background:#d4fcbc;">{word}</span>')

    return ' '.join(highlighted_tokens)


def paraphrase_with_flan(text):
    prompt = (
        "Rewrite this bullet point with correct grammar, using an action verb, "
        "the skill/technology used, and a measurable outcome if possible. "
        "Keep it concise:\n\n" + text
    )

    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        padding=True,
        truncation=True,
        max_length=256
    )

    outputs = model.generate(
        inputs.input_ids,
        max_length=256,
        num_beams=5,
        num_return_sequences=3,
        early_stopping=True
    )

    for i in range(3):
        decoded = tokenizer.decode(outputs[i], skip_special_tokens=True).strip()
        # If the result is basically the same or includes the prompt, skip it
        if (
            decoded
            and decoded.lower() != text.lower()
            and "rewrite this bullet" not in decoded.lower()
        ):
            return decoded

    return None


def check_grammar_and_strength(text_block):
    doc = nlp(text_block)
    style_issues = []
    metrics = {"first_person": 0, "passive_voice": 0, "content_density": 0}
    lines = [line.strip() for line in text_block.split("\n") if line.strip()]
    line_analysis = []

    for idx, line in enumerate(lines, start=1):
        if len(line.split()) < 5:
            continue

        # simple style checks
        if any(word.lower() in {"i", "my", "me"} for word in line.split()):
            metrics["first_person"] += 1
        if ("was" in line or "were" in line) and "by" in line:
            metrics["passive_voice"] += 1

        # grammar
        grammar_matches = tool.check(line)
        grammar_errors = [
            {"message": match.message, "rule": match.ruleId}
            for match in grammar_matches
        ]

        # paraphrasing
        try:
            improved = paraphrase_with_flan(line)
        except Exception as e:
            print(f"[Paraphrasing Error] Line {idx}: {e}")
            improved = None

        # highlight changes if improved
        diff_html = None
        if improved:
            diff_html = highlight_changes(line, improved)

        line_analysis.append({
            "line_number": idx,
            "text": line,
            "grammar_errors": grammar_errors,
            "paraphrased": improved,
            "diff_html": diff_html  # <--- We'll show this in the frontend
        })

    if metrics["first_person"] > 0:
        style_issues.append(f"Avoid first-person pronouns (found {metrics['first_person']})")
    if metrics["passive_voice"] > 2:
        style_issues.append(f"Reduce passive voice (found {metrics['passive_voice']})")
    if len(lines) < 10:
        style_issues.append("Resume may be too short – consider adding more achievements.")

    return {
        "style_issues": style_issues,
        "line_analysis": line_analysis,
        "metrics": metrics
    }
