import json
import jieba
import joblib
from sklearn.metrics.pairwise import cosine_similarity


class TFIDFSearchEngine:
    def __init__(self,
                 dataset_path='faq_dataset.json',
                 model_path='data/tfidf_model.pkl',
                 matrix_path='data/tfidf_matrix.pkl'):

        self.dataset_path = dataset_path
        self.kb_questions = []
        self.kb_answers = []
        self.vectorizer = joblib.load(model_path)
        self.tfidf_matrix = joblib.load(matrix_path)

        self._load_dataset()

    def _load_dataset(self):
        """读取本地知识库 JSON 文件"""
        try:
            with open(self.dataset_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for item in data:
                    self.kb_questions.append(item['question'])
                    self.kb_answers.append(item['answer'])

        except FileNotFoundError:
            print(f"【错误】找不到 {self.dataset_path} 文件！")

    def _tokenize(self, text):
        words = jieba.lcut(text)
        return " ".join(words)

    def search(self, user_query):
        """根据用户输入的问题进行极速检索"""
        tokenized_query = self._tokenize(user_query)

        # 加载的 vectorizer 把切好的词变成稀疏向量
        query_vector = self.vectorizer.transform([tokenized_query])

        # 和加载的 tfidf_matrix 进行极速余弦相似度比对
        similarity_scores = cosine_similarity(query_vector, self.tfidf_matrix)[0]

        best_match_idx = similarity_scores.argmax()
        best_score = similarity_scores[best_match_idx]

        # 提取答案
        actual_match_q = self.kb_questions[best_match_idx]
        actual_match_a = self.kb_answers[best_match_idx]

        return actual_match_q, actual_match_a, best_score