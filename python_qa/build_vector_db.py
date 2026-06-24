import json
import joblib
from sentence_transformers import SentenceTransformer

import os
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

model = SentenceTransformer('shibing624/text2vec-base-chinese')

with open('faq_dataset.json', 'r', encoding='utf-8') as f:
    qa_data = json.load(f)

questions = [item['question'] for item in qa_data]

# 编码
embeddings = model.encode(questions, normalize_embeddings=True)

# 存储
joblib.dump(embeddings, 'data/sbert_matrix.pkl')

