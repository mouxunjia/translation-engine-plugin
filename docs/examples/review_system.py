import asyncio
from plugin.push_notifier import PushNotifier

async def main():
    notifier = PushNotifier({"enabled": True})
    await notifier.add_review_item("Cultural tip", "etiquette", 3)
    reviews = await notifier.get_today_reviews()
    print(f"Reviews: {len(reviews)}")

asyncio.run(main())
