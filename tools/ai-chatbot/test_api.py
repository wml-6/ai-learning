import os
import requests

API_KEY = os.environ.get("DEEPSEEK_API_KEY")
resp = requests.post(
    "https://api.deepseek.com/chat/completions",
    headers={
        "Authorization":f"Bearer {API_KEY}",
        "Content-Type":"application/json",
    },
    json={
        "model": "deepseek-chat",
        "messages": [
            {
                "role": "user",
                "content": "你好，请用一句话介绍你自己"
            }
        ],
    },
    timeout=60,
)

print("HTTP 状态码：", resp.status_code)
print("原始响应 JSON：")
print(resp.json())