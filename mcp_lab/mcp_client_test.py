import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVER = "/home/wml/ai-learning/mcp_lab/weather_mcp_server.py"
PY = "/home/wml/miniconda3/envs/py312/bin/python"


async def main():
    # Client 把 Server 当子进程启动，走 stdio
    params = StdioServerParameters(command=PY, args=[SERVER])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()                      # 握手

            tools = await session.list_tools()              # tools/list
            print("Server 暴露的工具:", [t.name for t in tools.tools])

            res = await session.call_tool("get_weather", {"city": "北京"})   # tools/call
            print("get_weather('北京') ->", res.content[0].text)

            res = await session.call_tool("add", {"a": 2, "b": 3})
            print("add(2,3) ->", res.content[0].text)


if __name__ == "__main__":
    asyncio.run(main())