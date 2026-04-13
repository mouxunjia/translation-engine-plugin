# -*- coding: utf-8 -*-
"""
Translation Engine Plugin - Main Entry
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional

try:
    import obsidian
except ImportError:
    class obsidian:
        class Plugin:
            pass
        class App:
            pass

from .translation_engine import TranslationEngine
from .culture_helper import CultureHelper
from .push_notifier import PushNotifier
from .language_manager import LanguageManager

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class TranslationEnginePlugin(obsidian.Plugin):
    
    def __init__(self, app: obsidian.App, manifest: Dict[str, Any]):
        super().__init__(app, manifest)
        self.config: Dict[str, Any] = {}
        self.plugin_path: Optional[Path] = None
        self.translation_engine: Optional[TranslationEngine] = None
        self.culture_helper: Optional[CultureHelper] = None
        self.push_notifier: Optional[PushNotifier] = None
        self.language_manager: Optional[LanguageManager] = None
        logger.info("Translation Engine Plugin initialized")
    
    async def onload(self) -> None:
        logger.info("Loading Translation Engine Plugin...")
        await self._load_config()
        await self._init_modules()
        await self._register_commands()
        if self.config.get("push", {}).get("enabled", True):
            await self._start_push_service()
        logger.info("Translation Engine Plugin loaded")
    
    async def onunload(self) -> None:
        logger.info("Unloading Translation Engine Plugin...")
        if self.push_notifier:
            await self.push_notifier.stop()
        await self._save_config()
        logger.info("Translation Engine Plugin unloaded")
    
    async def _load_config(self) -> None:
        import yaml
        config_path = self.plugin_path / "config" / "config.yaml"
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
        else:
            self.config = self._get_default_config()
            await self._save_config()
        logger.info(f"Config loaded: {len(self.config)} items")
    
    async def _save_config(self) -> None:
        import yaml
        config_path = self.plugin_path / "config" / "config.yaml"
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(self.config, f, allow_unicode=True, default_flow_style=False)
        logger.info("Config saved")
    
    def _get_default_config(self) -> Dict[str, Any]:
        return {
            "translation": {"primary_engine": "ollama"},
            "language": {"user_mother_tongue": "zh-CN"},
            "cultural_filter": {"enabled": True},
            "push": {"enabled": True}
        }
    
    async def _init_modules(self) -> None:
        self.translation_engine = TranslationEngine(self.config.get("translation", {}))
        self.culture_helper = CultureHelper(self.config.get("cultural_filter", {}))
        self.push_notifier = PushNotifier(self.config.get("push", {}))
        self.language_manager = LanguageManager(self.config.get("language", {}))
        logger.info("Modules initialized")
    
    async def _register_commands(self) -> None:
        logger.info("Commands registered")
    
    async def _start_push_service(self) -> None:
        if self.config.get("push", {}).get("enabled", True):
            await self.push_notifier.start()
            logger.info("Push service started")
