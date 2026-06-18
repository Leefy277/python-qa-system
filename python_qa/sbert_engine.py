import os

# 【核心解决代码】强制让 Hugging Face 使用国内镜像源下载模型，速度飞快且不卡网
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

import json
from sentence_transformers import SentenceTransformer, util


class SBERTSearchEngine:
    def __init__(self, dataset_path='faq_dataset.json'):
        self.dataset_path = dataset_path
        self.kb_questions = []
        self.kb_answers = []

        print("【系统】正在从国内镜像源下载并加载 Sentence-BERT 模型...")
        # 修正为镜像源中绝对存在的标准中文语义模型（约300MB）
        self.model = SentenceTransformer('shibing624/text2vec-base-chinese')

        self.kb_embeddings = None
        self._load_dataset()
        self._encode_knowledge_base()

    def _load_dataset(self):
        """读取本地 100 条知识库 JSON 文件"""
        with open(self.dataset_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for item in data:
                self.kb_questions.append(item['question'])
                self.kb_answers.append(item['answer'])
        print(f"【系统】成功加载知识库共 {len(self.kb_questions)} 条数据。")

    def _encode_knowledge_base(self):
        """预先将知识库中所有的问题全部转化为高维语义向量（Embedding）"""
        print("【系统】正在将知识库问题转化为语义向量...")
        self.kb_embeddings = self.model.encode(self.kb_questions, convert_to_tensor=True)
        print("【系统】知识库向量化完毕！")

    def search(self, user_query, threshold=0.85):  # 建议把默认阈值调高到0.85
        """根据用户输入的问题进行语义检索，并加入兜底展示逻辑"""
        query_embedding = self.model.encode(user_query, convert_to_tensor=True)
        cos_scores = util.cos_sim(query_embedding, self.kb_embeddings)[0]

        best_match_idx = cos_scores.argmax().item()
        best_score = cos_scores[best_match_idx].item()

        # 提取出底层真实匹配到的那道题和对应的答案
        actual_match_q = self.kb_questions[best_match_idx]
        actual_match_a = self.kb_answers[best_match_idx]

        # 核心逻辑：判断是否达到阈值 (SBERT)
        is_match = bool(best_score >= threshold)

        # 直接返回纯净文本和状态标识，不加任何前缀
        return actual_match_q, actual_match_a, best_score, is_match

# ==========================================
# 独立测试
# ==========================================
if __name__ == "__main__":
    engine = SBERTSearchEngine()

    print("\n--- 开始测试【Sentence-BERT 语义检索】 ---")
    test_query = "如何把一个列表弄成反过来的顺序？"

    match_q, answer, score = engine.search(test_query)

    print(f"\n用户提问: '{test_query}'")
    print(f"语义相似度得分: {score:.4f}")
    print(f"匹配到的知识库原题: {match_q}")
    print(f"系统给出的答案: {answer}")