# -*- coding: utf-8 -*-
"""
Unit tests - Translation Engine Module
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from plugin.translation_engine import TranslationEngine, TranslationResult, TranslationProvider


class TestTranslationEngine:
    """Translation engine unit tests"""
    
    @pytest.fixture
    def config(self):
        return {
            "primary_engine": "ollama",
            "ollama": {
                "model": "qwen2.5:7b",
                "endpoint": "http://localhost:11434",
                "timeout": 30
            },
            "cloud": {
                "provider": "deepl",
                "api_key": "test_key",
                "fallback_enabled": True
            }
        }
    
    @pytest.fixture
    def engine(self, config):
        return TranslationEngine(config)
    
    @pytest.mark.asyncio
    async def test_translate_with_ollama_success(self, engine):
        """Test Ollama translation success"""
        mock_response = {"response": "Hello, world!"}
        
        with patch("aiohttp.ClientSession.post") as mock_post:
            mock_resp = AsyncMock()
            mock_resp.status = 200
            mock_resp.json = AsyncMock(return_value=mock_response)
            mock_post.return_value.__aenter__.return_value = mock_resp
            
            result = await engine._translate_with_ollama("Hello world", "zh", "en")
            
            assert result is not None
            assert result.translated_text == "Hello, world!"
            assert result.provider == TranslationProvider.OLLAMA
    
    @pytest.mark.asyncio
    async def test_translate_with_ollama_fallback_to_cloud(self, engine):
        """Test fallback to cloud when Ollama fails"""
        with patch("aiohttp.ClientSession.post") as mock_post:
            # Simulate Ollama failure
            mock_post.return_value.__aenter__.return_value.status = 500
            
            # Simulate cloud success
            with patch.object(engine, "_translate_with_cloud") as mock_cloud:
                mock_cloud.return_value = TranslationResult(
                    original_text="test",
                    translated_text="test result",
                    source_lang="zh",
                    target_lang="en",
                    provider=TranslationProvider.DEEP_L
                )
                
                result = await engine.translate("test text")
                
                assert result is not None
                assert result.provider == TranslationProvider.DEEP_L
    
    @pytest.mark.asyncio
    async def test_translate_cache_hit(self, engine):
        """Test cache hit"""
        result1 = TranslationResult(
            original_text="test",
            translated_text="result",
            source_lang="zh",
            target_lang="en",
            provider=TranslationProvider.OLLAMA
        )
        
        engine.cache["test_auto_None"] = result1
        
        result2 = await engine.translate("test")
        
        assert result2 is result1
    
    @pytest.mark.asyncio
    async def test_batch_translate(self, engine):
        """Test batch translation"""
        with patch.object(engine, "translate") as mock_translate:
            mock_translate.side_effect = [
                TranslationResult("text1", "res1", "zh", "en", TranslationProvider.OLLAMA),
                TranslationResult("text2", "res2", "zh", "en", TranslationProvider.OLLAMA)
            ]
            
            results = await engine.batch_translate(["text1", "text2"])
            
            assert len(results) == 2
            assert mock_translate.call_count == 2
    
    def test_clean_cache(self, engine):
        """Test cache cleanup"""
        for i in range(1500):
            engine.cache[f"key_{i}"] = None
        
        assert len(engine.cache) > 1000
        
        engine._clean_cache()
        
        assert len(engine.cache) <= 500
    
    @pytest.mark.asyncio
    async def test_translate_without_api_key(self, engine):
        """Test cloud translation without API key"""
        engine.cloud_config["api_key"] = ""
        
        result = await engine._translate_with_cloud("test", "zh", "en")
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_translate_with_cloud_deepl_success(self, engine):
        """Test DeepL cloud translation success"""
        engine.cloud_config["api_key"] = "valid_key"
        mock_response = {"translations": [{"text": "Translated text"}]}
        
        with patch("aiohttp.ClientSession.post") as mock_post:
            mock_resp = AsyncMock()
            mock_resp.status = 200
            mock_resp.json = AsyncMock(return_value=mock_response)
            mock_post.return_value.__aenter__.return_value = mock_resp
            
            result = await engine._translate_with_deepl("test", "en", "zh", "valid_key")
            
            assert result is not None
            assert result.translated_text == "Translated text"
            assert result.provider == TranslationProvider.DEEP_L


class TestTranslationResult:
    """Translation result data class tests"""
    
    def test_translation_result_creation(self):
        result = TranslationResult(
            original_text="Hello",
            translated_text="Ni Hao",
            source_lang="en",
            target_lang="zh",
            provider=TranslationProvider.OLLAMA
        )
        
        assert result.original_text == "Hello"
        assert result.translated_text == "Ni Hao"
        assert result.provider == TranslationProvider.OLLAMA
    
    def test_translation_result_with_warning(self):
        result = TranslationResult(
            original_text="Hello",
            translated_text="Ni Hao",
            source_lang="en",
            target_lang="zh",
            provider=TranslationProvider.OLLAMA,
            cultural_warning="Cultural note here"
        )
        
        assert result.cultural_warning == "Cultural note here"
    
    def test_translation_result_confidence(self):
        result = TranslationResult(
            original_text="Test",
            translated_text="Test",
            source_lang="en",
            target_lang="en",
            provider=TranslationProvider.CACHE,
            confidence=1.0
        )
        
        assert result.confidence == 1.0
