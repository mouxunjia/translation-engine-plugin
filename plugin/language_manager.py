# -*- coding: utf-8 -*-
"""
Language Manager - Multi-language management module
"""

import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class LanguageCode(Enum):
    ZH_CN = "zh-CN"
    ZH_TW = "zh-TW"
    EN_US = "en-US"
    EN_GB = "en-GB"
    JA_JP = "ja-JP"
    KO_KR = "ko-KR"
    FR_FR = "fr-FR"
    DE_DE = "de-DE"
    ES_ES = "es-ES"
    RU_RU = "ru-RU"
    AR_SA = "ar-SA"


@dataclass
class LanguageProfile:
    code: str
    name: str
    is_mother_tongue: bool
    proficiency_level: int
    preferred: bool


class LanguageManager:
    
    LANGUAGE_NAMES = {
        "zh-CN": "Simplified Chinese",
        "zh-TW": "Traditional Chinese",
        "en-US": "English (US)",
        "en-GB": "English (UK)",
        "ja-JP": "Japanese",
        "ko-KR": "Korean",
        "fr-FR": "French",
        "de-DE": "German",
        "es-ES": "Spanish",
        "ru-RU": "Russian",
        "ar-SA": "Arabic"
    }
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.mother_tongue = config.get("user_mother_tongue", "zh-CN")
        self.assistant_languages = config.get("assistant_languages", ["en-US"])
        self.auto_detect = config.get("auto_detect", True)
        self.third_language_enabled = config.get("third_language_enabled", False)
        self.third_language = config.get("third_language", "ja-JP")
        
        self.supported_languages = list(self.LANGUAGE_NAMES.keys())
        self._detection_cache: Dict[str, str] = {}
        
        logger.info(f"LanguageManager initialized, mother tongue: {self.mother_tongue}")
    
    def get_target_language(self, context: str = "general") -> str:
        return self.mother_tongue
    
    def get_assistant_languages(self) -> List[str]:
        languages = self.assistant_languages.copy()
        if self.third_language_enabled and self.third_language not in languages:
            languages.append(self.third_language)
        return languages
    
    async def detect_language(self, text: str) -> str:
        if not text or not self.auto_detect:
            return "en-US"
        
        if text in self._detection_cache:
            return self._detection_cache[text]
        
        try:
            import langdetect
            from langdetect import detect
            
            detected = detect(text)
            
            mapping = {
                "zh-cn": "zh-CN",
                "zh-tw": "zh-TW",
                "en": "en-US",
                "ja": "ja-JP",
                "ko": "ko-KR",
                "fr": "fr-FR",
                "de": "de-DE",
                "es": "es-ES",
                "ru": "ru-RU",
                "ar": "ar-SA"
            }
            
            result = mapping.get(detected, "en-US")
            self._detection_cache[text] = result
            
            if len(self._detection_cache) > 1000:
                self._detection_cache.clear()
            
            return result
            
        except ImportError:
            logger.warning("langdetect not installed")
            return self._simple_detect(text)
        except Exception as e:
            logger.error(f"Language detection failed: {e}")
            return "en-US"
    
    def _simple_detect(self, text: str) -> str:
        for ch in text:
            if '\u4e00' <= ch <= '\u9fff':
                return "zh-CN"
            if '\u3040' <= ch <= '\u309f' or '\u30a0' <= ch <= '\u30ff':
                return "ja-JP"
            if '\uac00' <= ch <= '\ud7af':
                return "ko-KR"
        return "en-US"
    
    def get_language_name(self, code: str) -> str:
        return self.LANGUAGE_NAMES.get(code, code)
    
    async def switch_mother_tongue(self, new_language: str) -> bool:
        if new_language not in self.supported_languages:
            logger.error(f"Unsupported language: {new_language}")
            return False
        
        self.mother_tongue = new_language
        self.config["user_mother_tongue"] = new_language
        
        logger.info(f"Mother tongue switched to: {new_language}")
        return True
    
    async def add_assistant_language(self, language: str) -> bool:
        if language not in self.supported_languages:
            return False
        
        if language not in self.assistant_languages:
            self.assistant_languages.append(language)
            self.config["assistant_languages"] = self.assistant_languages
            logger.info(f"Added assistant language: {language}")
        
        return True
    
    async def remove_assistant_language(self, language: str) -> bool:
        if language in self.assistant_languages:
            self.assistant_languages.remove(language)
            self.config["assistant_languages"] = self.assistant_languages
            logger.info(f"Removed assistant language: {language}")
            return True
        return False
    
    def get_all_languages(self) -> List[LanguageProfile]:
        profiles = []
        for code, name in self.LANGUAGE_NAMES.items():
            profiles.append(LanguageProfile(
                code=code,
                name=name,
                is_mother_tongue=(code == self.mother_tongue),
                proficiency_level=5 if code == self.mother_tongue else 3,
                preferred=(code in self.assistant_languages or code == self.mother_tongue)
            ))
        return profiles
