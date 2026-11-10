---
name: creator-idea-vault
description: Build a private offline idea vault from user-supplied links and excerpts; deduplicate, search, generate sourced writing angles and export Markdown/Notion CSV. Use for creator research collections.
license: MIT
compatibility: Python 3.10+; Windows 10/macOS/Linux; local command execution only
metadata:
  author: "0xMulight"
  version: "1.0.0"
---

# Creator Idea Vault

## 使用时机

用户想把零散链接、收藏视频、帖子和自己的参考笔记变成可搜索的选题库，或导出Notion CSV。

## 输入

CSV（列 `platform,source_url,title,content,notes,added_at`），每行至少标题+本人提供的内容摘录/备注。

## 执行流程

1. 收集合法可访问的链接和用户授权的摘要；不要说已打开没有实际读过的页面。
2. 从仓库根目录运行 `python -m creator_idea_vault import --file examples/sources.csv`。
3. 需要时用 `python -m creator_idea_vault search --query 关键字` 回找原始来源。
4. 运行 `python -m creator_idea_vault export --output reports`，得到`idea-vault.md`及`notion-import.csv`。
5. 先选一个角度研究，核对原文、时间和数据，再写自己的内容；不可直接抄袭来源。

## 验收和权限

- 同一规范化URL重复导入不产生两个来源。
- 输出必须带来源与显式待核对事项；未知的播放数/表现不输出虚构数字。
- 这只是用户提供资料的离线整理，**不会自动读取账号收藏**；若Bot无法访问Python环境，纯文本按CSV列组织即可。
- 不自动访问受限内容、不索取平台Cookie/API Key，不发布和联系原作者。

