import asyncio
from plugin.culture_helper import CultureHelper

async def main():
    helper = CultureHelper({"enabled": True})
    warnings = await helper.check("sample text", "JP")
    for w in warnings:
        print(f"Warning: {w.message}")

asyncio.run(main())
