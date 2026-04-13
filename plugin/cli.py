#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Translation Engine CLI - 供 Obsidian 调用的命令行接口
"""

import sys
import os
import asyncio
import json
import argparse

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from plugin.translation_engine import TranslationEngine
from plugin.culture_helper import CultureHelper
from plugin.language_manager import LanguageManager


async def translate_text(text, source_lang="auto", target_lang="zh-CN"):
    """翻译文本"""
    try:
        # 加载配置
        import yaml
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'config.yaml')
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        engine = TranslationEngine(config.get("translation", {}))
        result = await engine.translate(text, source_lang, target_lang)
        
        return result.translated_text
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return "Translation failed"


async def check_culture(text, target_country=None):
    """文化检测"""
    try:
        import yaml
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'config.yaml')
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        helper = CultureHelper(config.get("cultural_filter", {}))
        warnings = await helper.check(text, target_country)
        
        if warnings:
            return "; ".join([w.message for w in warnings])
        else:
            return "No issues found"
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return "Check failed"


async def get_supported_languages():
    """获取支持的语言列表"""
    try:
        import yaml
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'config.yaml')
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        manager = LanguageManager(config.get("language", {}))
        languages = manager.get_all_languages()
        
        result = {}
        for lang in languages:
            result[lang.code] = lang.name
        
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return "{}"


def main():
    parser = argparse.ArgumentParser(description="Translation Engine CLI")
    parser.add_argument("text", nargs="?", help="Text to translate")
    parser.add_argument("--culture", action="store_true", help="Run culture check instead of translation")
    parser.add_argument("--source", default="auto", help="Source language")
    parser.add_argument("--target", default="zh-CN", help="Target language")
    parser.add_argument("--country", help="Target country for culture check")
    parser.add_argument("--languages", action="store_true", help="List supported languages")
    
    args = parser.parse_args()
    
    if args.languages:
        result = asyncio.run(get_supported_languages())
        print(result)
    elif args.culture:
        result = asyncio.run(check_culture(args.text or "", args.country))
        print(result)
    elif args.text:
        result = asyncio.run(translate_text(args.text, args.source, args.target))
        print(result)
    else:
        print("Usage: python cli.py <text> [--culture] [--source lang] [--target lang]")
        print("       python cli.py --languages")


if __name__ == "__main__":
    main()
