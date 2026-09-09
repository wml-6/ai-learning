import os
import json
import requests

API_KEY = os.environ["DEEPSEEK_API_KEY"]
URL = "https://api.deepseek.com/chat/completions"
GEO_URL = "https://geocoding-api.open-meteo.com/v1/search"
WX_URL = "https://api.open-meteo.com/v1/forecast"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36"}

WMO = {
    0: "晴", 1: "基本晴朗", 2: "局部多云", 3: "阴天",
    45: "雾", 48: "雾凇",
    51: "毛毛雨", 53: "毛毛雨", 55: "毛毛雨", 56: "冻毛毛雨", 57: "冻毛毛雨",
    61: "小雨", 63: "中雨", 65: "大雨", 66: "冻雨", 67: "冻雨",
    71: "小雪", 73: "中雪", 75: "大雪", 77: "米雪",
    80: "小阵雨", 81: "阵雨", 82: "强阵雨",
    85: "小阵雪", 86: "大阵雪",
    95: "雷阵雨", 96: "雷暴伴冰雹", 99: "雷暴伴冰雹",
}

def get_weather(city: str) -> str:
    try:
        r = requests.get(GEO_URL, headers=HEADERS, timeout=15, params={
            "name": city, "count": 1, "language": "zh", "format": "json"
        })
        results = r.json().get("results", [])
        if not results:
            return f"没有找到城市：{city}，请确认城市名写法"
        loc = results[0]
        place = f"{loc['name']} ({loc.get('country')}·{loc.get('admin1', '')})"

        r = requests.get(WX_URL, headers=HEADERS, timeout=15, params={
            "latitude": loc["latitude"], "longitude": loc["longitude"],
            "current": "temperature_2m,apparent_temperature,relative_humidity_2m,weather_code,wind_speed_10m",
            "timezone": "auto",
        })
        cur = r.json()['current']
        desc = WMO.get(cur["weather_code"], f"天气码{cur['weather_code']}")
        return (
            f"{place}当前：{desc}，"
            f"气温 {cur['temperature_2m']}°C，体感 {cur['apparent_temperature']}°C，"
            f"湿度 {cur['relative_humidity_2m']}%，风速 {cur['wind_speed_10m']} km/h"
        )
    except requests.RequestException as e:
        return f"查询失败（网络错误）：{e}"

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "查询某个城市的当前天气。当用户询问天气时必须使用它。",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "城市名，如：北京"
                    },
                },
                "required": ["city"],
            },
        },
    }
]

messages = [
    {
        "role": "system",
        "content": "你是天气助手。用户问天气时，必须调用 get_weather 拿到真实结果后再回答，禁止编造天气。"
    },
]

print("天气助手（输入 exit 退出）")
while True:
    user_input = input("\n你：").strip()
    if user_input in ("exit", "quit"):
        break
    messages.append({"role": "user", "content": user_input})
    
    for _ in range(5):
        resp = requests.post(
            URL,
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "deepseek-chat",
                "messages": messages,
                "tools": tools
            },
            timeout=60,
        )
        msg = resp.json()["choices"][0]["message"]

        if msg.get("tool_calls"):
            messages.append({
                "role": "assistant",
                "content": msg.get("content"),
                "tool_calls": msg["tool_calls"],
            })

            for tc in msg["tool_calls"]:
                fn = tc["function"]
                print(f"\n[模型申请] {fn['name']}({fn['arguments']})")
                args = json.loads(fn['arguments'])
                result = get_weather(args["city"])
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc["id"],
                    "content": result,
                })
            continue
        
        print("\nAI:", msg["content"])
        messages.append({
            "role": "assistant",
            "content": msg["content"]
        })
        break