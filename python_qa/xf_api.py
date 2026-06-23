import requests
import hashlib
import hmac
import base64
import time
import os
import urllib.parse
import json
import websocket

from dotenv import load_dotenv

#读 .env 文件
load_dotenv()


class XunFeiChatDocAPI:
    def __init__(self):

        # 从本地环境变量中安全提取
        self.APP_ID = os.getenv("XF_APP_ID")
        self.API_SECRET = os.getenv("XF_API_SECRET")
        self.file_id = os.getenv("XF_FILE_ID")

    #动态安全鉴权
    def _get_auth_params(self):
        timestamp = str(int(time.time()))
        auth_str = self.APP_ID + timestamp
        auth = hashlib.md5(auth_str.encode('utf-8')).hexdigest()

        signature_bytes = hmac.new(
            self.API_SECRET.encode('utf-8'),
            auth.encode('utf-8'),
            hashlib.sha1
        ).digest()
        signature_base64 = base64.b64encode(signature_bytes).decode('utf-8')

        return {
            "appId": self.APP_ID,
            "timestamp": timestamp,
            "signature": signature_base64
        }

    def _convert_json_to_txt(self, json_path, txt_path):
        """
        将本地不合规的 json 自动化解构清洗为合规的纯文本 txt
        """
        try:
            with open(json_path, 'r', encoding='utf-8') as fj:
                data = json.load(fj)

            with open(txt_path, 'w', encoding='utf-8') as ft:
                ft.write("=== 教育领域问答系统 - Python核心知识库 ===\n\n")
                for item in data:
                    ft.write(f"问题: {item['question']}\n")
                    ft.write(f"答案: {item['answer']}\n")
                    ft.write("-" * 30 + "\n")
            print(f"【系统】数据清洗成功：{json_path} -> {txt_path}")
            return True
        except Exception as e:
            print(f"【系统】格式清洗转换失败: {str(e)}")
            return False

    def upload_knowledge_base(self, json_file_path='faq_dataset.json'):
        """
        【规范化上传接口】
        """
        url = "https://chatdoc.xfyun.cn/openapi/v1/file/upload"
        headers = self._get_auth_params()

        data = {
            "fileType": "wiki",
            "parseType": "AUTO"
        }
        txt_file_path = 'faq_dataset.txt'

        try:
            if not os.path.exists(json_file_path):
                print(f"【错误】未找到本地数据源: {json_file_path}")
                return False

            # 执行格式转换
            if not self._convert_json_to_txt(json_file_path, txt_file_path):
                return False

            with open(txt_file_path, 'rb') as f:
                files = {
                    "file": (os.path.basename(txt_file_path), f, "application/octet-stream")
                }
                print(f"【讯飞云】正在将清洗后的 {os.path.basename(txt_file_path)} 上传至科大讯飞控制台...")
                response = requests.post(url, headers=headers, data=data, files=files)

                if response.status_code != 200:
                    print(f"【讯飞云】网关拒绝 [{response.status_code}]: {response.text}")
                    return False

                result = response.json()
                if result.get("code") == 0:
                    self.file_id = result["data"]["fileId"]
                    print(f"【讯飞云】上传成功！新 FileID: {self.file_id}，请等待云端预处理。")
                    return True
                else:
                    print(f"【讯飞云】上传失败: {result.get('desc')}")
                    return False
        except Exception as e:
            print(f"【讯飞云】请求异常: {str(e)}")
            return False

    def ask_remote_ai(self, question):
        # 实时根据通过测试的算法生成凭证参数
        auth_params = self._get_auth_params()
        appId = auth_params["appId"]
        timestamp = auth_params["timestamp"]
        signature = urllib.parse.quote(auth_params["signature"])

        # 严格使用你提供的 URL 拼接模板
        url = f"wss://chatdoc.xfyun.cn/openapi/chat?appId={appId}&timestamp={timestamp}&signature={signature}"

        data = {
            "fileIds": [self.file_id],  # 绑定专属 FileID
            "messages": [
                {
                    "role": "user",
                    "content": question
                }
            ]
        }

        try:
            print("【讯飞云】正在基于通过验证的鉴权规则建立 WebSocket 连接...")
            ws = websocket.create_connection(url)
            ws.send(json.dumps(data))

            full_answer = ""
            while True:
                recv_data = ws.recv()
                res = json.loads(recv_data)

                if res.get("code") != 0:
                    ws.close()
                    return f"【讯飞云问答报错】: {res.get('message', '未知错误')}"

                content_piece = res.get("content", "")
                if content_piece:
                    full_answer += content_piece

                if res.get("status") == 2:
                    break

            ws.close()
            return full_answer

        except Exception as e:
            return f"【讯飞云连接异常】: {str(e)}"