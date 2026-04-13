import asyncio
from plugin.translation_engine import TranslationEngine

async def main():
    config = {"primary_engine": "ollama"}
    engine = TranslationEngine(config)
    texts = ["Hello", "Good morning", "How are you"]
    results = await engine.batch_translate(texts, target_lang="zh-CN")
    for r in results:
        print(r.translated_text)

asyncio.run(main())
