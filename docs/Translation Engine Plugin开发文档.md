# Translation Engine Plugin - 开发文档

## 项目概述

| 属性 | 值 |
|------|-----|
| 项目名称 | translation-engine-plugin |
| 版本 | v1.0.0 |
| 开发语言 | Python 3.10+ |
| 框架 | Obsidian Plugin API |
| 目标平台 | Windows / macOS / Linux / iOS / Android |

## 核心功能模块
┌─────────────────────────────────────────────────────────────┐
│ translation-engine-plugin │
├─────────────────────────────────────────────────────────────┤
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐ │
│ │ main.py │ │ translation │ │ culture_helper.py │ │
│ │ 插件入口 │ │ engine.py │ │ 文化障碍检测 │ │
│ └─────────────┘ └─────────────┘ └─────────────────────┘ │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐ │
│ │ push │ │ language_ │ │ tools/ │ │
│ │ notifier.py │ │ manager.py │ │ 外事工具集 │ │
│ └─────────────┘ └─────────────┘ └─────────────────────┘ │
└─────────────────────────────────────────────────────────────┘

text

## 命名规范

| 类型 | 规范 | 示例 |
|------|------|------|
| 插件名称 | `{功能}-plugin` | `translation-engine-plugin` |
| 模块文件 | 小写 + 下划线 | `translation_engine.py` |
| 类名 | 大驼峰 | `TranslationEngine` |
| 函数/方法 | 小写 + 下划线 | `translate_text()` |
| 常量 | 全大写下划线 | `MAX_RETRY_COUNT = 3` |
| 私有成员 | 单下划线前缀 | `_internal_cache` |
| 测试文件 | `test_` + 模块名 | `test_translation_engine.py` |

## 版本规范

采用语义化版本 `MAJOR.MINOR.PATCH`

| 类型 | 规则 | 示例场景 |
|------|------|----------|
| MAJOR | 不兼容的API变更 | 插件接口重构 |
| MINOR | 向后兼容的功能新增 | 新增翻译引擎 |
| PATCH | 向后兼容的问题修复 | Bug修复 |

## API 设计

### 翻译引擎接口

```python
def translate_text(
    text: str,
    source_lang: str = "auto",
    target_lang: str = None,
    context: str = "general"
) -> TranslationResult:
    """
    翻译文本并返回文化注释
    
    Args:
        text: 待翻译文本
        source_lang: 源语言，默认自动检测
        target_lang: 目标语言，默认使用用户母语
        context: 场景上下文 (general/meeting/banquet/negotiation)
    
    Returns:
        TranslationResult: 包含翻译结果、文化注释、敏感词警告
    """
    pass
文化检测接口
python
def detect_cultural_issues(
    text: str,
    target_culture: str
) -> CulturalWarning:
    """
    检测文本中的文化敏感问题
    
    Returns:
        CulturalWarning: 包含警告级别、问题描述、替代建议
    """
    pass
配置文件结构
config.yaml
yaml
# 翻译引擎配置
translation:
  primary_engine: "ollama"  # ollama / cloud
  ollama:
    model: "qwen2.5:7b"
    endpoint: "http://localhost:11434"
    timeout: 30
  cloud:
    provider: "deepl"  # deepl / google
    api_key: ""
  
# 多语言配置  
language:
  user_mother_tongue: "zh-CN"
  assistant_languages: ["en", "fr"]
  auto_detect: true

# 文化检测配置
cultural_filter:
  enabled: true
  sensitive_action: "filter_and_log"  # filter / warn / filter_and_log
  log_path: "data/sensitive_logs.json"

# 推送配置
push:
  obsidian_notification: true
  system_notification: true
  daily_review_time: "09:00"
  review_count: 5

# 工具集成配置
tools:
  notebook: true
  reminder: true
  term_library: true
  culture_archive: true
  speaking_practice: true
  template_library: true
  realtime_translate: true
错误处理策略
错误类型	处理策略	重试次数
Ollama 连接失败	降级到云端API	3
云端API超时	返回缓存结果	2
文化检测超时	跳过检测，记录日志	1
敏感词匹配	静默过滤 + 记录	0
日志规范
日志级别：DEBUG < INFO < WARNING < ERROR

日志格式：

text
[2024-01-15 10:30:45] INFO translation_engine: 翻译完成 - 源语言:en 目标语言:zh
[2024-01-15 10:30:46] WARNING culture_helper: 检测到敏感词 - 输入:[masked]
[2024-01-15 10:30:47] ERROR push_notifier: 系统通知发送失败 - 原因:权限不足
text

### 2.2 生成开发文档到目录

```powershell
@'
# 开发文档内容见上方

# 将以下文档写入对应文件：
# - docs/DEVELOPMENT.md
# - docs/API.md  
# - docs/USAGE.md
# - docs/INSTALL.md
# - config/config.schema.json
'@

# 实际写入文件
$docs = @{
    "docs/DEVELOPMENT.md" = "开发文档内容（见上）"
    "docs/API.md" = "API文档内容"
    "docs/USAGE.md" = "使用手册内容"
    "docs/INSTALL.md" = "安装指南内容"
    "config/config.schema.json" = '{"type":"object","properties":{}}'
}

foreach ($file in $docs.Keys) {
    $fullPath = "F:\obsidian_developer\translation-engine-plugin\$file"
    $content = $docs[$file]
    # 创建目录（如果不存在）
    $dir = Split-Path $fullPath -Parent
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force
    }
    Set-Content -Path $fullPath -Value $content -Encoding UTF8
    Write-Host "生成文档: $fullPath" -ForegroundColor Green
}
🚀 执行命令汇总
在 Windows CMD 中依次执行：
batch
@echo off
chcp 65001 > nul

echo ========================================
echo 第1步：创建目录结构
echo ========================================
powershell -ExecutionPolicy Bypass -File "F:\obsidian_developer\create_dirs.ps1"

echo.
echo ========================================
echo 第2步：生成开发文档
echo ========================================
powershell -ExecutionPolicy Bypass -Command "& 'F:\obsidian_developer\generate_docs.ps1'"

echo.
echo ========================================
echo 完成！请检查 F:\obsidian_developer 目录
echo ========================================
pause