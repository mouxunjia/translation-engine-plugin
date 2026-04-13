# -*- coding: utf-8 -*-
"""
Culture Helper - Cultural issue detection module
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class CulturalWarning:
    level: str
    category: str
    original_text: str
    suggested_alternative: Optional[str]
    message: str
    country: Optional[str] = None


class CultureHelper:
    
    def __init__(self, config: Dict[str, Any], data_path: Path = None):
        self.config = config
        self.enabled = config.get("enabled", True)
        self.sensitive_action = config.get("sensitive_action", "filter_and_log")
        self.log_path = Path(data_path) / config.get("log_path", "sensitive_logs.json") if data_path else None
        
        self.sensitive_words: Dict[str, List[str]] = {}
        self.cultural_rules: List[Dict] = config.get("custom_rules", [])
        self._load_default_rules()
        
        logger.info(f"CultureHelper initialized")
    
    def _load_default_rules(self) -> None:
        """Load default cultural rules"""
        self.sensitive_words = {
            "political": ["sensitive_word_1", "sensitive_word_2"],
            "religious": ["religious_term_1"],
            "taboo": ["taboo_word_1"],
            "etiquette": ["etiquette_term_1"]
        }
        
        self.cultural_rules.extend([
            {"country": "JP", "category": "etiquette", "pattern": "honorific", "suggestion": "Use proper honorifics"},
            {"country": "US", "category": "political", "pattern": "race", "suggestion": "Avoid racial discussions"},
            {"country": "FR", "category": "etiquette", "pattern": "greeting", "suggestion": "Use Bonjour as greeting"},
        ])
    
    async def check(self, text: str, target_country: str = None) -> List[CulturalWarning]:
        """Check text for cultural issues"""
        if not self.enabled:
            return []
        
        warnings = []
        
        # Check sensitive words
        for category, words in self.sensitive_words.items():
            for word in words:
                if word.lower() in text.lower():
                    warning = CulturalWarning(
                        level="error" if category == "political" else "warning",
                        category=category,
                        original_text=word,
                        suggested_alternative=self._get_alternative(word, category),
                        message=f"Detected {category} sensitive word: {word}"
                    )
                    warnings.append(warning)
                    
                    if self.sensitive_action == "filter_and_log":
                        await self._log_sensitive_event(text, warning)
        
        # Check cultural rules
        for rule in self.cultural_rules:
            if target_country and rule.get("country") != target_country:
                continue
            if rule.get("pattern") in text:
                warning = CulturalWarning(
                    level="warning",
                    category=rule.get("category", "etiquette"),
                    original_text=rule.get("pattern"),
                    suggested_alternative=rule.get("suggestion"),
                    message=f"Cultural tip: {rule.get('suggestion')}",
                    country=rule.get("country")
                )
                warnings.append(warning)
        
        if warnings:
            logger.info(f"Found {len(warnings)} cultural issues")
        
        return warnings
    
    def _get_alternative(self, word: str, category: str) -> Optional[str]:
        """Get alternative suggestion for sensitive word"""
        alternatives = {
            "sensitive_word_1": "alternative_1",
            "sensitive_word_2": "alternative_2",
        }
        return alternatives.get(word)
    
    async def _log_sensitive_event(self, text: str, warning: CulturalWarning) -> None:
        """Log sensitive event to file"""
        if not self.log_path:
            return
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "original_text": text[:200],
            "warning": {
                "level": warning.level,
                "category": warning.category,
                "message": warning.message
            }
        }
        
        try:
            if self.log_path.exists():
                with open(self.log_path, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
            else:
                logs = []
            
            logs.append(log_entry)
            
            if len(logs) > 1000:
                logs = logs[-1000:]
            
            with open(self.log_path, 'w', encoding='utf-8') as f:
                json.dump(logs, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Failed to log sensitive event: {e}")
    
    async def get_suggestions(self, text: str) -> List[str]:
        """Get improvement suggestions for text"""
        warnings = await self.check(text)
        return [w.suggested_alternative for w in warnings if w.suggested_alternative]
    
    def add_custom_rule(self, country: str, category: str, pattern: str, suggestion: str) -> None:
        """Add custom cultural rule"""
        self.cultural_rules.append({
            "country": country,
            "category": category,
            "pattern": pattern,
            "suggestion": suggestion
        })
        logger.info(f"Added custom rule: {country} - {pattern}")
