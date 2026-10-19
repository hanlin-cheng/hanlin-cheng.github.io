# 论文阅读迁移记录

用户于 2026-10-19 确认这些报告属于本人或已获全文迁移授权。本次从 chengwei920412.github.io 文章页公开目录迁入 98 篇阅读报告，不包含其他栏目。

## 内容与来源

- 正文：`notes/papers/*.md`，每篇保留来源链接；README 新增完整的 98 篇相对链接索引。
- 图片：423 张，位于 `notes/media/papers/<文章文件名>/`，原始文件共 462,224,687 字节（约 441 MiB），最大单文件约 11 MiB；正文使用相对路径，支持现有点击放大功能。
- 结构：保留 471 张表格、2,854 个正文分节标题，以及 3,270 处正文公式。顶部标题采用原站目录的简洁文章名，完整原文标题记录在来源清单。
- 来源清单：`data/paper-reading-sources.json`，包含原文 URL、目标文件、原始标题、源 HTML/图片 SHA-256、公式数量及兼容修正。
- 原文中的 PDF、中文全文译文等附加材料保留源站绝对链接，未作为额外报告下载；报告正文与配图已本地保存。
- 分类：`papers` 映射为“论文阅读”；站点合计 204 篇笔记、9 个分类。文章页面日期沿用现有同步机制，为同步日期，不代表论文发表时间。

## 公式兼容

公式保留 LaTeX，以转义 HTML 字符后的 span/div 包装，使用 `\(...\)` 与 `\[...\]` 定界，避免 Markdown/HTML 把小于号和独立等号行误解析为标签或标题；Goldmark 对行内 `\(...\)` 启用 passthrough；由主题现有 KaTeX 0.16.9 渲染。源站 6 处公式需兼容修正，均记录在来源清单：

- Spatial-Nav-100K、NaVIDA 的 `\textsc` 改为 `\text`，保留文字内容。
- OVSegDT 的三处 `H_\max` 添加下标分组，改为 `H_{\max}`。
- SLAM3R 的集合表达式补齐左侧集合花括号的转义。

原始 HTML 保留在忽略的本地缓存中，源站内容未修改。

## 重跑与日常维护

日常新增笔记遵循 `docs/blog-generation.md`，不需要导入环境。需要重新迁入这 98 篇时：

```bash
python3 -m venv --system-site-packages resources/paper-import-venv
resources/paper-import-venv/bin/pip install -r scripts/requirements-paper-import.txt
resources/paper-import-venv/bin/python scripts/import_paper_readings.py
python3 scripts/check_note_links.py
python3 scripts/sync_notes.py
hugo --minify
```

导入脚本只允许显式授权的来源清单，最多 4 并发，失败可通过 `resources/paper-import-cache/` 缓存继续。不覆盖无匹配来源标记的已有文件；会重建带匹配标记的文章及 README 论文目录，重跑前必须检查并保留迁入后的人工修改。缓存、虚拟环境与验证依赖不提交，普通构建也无需联网获取源站内容。

## 验证

- 98 个来源 URL 唯一，98 篇正文全部生成，423 张图片内容校验与 SHA-256 校验通过。
- 笔记和 README 共 1,008 个本地引用检查通过，缺失 0。
- 98 个生产输出页面的正文中 3,277 个本地链接/图片路径检查通过，缺失 0；页内锚点检查通过。
- 使用与主题一致的 KaTeX auto-render 对全部 98 个最终 HTML 正文做 DOM 渲染校验：3,270 处公式全部渲染成功，与来源清单正文公式数量逐篇一致，解析错误 0。
- 导入转换、公式兼容、HTML/Markdown 语法保护、覆盖保护和既有生成机制共 10 项测试通过。
- Hugo 生产构建成功；仅有既有主题 libsass 弃用提示。
- 浏览器分类显示“论文阅读 98”，搜索 NavGPT-3 返回对应报告；正文公式、表格、图片放大与关闭正常。390×844 手机视口未发现页面横向溢出。
- 截图证据见 `design-qa.md` 本轮记录。

本次没有提交、推送或部署；正式发布前需按子仓库先提交、主仓库更新子模块指针的流程处理，并由用户明确授权。
