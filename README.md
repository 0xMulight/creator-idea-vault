# 💡 Creator Idea Vault · 创作者选题库

把你实际收藏的 X 帖、YouTube、TikTok、文章资料，**连同自己的摘要**放进本地SQLite选题库。自动去重、检索、整理成三类选题角度，并导出可导入Notion的CSV。

## Windows 10 一分钟体验

1. 安装 Python 3.10+，下载 ZIP 解压。
2. 双击 `启动工具.bat`，选 `1` 导入 `examples/sources.csv`；选 `2` 导出选题。
3. 查看 `reports/idea-vault.md` 和 `reports/notion-import.csv`。
4. 把你自己的收藏链接、标题和内容摘录填到 CSV（模板见 `examples/blank-template.csv`），再导入。

```bash
python -m creator_idea_vault import --file examples/sources.csv
python -m creator_idea_vault stats
python -m creator_idea_vault search --query 剪辑
python -m creator_idea_vault export --output reports
python -m unittest discover -s tests -v
```

## 真实能力 / 边界

- ✅ 本地SQLite持久化、清理utm链接、按来源去重、关键词搜索、三种可写角度、Markdown与Notion CSV导出。
- ✅ 每条候选保留素材来源、标题、摘要和ID，方便回到原文核对。
- ❌ 不抓私人 X 收藏夹，不绕过网站登录，也不自动读取受版权保护的视频。
- ❌ 单纯贴链接不能得出正文内容：**必须有你自己提供的标题和内容摘要**。
- ❌ 角度是写作建议，不是真实热度排名；不会虚构点击率或来源。

**Grok Bot 接法**：有账号授权的Bot可以代为整理你提供的链接摘要并输出标准CSV；本地脚本负责去重、分类和导出。机器人不能执行本地代码时，仍可遵循SKILL.md手工整理。

默认无网络请求，无账号授权，无API Key。MIT · [@0xMulight](https://github.com/0xMulight)
