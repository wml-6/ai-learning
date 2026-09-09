import requests
from mcp.server.mcpserver import MCPServer

# 创建一个名为 weather 的 MCP server（stdio 传输是默认）
# v2 建议：name 用位置参数，其余(version 等)用关键字，避免参数顺序变化踩坑
mcp = MCPServer("weather", version="0.1.0")


@mcp.tool()
def get_weather(city: str) -> str:
    """查询指定城市的当前天气（气温、天气状况）。"""
    GEO = "https://geocoding-api.open-meteo.com/v1/search"
    WX = "https://api.open-meteo.com/v1/forecast"
    H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120"}
    try:
        loc = requests.get(GEO, headers=H, timeout=15,
                           params={"name": city, "count": 1, "language": "zh"}).json()["results"][0]
        cur = requests.get(WX, headers=H, timeout=15, params={
            "latitude": loc["latitude"], "longitude": loc["longitude"],
            "current": "temperature_2m,weather_code", "timezone": "auto",
        }).json()["current"]
        wmo = {0: "晴", 1: "基本晴朗", 2: "局部多云", 3: "阴天", 45: "雾", 61: "小雨", 63: "中雨", 80: "阵雨", 95: "雷阵雨"}
        return f"{loc['name']}：{wmo.get(cur['weather_code'], '未知')}，{cur['temperature_2m']}°C"
    except Exception as e:
        return f"天气查询失败：{e}"


@mcp.tool()
def add(a: float, b: float) -> float:
    """计算两个数相加。"""
    return a + b


if __name__ == "__main__":
    mcp.run()