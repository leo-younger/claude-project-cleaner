---
name: claude-project-cleaner
description: Use when finishing a project, cleaning up after development, or wanting to see what this conversation downloaded/created. Triggers on "project cleanup", "clean up project", "what did this session do", "organize claude assets", "clean claude downloads", "清理项目", "post-project cleanup", "收纳整理".
---

# Claude Project Cleaner

会话级清理 —— 分析**当前对话窗口**干了什么，仅清理本次会话产物，不碰其他项目。

## 核心理念

```
对话窗口结束，说"清理项目"
  │
  ├── 解析当前 transcript → 提取所有 Write/Edit/Bash/Skill 操作
  ├── 过滤只读操作（Read/WebSearch 不占磁盘，自动忽略）
  ├── 分类展示：
  │   ├── 📦 安装/下载了什么软件
  │   ├── 📝 创建了哪些文件
  │   ├── ✏️ 编辑了哪些文件
  │   └── 🧠 用了哪些 Skills
  └── 用户决定清理哪些
```

**绝不碰**：其他项目、其他对话窗口、全局 skills/配置。

## 使用方式

对话快结束时直接说：**"清理项目"** 或 **"看看这个窗口做了什么"**

会自动解析当前 transcript，生成报告，让你确认后清理。

## 命令行

```bash
# 分析当前对话窗口
python scripts/session_cleaner.py

# 分析指定 transcript
python scripts/session_cleaner.py ~/.claude/projects/xxx/session.jsonl
```

## 全局扫描（旧版，不常用）

```bash
python scripts/scanner.py && python scripts/organizer.py && python scripts/cleaner.py --auto --safe-only
```

## 冷却机制（可选钩子）

`hooks.json` → 加到 `.claude/settings.json`，闲置 7 天提醒 / 30 天自动清缓存。
