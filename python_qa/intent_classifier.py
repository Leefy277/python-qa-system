# -*- coding: utf-8 -*-
import jieba


class IntentClassifier:
    def __init__(self):
        # 1. 扩充：问候与日常闲聊特征词库 (全面覆盖天气、吃饭、身份等日常话题)
        self.chitchat_words = {
            # 基础问候
            '你好', '嗨', '在吗', 'hello', 'hi', '早上好', '下午好', '晚上好',
            # 闲聊：天气与生活
            '天气', '下雨', '晴天', '温度', '冷', '热',
            '吃饭', '饿', '美食', '吃什么', '食堂', '外卖', '饭点',
            # 闲聊：身份与娱乐
            '名字', '你是谁', '叫什么', '几岁', '多大', '机器人', '小助手',
            '无聊', '讲个笑话', '聊天', '干嘛呢', '再见', '拜拜', '笨蛋', '傻'
        }

        # 2. 否定/不满意特征词库
        self.negation_words = {'不对', '不是', '没有', '写错了', '不行', '错误', '回答错误', '不对啊', '不正确'}

        # 3. 针对非查询意图的固定回复（保留作为底层兜底）
        self.responses = {
            "chitchat": "你好呀！我是专业的 Python 编程小助手。我不太懂这个日常问题哦~ 请向我提问类似“如何反转列表”、“解释面向对象”等 Python 相关的知识吧！",
            "negation": "非常抱歉没能准确理解您的意思。您可以尝试换一种更具体的代码描述再问我一次哦！"
        }

    def classify(self, text):
        """
        核心网关：判断用户的输入意图
        """
        clean_text = text.lower().strip()

        # 1. 优先检查是否包含闲聊/问候词汇
        for word in self.chitchat_words:
            if word in clean_text:
                return "chitchat"

        # 2. 检查是否包含否定词
        for word in self.negation_words:
            if word in clean_text:
                return "negation"

        # 3. 默认属于正常的知识查询
        return "query"

    def get_preset_response(self, intent):
        """获取预设意图的固定回复"""
        return self.responses.get(intent, None)


# ==========================================
# 独立测试
# ==========================================
if __name__ == "__main__":
    classifier = IntentClassifier()
    print("--- 开始测试【意图分类】模块 ---")
    test_inputs = ["今天天气怎么样", "去哪里吃饭", "不对，你回答得不正确", "Python怎么定义列表？"]

    for text in test_inputs:
        print(f"输入: '{text}' -> 识别意图: {classifier.classify(text)}")