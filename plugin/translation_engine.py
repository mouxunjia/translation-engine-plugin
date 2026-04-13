# -*- coding: utf-8 -*-
"""
Translation Engine - Core translation module
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional, Tuple, List
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class TranslationProvider(Enum):
    OLLAMA = "ollama"
    DEEP_L = "deepl"
    GOOGLE = "google"
    CACHE = "cache"


@dataclass
class TranslationResult:
    original_text: str
    translated_text: str
    source_lang: str
    target_lang: str
    provider: TranslationProvider
    cultural_warning: Optional[str] = None
    confidence: float = 0.0
    processing_time_ms: float = 0.0


class TranslationEngine:
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.primary_engine = config.get("primary_engine", "ollama")
        self.ollama_config = config.get("ollama", {})
        self.cloud_config = config.get("cloud", {})
        self.cache: Dict[str, TranslationResult] = {}
        self._session = None
        logger.info(f"TranslationEngine initialized, primary: {self.primary_engine}")
    
    async def translate(
        self,
        text: str,
        source_lang: str = "auto",
        target_lang: Optional[str] = None,
        context: str = "general"
    ) -> TranslationResult:
        """Translate text"""
        import time
        start_time = time.time()
        
        # Check cache
        cache_key = f"{text}_{source_lang}_{target_lang}"
        if cache_key in self.cache:
            logger.info(f"Cache hit: {text[:50]}...")
            return self.cache[cache_key]
        
        # Execute translation
        result = None
        errors = []
        
        # Try primary engine
        if self.primary_engine == "ollama":
            result = await self._translate_with_ollama(text, source_lang, target_lang)
            if not result:
                errors.append("Ollama translation failed")
                if self.cloud_config.get("fallback_enabled", True):
                    logger.warning("Falling back to cloud translation")
                    result = await self._translate_with_cloud(text, source_lang, target_lang)
        else:
            result = await self._translate_with_cloud(text, source_lang, target_lang)
            if not result and self.ollama_config.get("fallback_enabled", False):
                logger.warning("Falling back to Ollama translation")
                result = await self._translate_with_ollama(text, source_lang, target_lang)
        
        if not result:
            raise Exception(f"Translation failed: {', '.join(errors)}")
        
        result.processing_time_ms = (time.time() - start_time) * 1000
        result.original_text = text
        
        # Cache result
        self.cache[cache_key] = result
        if len(self.cache) > 1000:
            self._clean_cache()
        
        logger.info(f"Translation completed: {source_lang} -> {target_lang}, time: {result.processing_time_ms:.2f}ms")
        return result
    
    async def _translate_with_ollama(
        self,
        text: str,
        source_lang: str,
        target_lang: str
    ) -> Optional[TranslationResult]:
        """Translate using Ollama local model"""
        try:
            import aiohttp
            
            model = self.ollama_config.get("model", "qwen2.5:7b")
            endpoint = self.ollama_config.get("endpoint", "http://localhost:11434")
            timeout = self.ollama_config.get("timeout", 30)
            
            prompt = f"Translate the following text from {source_lang} to {target_lang}, return only the translation:\n\n{text}"
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{endpoint}/api/generate",
                    json={"model": model, "prompt": prompt, "stream": False},
                    timeout=aiohttp.ClientTimeout(total=timeout)
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return TranslationResult(
                            original_text=text,
                            translated_text=data.get("response", ""),
                            source_lang=source_lang,
                            target_lang=target_lang,
                            provider=TranslationProvider.OLLAMA,
                            confidence=0.85
                        )
        except Exception as e:
            logger.error(f"Ollama translation failed: {e}")
        
        return None
    
    async def _translate_with_cloud(
        self,
        text: str,
        source_lang: str,
        target_lang: str
    ) -> Optional[TranslationResult]:
        """Translate using cloud API"""
        provider = self.cloud_config.get("provider", "deepl")
        api_key = self.cloud_config.get("api_key", "")
        
        if not api_key:
            logger.warning("Cloud API key not configured")
            return None
        
        try:
            import aiohttp
            
            if provider == "deepl":
                return await self._translate_with_deepl(text, source_lang, target_lang, api_key)
            else:
                return await self._translate_with_google(text, source_lang, target_lang, api_key)
        except Exception as e:
            logger.error(f"Cloud translation failed: {e}")
        
        return None
    
    async def _translate_with_deepl(
        self,
        text: str,
        source_lang: str,
        target_lang: str,
        api_key: str
    ) -> TranslationResult:
        """Translate using DeepL API"""
        import aiohttp
        
        url = "https://api.deepl.com/v2/translate"
        params = {
            "auth_key": api_key,
            "text": text,
            "target_lang": target_lang.upper() if target_lang else "EN"
        }
        if source_lang != "auto":
            params["source_lang"] = source_lang.upper()
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=params, timeout=30) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return TranslationResult(
                        original_text=text,
                        translated_text=data["translations"][0]["text"],
                        source_lang=source_lang,
                        target_lang=target_lang,
                        provider=TranslationProvider.DEEP_L,
                        confidence=0.95
                    )
        return None
    
    async def _translate_with_google(
        self,
        text: str,
        source_lang: str,
        target_lang: str,
        api_key: str
    ) -> TranslationResult:
        """Translate using Google Translate API"""
        import aiohttp
        
        url = "https://translation.googleapis.com/language/translate/v2"
        params = {
            "q": text,
            "target": target_lang or "en",
            "key": api_key
        }
        if source_lang != "auto":
            params["source"] = source_lang
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=30) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return TranslationResult(
                        original_text=text,
                        translated_text=data["data"]["translations"][0]["translatedText"],
                        source_lang=source_lang,
                        target_lang=target_lang,
                        provider=TranslationProvider.GOOGLE,
                        confidence=0.90
                    )
        return None
    
    def _clean_cache(self) -> None:
        """Clean cache, keep only latest 500 entries"""
        keys_to_remove = list(self.cache.keys())[500:]
        for key in keys_to_remove:
            del self.cache[key]
        logger.info(f"Cache cleaned, current size: {len(self.cache)}")
    
    async def batch_translate(
        self,
        texts: List[str],
        source_lang: str = "auto",
        target_lang: Optional[str] = None
    ) -> List[TranslationResult]:
        """Batch translate multiple texts"""
        tasks = [self.translate(text, source_lang, target_lang) for text in texts]
        return await asyncio.gather(*tasks)
