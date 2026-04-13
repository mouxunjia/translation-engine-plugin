import asyncio
from plugin.translation_engine import TranslationEngine

async def main():
    config = {"primary_engine": "ollama", "ollama": {"model": "qwen2.5:7b"}}
    engine = TranslationEngine(config)
    result = await engine.translate("Hello", "en", "zh-CN")
    print(f"Result: {result.translated_text}")

asyncio.run(main())
