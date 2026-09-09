import os
import requests

API_KEY = os.environ.get("DEEPSEEK_API_KEY")
URL = "https://api.deepseek.com/chat/completions"

SYTSTEM_PROMPT = """你是一个严格但耐心的英语口语陪练。
规则：
1. 每次只回 1~2 句，不超过 30 个英文单词；
2. 先指出用户句子里的语法/用词问题（若有），再给出地道说法；
3. 全英文回复，不要用中文。
"""

history = [{"role": "system", "content": SYTSTEM_PROMPT}]

print("AI 英语陪练（输入 'exit' 退出）")
while True:
    user_input = input("\n你：").strip()
    if user_input in ("exit", "quit"):
        break
    history.append({"role": "user", "content": user_input})

    resp = requests.post(
        URL,
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": "deepseek-chat",
            "messages": history,
        },
        timeout=60,
    )
    data = resp.json()
    reply = data["choices"][0]["message"]["content"]
    print("\nAI:", reply)

    history.append({"role": "assistant", "content": reply})

    usage = data.get("usage", {})
    print(f"[本turn token: prompt {usage.get('prompt_tokens')} + completion {usage.get('completion_tokens')}]")
