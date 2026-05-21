---
name: claude-project-cleaner
description: Use when finishing a project, cleaning up after development, organizing Claude-downloaded assets, or wanting to reclaim disk space from old tool versions and cache. Triggers on "project cleanup", "clean up project", "organize claude assets", "clean claude downloads", "project organizer", "清理项目", "tidy up after project", "post-project cleanup", "收纳整理", "/cleanup".
---

# Claude Project Cleaner

项目结束后的"收纳师"——自动扫描 Claude Code 在项目周期中下载/生成的一切资产，分类整理成可复用工具箱，清理冗余旧版，输出干净交接清单。

## 智能冷却机制 (Cooldown)

```
项目活跃
  │
  ├── 每次会话结束 => 自动记录时间戳 (Stop hook)
  │
  ├── 闲置 7 天 => 下次打开项目时提醒 "该清理了" (nudge)
  │
  ├── 闲置 30 天 => 自动清理缓存 (仅 Category E，安全无风险)
  │
  └── 手动 /cleanup => 随时可用，全量扫描 + 用户确认
```

**不会自动删的东西**: 可复用工具 (A)、项目配置 (B)、知识资产 (D) —— 这些永远需要手动确认。

## 安装自动冷却 (可选)

将 `hooks.json` 中的 hooks 块复制到项目的 `.claude/settings.json`：

```bash
# 快速安装
python scripts/cooldown.py touch    # 手动记录活动
python scripts/cooldown.py check    # 查看冷却状态
python scripts/cooldown.py reset    # 重置冷却计时
```

## 使用方法

### 完整清理（交互模式，默认）
```bash
cd scripts/
python scanner.py                    # 扫描 12 个位置
python organizer.py                  # 分类 + 生成报告
python cleaner.py                    # dry-run 预览
python cleaner.py --auto             # 确认后执行全量清理
```

### 安全模式（仅清理缓存，适合自动化）
```bash
python scanner.py && python organizer.py && python cleaner.py --auto --safe-only
```

### 一键自动
```bash
python scanner.py && python organizer.py && python cleaner.py --auto
```

### 仅出报告
```bash
python scanner.py && python organizer.py && python cleaner.py --report-only
```

### 回滚
```bash
python cleaner.py --rollback 20260521_143000
```

## 扫描的 12 个位置

| # | 位置 | 内容 |
|---|------|------|
| 1 | `~/.claude/skills/` | 全局 skills |
| 2 | `~/.claude/plugins/` | 插件缓存 |
| 3 | `~/.claude/projects/` | 按项目 memory |
| 4 | `~/.claude/commands/` | 自定义命令 |
| 5 | `~/.claude/hooks/` | hooks 脚本 |
| 6 | `~/.claude/settings.json` | 全局配置（不删） |
| 7 | `<project>/.claude/` | 项目配置 |
| 8 | `<project>/.claude/skills/` | 项目 skills |
| 9 | 全局 npm | MCP 依赖 |
| 10 | 全局 pip | MCP 依赖 |
| 11 | `<project>/node_modules/` | 项目 MCP |
| 12 | `~/.claude/cache/` | 会话缓存 |

## 6 大分类

| 分类 | 说明 | 自动清理 |
|------|------|:--:|
| A. 可复用工具 | 全局 skills、MCP 包 | ❌ |
| B. 项目配置 | settings.json、hooks | ❌ |
| C. 生成产物 | specs、plans、build | ❌ |
| D. 知识资产 | memory、CLAUDE.md | ❌ |
| E. 缓存冗余 | cache、tmp | ✅ 30天闲置自动清 |
| F. 旧版可升级 | 同工具多版本 | ❌ |

## 安全保护

- **白名单永不删**: `.git/`, `CLAUDE.md`, `src/`, 构建配置文件
- **Dry-run 强制先行**: `--auto` 模式下也先预览
- **备份可回滚**: 所有删除先备份到 `~/.claude/backup/<timestamp>/`
- **冷却期保护**: 闲置不足 7 天不做任何自动清理

## 产出文件

| 文件 | 说明 |
|------|------|
| `scan_result.json` | 原始扫描数据 |
| `classified.json` | 分类结果（机器可读） |
| `CLAUDE-CLEANUP-REPORT.md` | 清理报告（人可读） |
| `CLAUDE-CLEANUP-DONE.md` | 执行完成报告 + 回滚指令 |
| `~/.claude/backup/<ts>/` | 备份目录 |
| `.cleaner_activity.json` | 冷却计时文件 |
