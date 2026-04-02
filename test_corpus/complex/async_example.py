
import asyncio

async def fetch_data(url):
    await asyncio.sleep(1)
    return {"url": url, "data": "content"}

async def main():
    tasks = [fetch_data(f"url_{i}") for i in range(5)]
    results = await asyncio.gather(*tasks)
    return results
