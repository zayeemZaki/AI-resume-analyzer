import re
from transformers import T5ForConditionalGeneration, T5Tokenizer

# Load the tokenizer and model (this may take a moment on first run)
tokenizer = T5Tokenizer.from_pretrained("Vamsi/T5_Paraphrase_Paws")
model = T5ForConditionalGeneration.from_pretrained("Vamsi/T5_Paraphrase_Paws")

# Define regex patterns for checking description structure (if needed)
ACCOMPLISHMENT_KEYWORDS = r"\b(developed|implemented|created|improved|achieved|designed|optimized)\b"
RESULT_KEYWORDS = r"\b(\d+%|\d+\s*(?:points|percent)|increased|decreased|improved|resulted|reduced)\b"
SKILLS_KEYWORDS = r"\b(using|with|by leveraging|utilized|employed|applied)\b"

def paraphrase_description(text, num_beams=5, num_return_sequences=1):
    """
    Uses a pretrained T5 paraphrasing model to generate a paraphrased version of the text.
    """
    input_text = "paraphrase: " + text + " </s>"
    encoding = tokenizer.encode_plus(input_text, max_length=256, padding="longest", return_tensors="pt", truncation=True)
    input_ids = encoding["input_ids"]
    attention_mask = encoding["attention_mask"]
    outputs = model.generate(
        input_ids=input_ids, 
        attention_mask=attention_mask,
        max_length=256, 
        num_beams=num_beams, 
        num_return_sequences=num_return_sequences, 
        early_stopping=True
    )
    paraphrased = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return paraphrased

def always_paraphrase_description(text, num_beams=5, num_return_sequences=1):
    """
    Always returns a paraphrased version of the input text that emphasizes:
      (X) What was accomplished,
      (Y) Qualitative results, and
      (Z) The skills used.
    
    This function does not modify the resume; it only returns a suggestion.
    """
    prompt = ("Rewrite the following description so that it clearly states what was accomplished, "
              "the qualitative results, and the skills or experience used to achieve the outcome:\n\n" + text)
    return paraphrase_description(prompt, num_beams=num_beams, num_return_sequences=num_return_sequences)
