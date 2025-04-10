import language_tool_python
import spacy
from transformers import T5ForConditionalGeneration, T5Tokenizer

# Load spaCy and grammar tool
nlp = spacy.load("en_core_web_sm")
tool = language_tool_python.LanguageTool('en-US')

# Load FLAN-T5 model and tokenizer
tokenizer = T5Tokenizer.from_pretrained("google/flan-t5-base", legacy=False)
model = T5ForConditionalGeneration.from_pretrained("google/flan-t5-base")

def paraphrase_with_flan(text):
    """
    Uses FLAN-T5 to rewrite bullet points with better grammar,
    highlighting action verbs, skills used, and quantifiable outcomes.
    Returns None if no meaningful improvement is generated.
    """
    # More specific, guiding prompt:
    prompt = (
        "Rewrite this bullet point with correct grammar, using an action verb, "
        "the skill or technology used, and a measurable result if applicable. "
        "Make sure it remains concise:\n\n"
        + text
    )

    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        padding=True,
        truncation=True,
        max_length=256
    )

    # Let T5 produce up to 3 paraphrase candidates
    outputs = model.generate(
        inputs.input_ids,
        max_length=256,
        num_beams=5,
        num_return_sequences=3,
        early_stopping=True
    )

    # We'll pick the first candidate that meaningfully changes the text
    for i in range(3):
        decoded = tokenizer.decode(outputs[i], skip_special_tokens=True).strip()

        # If it's basically the same line or includes the prompt text, skip it
        if (
            decoded
            and decoded.lower() != text.lower()
            and "rewrite this bullet" not in decoded.lower()
        ):
            return decoded

    return None

def check_grammar_and_strength(text_block):
    """
    Splits text_block by newlines, runs grammar checks, style checks,
    then attempts rewriting with FLAN-T5 for each bullet.
    """
    doc = nlp(text_block)
    style_issues = []
    metrics = {"first_person": 0, "passive_voice": 0, "content_density": 0}
    lines = [line.strip() for line in text_block.split("\n") if line.strip()]
    line_analysis = []

    for idx, line in enumerate(lines, start=1):
        # Ignore lines too short for meaningful analysis
        if len(line.split()) < 5:
            continue

        # Style checks (very basic)
        if any(word.lower() in {"i", "my", "me"} for word in line.split()):
            metrics["first_person"] += 1
        if ("was" in line or "were" in line) and "by" in line:
            metrics["passive_voice"] += 1

        # Grammar analysis with language_tool_python
        grammar_matches = tool.check(line)
        grammar_errors = [
            {"message": match.message, "rule": match.ruleId}
            for match in grammar_matches
        ]

        # Try paraphrasing
        try:
            improved = paraphrase_with_flan(line)
        except Exception as e:
            print(f"[Paraphrasing Error] Line {idx}: {e}")
            improved = None

        line_analysis.append({
            "line_number": idx,
            "text": line,
            "grammar_errors": grammar_errors,
            "paraphrased": improved
        })

    # Summarize style issues
    if metrics["first_person"] > 0:
        style_issues.append(f"Avoid first-person pronouns (found {metrics['first_person']})")
    if metrics["passive_voice"] > 2:
        style_issues.append(f"Reduce passive voice (found {metrics['passive_voice']})")
    if len(lines) < 10:
        style_issues.append("Resume may be too short – consider adding more accomplishments or projects.")

    return {
        "style_issues": style_issues,
        "line_analysis": line_analysis,
        "metrics": metrics
    }
