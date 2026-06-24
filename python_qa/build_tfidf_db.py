import json
import joblib
import jieba
from sklearn.feature_extraction.text import TfidfVectorizer


stop_words = [
    '的', '是', '在', '了', '呢', '啊', '吗', '么', '吧', '都', '就', '还', '又', '也', '很', '太', '更',
    '有', '和', '与', '及', '或', '而', '则', '乃', '之', '其', '此', '该', '各', '每', '某',
    '我', '你', '他', '她', '它', '我们', '你们', '他们', '这里', '那里', '这边', '那边',
    '什么', '怎么', '如何', '为何', '多少', '几', '谁', '哪', '哪里', '怎样',
    '用于', '可以', '能够', '需要', '应当', '应该', '必须', '可能', '大概', '也许',
    '不', '没', '无', '未', '别', '勿', '非', '否',
    '?', '？', '!', '！', '。', '，', ',', '.', '、', '；', '：', ':', '“', '”', '"', '‘', '’',
    '(', ')', '（', '）', '[', ']', '【', '】', '{', '}', '《', '》', '…', '—', '·', '～', '`',
    '请问', '问一下', '想问', '咨询', '请教', '麻烦', '帮忙', '请问一下', '我想问', '我想知道',
    '怎么弄', '怎么做', '怎么操作', '如何使用', '怎么解决', '怎么办', '有没有', '有没有办法',
    '介绍', '说明', '解释', '一下', '一点', '一些', '全部', '所有', '全部的',
    '多少', '多久', '多大', '多长', '多远', '多少钱', '为啥', '为什么'
]

with open('faq_dataset.json', 'r', encoding='utf-8') as f:
    qa_data = json.load(f)

# 分词函数
def tokenize(text):
    return " ".join(jieba.cut(text))
questions = [tokenize(item['question']) for item in qa_data]



# 初始化并“训练” TF-IDF 模型
vectorizer = TfidfVectorizer(
        token_pattern=r"(?u)\b\w+\b",
        stop_words=stop_words
    )
tfidf_matrix = vectorizer.fit_transform(questions)

joblib.dump(vectorizer, 'data/tfidf_model.pkl')
joblib.dump(tfidf_matrix, 'data/tfidf_matrix.pkl')
