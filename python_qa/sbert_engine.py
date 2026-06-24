import os
import joblib
import json
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"


class SBERTSearchEngine:
    def __init__(self, dataset_path='faq_dataset.json'):
        self.dataset_path = dataset_path
        self.kb_questions = []
        self.kb_answers = []
        self.sbert_matrix = joblib.load('data/sbert_matrix.pkl')

        print("正在从国内镜像源下载并加载 Sentence-BERT 模型...")

        self.model = SentenceTransformer('shibing624/text2vec-base-chinese')
        self._load_dataset()

    def _load_dataset(self):
        """读取本地 100 条知识库 JSON 文件"""
        with open(self.dataset_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for item in data:
                self.kb_questions.append(item['question'])
                self.kb_answers.append(item['answer'])

    def search(self, user_query):
        # 把用户的新问题翻译成 1 个 768 维的稠密向量
        query_vector = self.model.encode([user_query], normalize_embeddings=True)
        similarity_scores = cosine_similarity(query_vector, self.sbert_matrix)[0]

        best_match_idx = similarity_scores.argmax()
        best_score = similarity_scores[best_match_idx]

        # 拿着最高分索引，去 JSON 文本库里把真实的文字提出来
        actual_match_q = self.kb_questions[best_match_idx]
        actual_match_a = self.kb_answers[best_match_idx]

        return actual_match_q, actual_match_a, best_score