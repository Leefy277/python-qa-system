# -*- coding: utf-8 -*-
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# 导入算法模块
from intent_classifier import IntentClassifier
from search_engine import TFIDFSearchEngine
from sbert_engine import SBERTSearchEngine
from xf_api import XunFeiChatDocAPI

app = FastAPI(title="Python智能问答系统 - 后端核心网关")

# 挂载跨域中间件，允许 Vue 前端跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局对象初始化（服务启动时加载一次）
print("【系统初始化】正在加载前置意图分类网关...")
classifier = IntentClassifier()

print("【系统初始化】正在构建本地词频矩阵（TF-IDF）...")
tfidf_engine = TFIDFSearchEngine()

print("【系统初始化】正在加载本地神经网络权重（Sentence-BERT）...")
sbert_engine = SBERTSearchEngine()

print("【系统初始化】正在挂载远端科大讯飞大厂对比引擎...")
xf_client = XunFeiChatDocAPI()

# 全局统一的温柔引导话术
UNIFIED_GUIDE_MSG = "你好呀！我是专业的 Python 编程小助手。我不太懂这个日常问题哦~ 请向我提问类似“如何反转列表”、“解释面向对象”等 Python 相关的知识吧！"


class QueryRequest(BaseModel):
    text: str
    mode: str = "tfidf"


# ===================================================
# 接口 1：单维问答路由（保留并兼容 chitchat 意图）
# ===================================================
@app.post("/api/chat")
async def chat(request: QueryRequest):
    user_input = request.text.strip()
    if not user_input:
        raise HTTPException(status_code=400, detail="提问内容不能为空")

    intent = classifier.classify(user_input)
    if intent in ["chitchat", "negation"]:
        return {
            "intent": intent,
            "match_question": None,
            "score": 1.0,
            "answer": classifier.get_preset_response(intent) if intent == "negation" else UNIFIED_GUIDE_MSG,
            "engine": "intent_classifier"
        }

        # 步骤 B：算法分流
    if request.mode == "sbert":
        match_q, answer, score, is_match = sbert_engine.search(user_input)  # <--- 这里加 is_match
        return {
            "intent": "query",
            "match_question": match_q if match_q else "没有在库中找到语义相近的题目",
            "score": round(float(score), 4),
            "answer": answer,
            "is_match": is_match,  # <--- 传给前端
            "engine": "sentence-bert"
        }
    else:
        match_q, answer, score, is_match = tfidf_engine.search(user_input)  # <--- 这里加 is_match
        return {
            "intent": "query",
            "match_question": match_q if match_q else "没有在库中找到字面匹配的题目",
            "score": round(float(score), 4),
            "answer": answer,
            "is_match": is_match,  # <--- 传给前端
            "engine": "tf-idf"
        }


# ===================================================
# 接口 2：质量对比路由（全面打通前两列数据流）
# ===================================================
@app.post("/api/compare")
async def compare_answers(request: QueryRequest):
    user_input = request.text.strip()
    if not user_input:
        raise HTTPException(status_code=400, detail="提问内容不能为空")

    print(f"【质量对比】收到全网联合对比指令，内容: '{user_input}'")

    # 步骤 A：意图网关拦截（精准拦截日常打招呼、闲聊或否定）
    intent = classifier.classify(user_input)
    if intent in ["chitchat", "negation"]:
        intent_name = "日常闲聊 / 打招呼 (Chitchat)" if intent == "chitchat" else "用户否定/不满意意图"
        return {
            "intent_type": "chat",
            "intent_name": intent_name,
            "intent_score": "1.00",
            "question": user_input,
            "tfidf_result": {
                "match_question": "未匹配到相关编程知识",
                "answer": UNIFIED_GUIDE_MSG if intent == "chitchat" else classifier.get_preset_response(intent),
                "score": 0.0
            },
            "local_system_answer_full": {
                "match_question": "未匹配到相关编程知识",
                "answer": UNIFIED_GUIDE_MSG if intent == "chitchat" else classifier.get_preset_response(intent),
                "score": 0.0
            },
            "xf_cloud_answer": UNIFIED_GUIDE_MSG if intent == "chitchat" else classifier.get_preset_response(intent)
        }

    # 步骤 B：执行底层算法搜索
    tfidf_match_q, tfidf_answer, tfidf_score, tfidf_is_match = tfidf_engine.search(user_input)
    sbert_match_q, sbert_answer, sbert_score, sbert_is_match = sbert_engine.search(user_input)

    # 步骤 C：OOD 领域外无关长句提问统一拦截（如：今天去哪里吃饭比较合适呢）
    OOD_THRESHOLD = 0.45
    if sbert_score < OOD_THRESHOLD:
        return {
            "intent_type": "chat",
            "intent_name": "领域外无关提问拦截 (OOD)",
            "intent_score": round(float(sbert_score), 4) if sbert_score else 0.0,
            "question": user_input,
            "tfidf_result": {
                "match_question": "未匹配到相关编程知识",
                "answer": UNIFIED_GUIDE_MSG,
                "score": round(float(tfidf_score), 4) if tfidf_score else 0
            },
            "local_system_answer_full": {
                "match_question": "未匹配到相关编程知识",
                "answer": UNIFIED_GUIDE_MSG,
                "score": round(float(sbert_score), 4) if sbert_score else 0
            },
            "xf_cloud_answer": UNIFIED_GUIDE_MSG
        }

    # 步骤 D：分数达标，说明是正统 Python 问题，正常请求云端大模型并返回
    xf_answer = xf_client.ask_remote_ai(user_input)

    # 正常返回结构化数据 (在 tfidf_result 和 local_system_answer_full 里面加上 is_match)
    return {
        "intent_type": "qa",
        "intent_name": "标准专业知识检索 (Q&A)",
        "intent_score": round(float(sbert_score), 4) if sbert_score else 0.94,
        "question": user_input,
        "tfidf_result": {
            "match_question": tfidf_match_q if tfidf_match_q else "未命中",
            "answer": tfidf_answer if tfidf_answer else "本地库未检索到",
            "score": round(float(tfidf_score), 4) if tfidf_score else 0,
            "is_match": tfidf_is_match  # <--- 这里
        },
        "local_system_answer_full": {
            "match_question": sbert_match_q if sbert_match_q else "未命中",
            "answer": sbert_answer if sbert_answer else "本地库未检索到",
            "score": round(float(sbert_score), 4) if sbert_score else 0,
            "is_match": sbert_is_match  # <--- 这里
        },
        "xf_cloud_answer": xf_answer
    }


#将 Vue 前端页面挂载到 Python 后端上
# 1. 挂载前端的静态资源目录
if os.path.exists("dist"):
    app.mount("/assets", StaticFiles(directory="dist/assets"), name="assets")

# 2. 捕捉所有不是 /api 开头的请求，统统返回 Vue 的主网页
@app.get("/{catchall:path}")
async def serve_vue_app(catchall: str):
    # 如果请求的是具体的静态文件（如 favicon），直接返回
    file_path = os.path.join("dist", catchall)
    if os.path.isfile(file_path):
        return FileResponse(file_path)

    # 否则，返回 Vue 的主页 index.html
    return FileResponse("dist/index.html")