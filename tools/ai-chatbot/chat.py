import os
import requests

API_KEY = os.environ.get("DEEPSEEK_API_KEY")
URL = "https://api.deepseek.com/chat/completions"

history = []

print("欢迎使用 DeepSeek ChatBot！输入 'exit' 退出。")
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
