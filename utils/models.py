from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import os

# Add this to prevent tokenizer parallelism warnings
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Initialize BERT model with explicit device management
bert_model = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')  # or 'cuda' if you have GPU
bert_model.max_seq_length = 512  # Set explicit sequence length

def tfidf_similarity(text1, text2):
    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform([text1, text2])
    return cosine_similarity(vectors[0], vectors[1])[0][0]

def bert_similarity(text1, text2):
    try:
        embeddings = bert_model.encode(
            [text1, text2],
            convert_to_tensor=True,
            show_progress_bar=False
        )
        return cosine_similarity(embeddings[0].cpu().numpy().reshape(1, -1), 
                               embeddings[1].cpu().numpy().reshape(1, -1))[0][0]
    except Exception as e:
        print(f"BERT Error: {str(e)}")
        return 0.0