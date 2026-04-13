# Development Documentation

## Project Overview
- Version: v1.0.0
- Language: Python 3.10+
- Framework: Obsidian Plugin API

## Architecture
- plugin/main.py - Entry point
- plugin/translation_engine.py - Translation core
- plugin/culture_helper.py - Cultural detection
- plugin/push_notifier.py - Push service
- plugin/language_manager.py - Language management

## Development Setup
pip install -r requirements.txt
.\scripts\run_tests.ps1 -Coverage
