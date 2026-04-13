# -*- coding: utf-8 -*-
"""
Push Notifier - Daily push and review module
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime, time, timedelta

logger = logging.getLogger(__name__)


@dataclass
class ReviewItem:
    id: str
    content: str
    category: str
    next_review_date: datetime
    review_count: int
    difficulty: int


class PushNotifier:
    
    def __init__(self, config: Dict[str, Any], data_path: Path = None):
        self.config = config
        self.enabled = config.get("enabled", True)
        self.obsidian_notification = config.get("obsidian_notification", True)
        self.system_notification = config.get("system_notification", True)
        self.daily_time = config.get("daily_review_time", "09:00")
        self.review_count = config.get("review_count", 5)
        
        self.data_path = data_path
        self.review_items: List[ReviewItem] = []
        self._task: Optional[asyncio.Task] = None
        self._obsidian_app = None
        
        logger.info("PushNotifier initialized")
    
    def set_obsidian_app(self, app):
        self._obsidian_app = app
    
    async def start(self) -> None:
        if not self.enabled:
            logger.info("Push service not enabled")
            return
        
        await self._load_review_items()
        self._task = asyncio.create_task(self._scheduler_loop())
        logger.info(f"Push service started, daily time: {self.daily_time}")
    
    async def stop(self) -> None:
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        await self._save_review_items()
        logger.info("Push service stopped")
    
    async def _scheduler_loop(self) -> None:
        while True:
            now = datetime.now()
            target_time = self._parse_time(self.daily_time)
            next_run = datetime.combine(now.date(), target_time)
            
            if now >= next_run:
                next_run += timedelta(days=1)
            
            wait_seconds = (next_run - now).total_seconds()
            await asyncio.sleep(wait_seconds)
            await self._send_daily_review()
    
    def _parse_time(self, time_str: str) -> time:
        parts = time_str.split(":")
        return time(int(parts[0]), int(parts[1]) if len(parts) > 1 else 0)
    
    async def _send_daily_review(self) -> None:
        reviews = await self.get_today_reviews()
        
        if not reviews:
            logger.info("No reviews for today")
            return
        
        message = f"Daily Review ({len(reviews)} items)\n"
        for i, review in enumerate(reviews[:3]):
            message += f"{i+1}. {review.content[:30]}...\n"
        if len(reviews) > 3:
            message += f"... {len(reviews)} total"
        
        if self.obsidian_notification and self._obsidian_app:
            try:
                await self._obsidian_app.notification.show(message)
                logger.info("Obsidian notification sent")
            except Exception as e:
                logger.error(f"Failed to send Obsidian notification: {e}")
        
        if self.system_notification:
            await self._send_system_notification("Translation Engine - Daily Review", message)
        
        logger.info(f"Daily review sent, {len(reviews)} items")
    
    async def _send_system_notification(self, title: str, message: str) -> None:
        try:
            import platform
            system = platform.system()
            
            if system == "Windows":
                from win10toast import ToastNotifier
                toaster = ToastNotifier()
                toaster.show_toast(title, message, duration=5)
            elif system == "Darwin":
                import subprocess
                subprocess.run(["osascript", "-e", f'display notification "{message}" with title "{title}"'])
            elif system == "Linux":
                import subprocess
                subprocess.run(["notify-send", title, message])
        except Exception as e:
            logger.error(f"Failed to send system notification: {e}")
    
    async def get_today_reviews(self) -> List[ReviewItem]:
        now = datetime.now()
        today_start = datetime(now.year, now.month, now.day)
        today_end = today_start + timedelta(days=1)
        
        return [
            item for item in self.review_items
            if today_start <= item.next_review_date < today_end
        ]
    
    async def add_review_item(self, content: str, category: str, difficulty: int = 3) -> ReviewItem:
        import uuid
        
        intervals = [1, 2, 4, 7, 14, 30]
        interval = intervals[min(difficulty - 1, len(intervals) - 1)]
        
        item = ReviewItem(
            id=str(uuid.uuid4()),
            content=content,
            category=category,
            next_review_date=datetime.now() + timedelta(days=interval),
            review_count=0,
            difficulty=difficulty
        )
        
        self.review_items.append(item)
        await self._save_review_items()
        logger.info(f"Added review item: {content[:50]}...")
        
        return item
    
    async def mark_reviewed(self, item_id: str, success: bool = True) -> None:
        for item in self.review_items:
            if item.id == item_id:
                item.review_count += 1
                if success:
                    intervals = [1, 2, 4, 7, 14, 30, 60]
                    next_idx = min(item.review_count, len(intervals) - 1)
                    item.next_review_date = datetime.now() + timedelta(days=intervals[next_idx])
                else:
                    item.next_review_date = datetime.now() + timedelta(days=1)
                break
        
        await self._save_review_items()
        logger.info(f"Review item marked: {item_id}, success={success}")
    
    async def _load_review_items(self) -> None:
        if not self.data_path:
            return
        
        file_path = self.data_path / "review_records" / "reviews.json"
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for item in data:
                        self.review_items.append(ReviewItem(
                            id=item["id"],
                            content=item["content"],
                            category=item["category"],
                            next_review_date=datetime.fromisoformat(item["next_review_date"]),
                            review_count=item["review_count"],
                            difficulty=item["difficulty"]
                        ))
                logger.info(f"Loaded {len(self.review_items)} review items")
            except Exception as e:
                logger.error(f"Failed to load review items: {e}")
    
    async def _save_review_items(self) -> None:
        if not self.data_path:
            return
        
        file_path = self.data_path / "review_records" / "reviews.json"
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        data = [
            {
                "id": item.id,
                "content": item.content,
                "category": item.category,
                "next_review_date": item.next_review_date.isoformat(),
                "review_count": item.review_count,
                "difficulty": item.difficulty
            }
            for item in self.review_items
        ]
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.debug(f"Saved {len(self.review_items)} review items")
