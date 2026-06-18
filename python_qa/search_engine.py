import json
import jieba
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class TFIDFSearchEngine:
    def __init__(self, dataset_path='faq_dataset.json'):
        self.dataset_path = dataset_path
        self.kb_questions = []
        self.kb_answers = []

        # 修复点 1：修改 token_pattern，允许保留长度为 1 的中文单字
        # 修复点 2：加入基础的停用词表，屏蔽标点符号和无意义语气词，提升核心词权重
        self.vectorizer = TfidfVectorizer(
            token_pattern=r"(?u)\b\w+\b",
            # 添加更多无意义的疑问词汇
            stop_words=['的', '是', '在', '了', '呢', '啊', '吗', '？', '?', '！', '!', '，', ',', '。', '.', '用于',
                        '什么', '怎么', '如何', '个']
        )

        self.tfidf_matrix = None

        self._load_dataset()
        self._train_model()

    def _load_dataset(self):
        """读取本地知识库 JSON 文件"""
        try:
            with open(self.dataset_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for item in data:
                    self.kb_questions.append(item['question'])
                    self.kb_answers.append(item['answer'])
            print(f"【系统】成功加载知识库，共导入 {len(self.kb_questions)} 条问答数据。")
        except FileNotFoundError:
            print(f"【错误】找不到 {self.dataset_path} 文件，请先运行 make_data.py 生成数据！")

    def _tokenize(self, text):
        """使用 jieba 对中文文本进行分词，并用空格拼接（满足 sklearn 的输入要求）"""
        words = jieba.lcut(text)
        return " ".join(words)

    def _train_model(self):
        if not self.kb_questions:
            return
        tokenized_questions = [self._tokenize(q) for q in self.kb_questions]
        self.tfidf_matrix = self.vectorizer.fit_transform(tokenized_questions)

        # === 加入这两行，看透 TF-IDF 的底牌 ===
        print("【系统】TF-IDF 提取到的所有词汇字典：")
        print(self.vectorizer.get_feature_names_out())

        print("【系统】TF-IDF 模型初始化及矩阵构建完毕。")

    def search(self, user_query, threshold=0.45):
        """
        根据用户输入的问题进行检索，加入拒答兜底机制
        """
        tokenized_query = self._tokenize(user_query)
        query_vector = self.vectorizer.transform([tokenized_query])

        # 计算相似度并获取最高分
        similarity_scores = cosine_similarity(query_vector, self.tfidf_matrix)[0]
        best_match_idx = similarity_scores.argmax()
        best_score = similarity_scores[best_match_idx]

        # 获取底层真实匹配到的问题和答案
        actual_match_q = self.kb_questions[best_match_idx]
        actual_match_a = self.kb_answers[best_match_idx]

        # 核心逻辑：判断是否达到阈值 (TF-IDF)
        is_match = bool(best_score >= threshold)

        # 无论是否达标，都直接返回纯净的真实问题和答案，外加一个是否达标的布尔值
        return actual_match_q, actual_match_a, best_score, is_match

# ==========================================
# 测试代码：直接运行当前文件可测试效果
# ==========================================
if __name__ == "__main__":
    # 实例化检索引擎
    engine = TFIDFSearchEngine()

    print("\n--- 问答系统已启动（输入 'exit' 退出） ---")
    while True:
        user_input = input("\n请输入你的 Python 问题: ").strip()
        if user_input.lower() == 'exit':
            break
        if not user_input:
            continue

        match_q, answer, score = engine.search(user_input)

        print(f"[匹配度]: {score:.4f}")
        if match_q:
            print(f"[匹配原题]: {match_q}")
        print(f"[系统回答]: {answer}")