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
classifier = IntentClassifier()

tfidf_engine = TFIDFSearchEngine()

sbert_engine = SBERTSearchEngine()

xf_client = XunFeiChatDocAPI()

# 全局统一的温柔引导话术
UNIFIED_GUIDE_MSG = "你好呀！我是专业的 Python 编程小助手。我不太懂这个日常问题哦~ 请向我提问类似“Python 是什么类型的语言”、“什么是集合”等 Python 相关的知识吧！"

class QueryRequest(BaseModel):
    text: str
    mode: str = "tfidf"

@app.post("/api/compare")
async def compare_answers(request: QueryRequest):
    user_input = request.text.strip()
    if not user_input:
        raise HTTPException(status_code=400, detail="提问内容不能为空")
    print(f"【质量对比】收到全网联合对比指令，内容: '{user_input}'")
    # 步骤 1：意图网关拦截（精准拦截日常打招呼、闲聊或否定）
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

    # 步骤 2：执行底层算法搜索
    tfidf_match_q, tfidf_answer, tfidf_score = tfidf_engine.search(user_input)
    sbert_match_q, sbert_answer, sbert_score= sbert_engine.search(user_input)

    # 步骤 3：OOD 领域外无关长句提问统一拦截（如：今天去哪里吃饭比较合适呢）
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

    # 步骤 4：分数>0.45，说明是正统 Python 问题，正常请求云端大模型并返回
    xf_answer = xf_client.ask_remote_ai(user_input)

    return {
        "intent_type": "qa",
        "intent_name": "标准专业知识检索 (Q&A)",
        "intent_score": round(float(sbert_score), 4) if sbert_score else 0.94,
        "question": user_input,
        "tfidf_result": {
            "match_question": tfidf_match_q if tfidf_match_q else "未命中",
            "answer": tfidf_answer if tfidf_answer else "本地库未检索到",
            "score": round(float(tfidf_score), 4) if tfidf_score else 0,
        },
        "local_system_answer_full": {
            "match_question": sbert_match_q if sbert_match_q else "未命中",
            "answer": sbert_answer if sbert_answer else "本地库未检索到",
            "score": round(float(sbert_score), 4) if sbert_score else 0,
        },
        "xf_cloud_answer": xf_answer
    }


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