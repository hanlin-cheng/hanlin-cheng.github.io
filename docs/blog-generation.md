# 博客生成与笔记维护规则

供维护本仓库的 agent 使用。每次任务开始由 `AGENTS.md` 引导先读本文件；两个仓库的 README 面向读者，不放 Agent 入口、维护流程或提交授权说明。新增笔记先看“新增笔记流程”；修改生成机制时再阅读后续章节。以下描述的是当前代码行为，不代表已经实现的改进计划。

## 1. 项目与内容边界

- 本仓库是 `hanlin-cheng.github.io`，使用 **Hugo Extended + hugo-theme-stack**，不是 Hexo。
- Butterfly 仅作为当前外观参考；不要安装 Hexo 或直接替换为 Hexo 的 Butterfly 主题。
- `notes/` 是独立 Git 子模块，来源为 `hanlin-cheng/slam-study-note`。
- `themes/hugo-theme-stack/` 也是独立子模块；根目录同路径模板和资源用于覆盖主题。
- [hugo.yaml](../hugo.yaml) 是常规 Hugo 命令当前使用的主配置。根目录还有 [config.yaml](../config.yaml) 副本，当前内容一致；调整共同设置时保持一致，除非任务明确要求合并配置。
- [scripts/sync_notes.py](../scripts/sync_notes.py) 决定哪些笔记可发布以及如何生成元数据；`params.noteSubmodulePath` 不会改变脚本中硬编码的 `notes/` 路径。

内容流转：

```text
notes/<分类目录>/*.md 与附件
  → python3 scripts/sync_notes.py
  → content/notes/：Markdown + 自动生成的 YAML front matter
  → static/notes/：图片、PDF 等附件
  → static/search-index.json：额外的标题与路径索引
  → hugo --minify
  → public/：可部署静态网页、附件和 Hugo 搜索 JSON
  → GitHub Actions 部署 GitHub Pages
```

`content/notes/`、`static/notes/`、`static/search-index.json`、`public/`、`resources/` 已被 `.gitignore` 忽略。人工维护页面位于 `content/search/`、`content/archives/`、`content/categories/`，不属于笔记同步清理范围。

## 2. 新增笔记流程

1. 先读根目录 [AGENTS.md](../AGENTS.md)，检查父仓库和笔记子模块的工作区状态，保留已有改动。
2. 确认 `notes/` 已初始化且实际包含 Markdown；不要对空子模块目录直接执行同步，因为脚本会清理现有生成结果。
3. 阅读子仓库 [AGENTS.md](../notes/AGENTS.md) 和 [CONTRIBUTING.md](../notes/CONTRIBUTING.md)，在 `notes/` 下已有分类目录中新建 Markdown，图片放在共享 `notes/media/<文章名>/` 中。不要修改生成后的笔记副本。
4. 第一处一级标题应是完整文章名；正文分节使用二级及更低级标题。尽量不在文章名前添加序号或 Markdown 加粗符号。
5. 在 `notes/README.md` 对应分类添加新文章的相对链接。每次新增、删除、移动或重命名笔记/附件，都必须同时核对更新子仓库索引与引用、博客分类映射及地址兼容映射；已有分类自动收录文章，无需逐篇修改同步脚本。附件只在正文引用，不在 README 新增“参考资料”分组。
6. 从博客根目录依次执行 `python3 scripts/check_note_links.py`、`python3 scripts/sync_notes.py`、`hugo --minify`，检查 README 覆盖全部可发布 Markdown，且无遗漏、重复或失效链接；验证新文章、分类/全部笔记入口、搜索结果、正文图片和图片放大操作。首页随机抽取，不以首页是否立即出现新文章判断收录成功。
7. 交付时说明改动位于哪个仓库、验证结果及未完成项；未获明确授权时不提交、不推送、不发布。

子仓库与博客联动是每次内容增删改的完成条件，不能只新增源文件。若从独立笔记仓库开始工作，应定位关联博客工作区并完成上述流程；无法访问时明确记录博客侧待办。“同时更新”不意味着每次都要修改博客模板或提交 Git；生成结果仍忽略，正式发布时需在用户授权后先提交推送子仓库，再更新父仓库的子模块指针。

只读状态检查：

```bash
git status --short --branch
git submodule status
git -C notes status --short --branch
rg --files notes -g '*.md'
```

子模块缺失时可初始化到父仓库记录的版本。执行前检查已有子模块改动；不要为了预览擅自更新到远端最新提交：

```bash
git submodule update --init --recursive
```

新增示例，文件位于 `notes/robotics/新的算法笔记.md`：

```markdown
# 新的算法笔记

用几句话说明问题、适用范围和结论。

## 原理

正文内容。

![算法示意图](../media/新的算法笔记/new-algorithm-overview.png)

## 实现与验证

实现步骤、使用方法和验证结果。
```

配套图片应存在于 `notes/media/新的算法笔记/new-algorithm-overview.png`。当前同步脚本会自行生成 YAML front matter，**不会解析、合并源笔记中已有的 front matter**；不要通过给源笔记添加 YAML 来尝试设置日期、标签或置顶。

## 3. 分类与目录规则

仅同步脚本 `SECTIONS` 中列出的九个顶层目录，名称区分大小写：

- `math` → 数学基础
- `robotics` → SLAM 与机器人
- `ros` → ROS 与中间件
- `cpp` → C++ 开发
- `engineering` → 开发工具与工程实践
- `linux` → Linux 与嵌入式
- `qt` → Qt 开发
- `misc` → 应用与杂记
- `papers` → 论文阅读

每篇笔记只有一个由顶层目录生成的主分类，嵌套文件夹不会自动生成子分类。按文章核心问题归类，安装、运行、命令等是文章类型，不另作主分类。具体边界见 [笔记子仓库维护约定](../notes/CONTRIBUTING.md)。

图片集中在 `notes/media/`。迁移图片保留原目录命名空间（如 `media/Algorithm/`），这不是主分类；新增图片推荐 `media/<文章名>/`。根目录 `media/` 只复制附件，不发布为文章分类。

Markdown 同步跳过 `.git`、`.obsidian`、`.agents`、`.codex` 目录。附件复制排除 `.md`、`.whl`、`.pyc`，覆盖上述分类目录及共享 `media/`。PDF 等参考文件放在其所属分类下，所有公开附件都需要核对是否适合发布。

## 4. 同步脚本的实际行为

脚本先检查至少存在一篇可发布笔记，避免空子模块清空生成结果；正常同步时会删除并重建 `content/notes/`、`static/notes/` 和 `static/search-index.json`，不能在这些位置保存需要长期保留的编辑。

生成的元数据包括：

- `title`：正文第一处匹配 `# 标题` 的行，没有则使用文件名。
- `date`：**本次同步时的 UTC 时间**，不是原文创建时间或 Git 提交时间；全量同步会重写所有文章日期。
- `draft: false`：匹配分类范围的 Markdown 默认全部发布，没有源笔记草稿开关。
- `weight`：相对路径 SHA-1 的前六位转换成整数，用于稳定权重；并非编辑人员设置的优先级。
- `categories`：对应顶层目录的中文分类。
- `source.path`：相对于 `notes/` 的源文件路径，保留目录大小写，用于图片解析与来源定位。
- `image`：按正文顺序匹配本地 Markdown 或 HTML 图片；若没有，仍会尝试分类目录自身的 `media/`。共享图片目录不会被随机用作其他文章的封面。
- `aliases`：从 `data/note-migration.json` 的 `legacy_urls` 读取旧文章地址，Hugo 为迁移后仍存在的文章生成兼容跳转。

自动封面选择不会检查图片是否适合当封面。当前定制首页使用纯文字摘要卡片，文章头部也不展示自动封面，但元数据仍可能用于分享卡片、搜索数据等位置。

路径解析工具为 `scripts/note_links.py`，识别本仓库常用的 Markdown、HTML、引用式和 wiki 链接，跳过代码块与行内代码；它不是完整的 CommonMark 解析器。同步时规范化旧 media 写法，并将 HTML 本地链接转换为基于 `source.path` 的站内地址。它不会提取原始日期、生成标签或自动修复所有源文件错误。

## 5. 图片、附件与 URL

- 推荐用标准 Markdown 图片语法 `![说明](../media/<文章名>/图片.png)`，严格匹配文件名大小写。
- [layouts/_markup/render-image.html](../layouts/_markup/render-image.html) 根据 `source.path` 的父目录解析相对地址，并清理 `..` 路径段。
- 例：`robotics/文章.md` 中的 `../media/Algorithm/a.png` 指向 `/notes/media/Algorithm/a.png`。
- 静态附件保留源文件大小写，不要根据文章 URL 将图片目录统一转换为小写。
- 原始 HTML 不经过 Markdown 渲染钩子；同步脚本会处理 HTML 标签中的本地 `src`/`href`，仍需在浏览器验证。
- [layouts/_markup/render-link.html](../layouts/_markup/render-link.html) 将普通 Markdown 的 `.md` 目标解析为 Hugo 页面的真实 `RelPermalink`，其他附件链接解析为 `/notes/` 下的静态地址，并保留查询参数和锚点。
- 不依赖 Obsidian 专属图片嵌入语法；源笔记统一使用标准 Markdown。
- `uglyURLs: true` 下文章通常为 `/notes/<分类>/<文件名>.html`。实际 URL 以 Hugo 输出为准，中文及括号等标点可能被规范化。
- 移动或重命名文章要同步修改图片、其他笔记和 README 引用；公开地址变动还需维护迁移清单中的 `legacy_urls`。
- 历史映射保存在 [data/note-migration.json](../data/note-migration.json)，迁移过程与验证记录见 [分类迁移记录](note-migration.md)。不把源仓库已删除文章重新加入兼容映射。

图片放大由 [assets/ts/custom.ts](../assets/ts/custom.ts) 与 [photoswipe.html](../layouts/_partials/article/components/photoswipe.html) 中的本地原生 `dialog` 实现。正文中未被链接或按钮包裹的图片会自动获得放大入口，支持细节缩放、关闭按钮、空白区关闭及 Esc 关闭；已有图片链接保留原有行为。不要误以为文件名为 `photoswipe.html` 就仍在使用外部 PhotoSwipe CDN。

## 6. 页面生成与样式覆盖

优先修改以下根目录文件，不直接改主题子模块：

- [layouts/baseof.html](../layouts/baseof.html)：顶部导航、首页整屏封面和公共布局。
- [layouts/home.html](../layouts/home.html)：首页随机笔记列表、“换一批”按钮与全部笔记入口。
- [layouts/_partials/helper/pages.html](../layouts/_partials/helper/pages.html)：页面集合与首页无脚本时的标题排序。
- [layouts/_partials/helper/note-title.html](../layouts/_partials/helper/note-title.html)：展示标题清理；去除 Markdown 格式，超过 60 个字符时回退到文件名。
- `layouts/_partials/article-list/default.html`：首页文字摘要卡片。
- `layouts/_partials/sidebar/right.html`：资料、搜索、分类和文章目录。
- `layouts/_partials/article/components/`：文章头部、正文、元信息与图片预览。
- [assets/scss/custom.scss](../assets/scss/custom.scss)：站点样式、响应式、深色模式和图片预览样式。
- [assets/ts/custom.ts](../assets/ts/custom.ts)：首页随机换批、目录滚动时避让固定导航、图片放大交互。
- 首页当前按用户要求直接引用 Butterfly 示例站背景 `https://oss.012700.xyz/butterfly/2024/10/index.jpg`，未下载到仓库；`static/img/mountain-hero.webp` 保留为加载失败时的本地回退图，`assets/img/avatar.JPG` 为头像。封面图来源在首页页脚注明。
- `i18n/zh-cn.toml`：当前语言代码对应的中文翻译补充。

首页“探索笔记”从全部已发布笔记中等概率随机抽取 8 篇，每次进入首页、重新加载或从浏览器往返缓存恢复时重新抽取；点击“换一批”仅替换卡片，不重载页面。使用 Fisher–Yates 洗牌，同一批内无重复，不设置分类权重或固定置顶，不刻意排除上一批，因此两批间可以重复。

`layouts/home.html` 内的惰性 `<template>` 保存所有笔记卡片，`assets/ts/custom.ts` 克隆随机选中的 8 张；只包含标题、摘要和站内链接，不请求全文或依赖搜索索引。新增笔记经同步和 Hugo 构建后自动进入抽取范围。JavaScript 不可用时按标题展示前 8 篇且隐藏换批按钮，仍可通过“全部”入口浏览完整列表。

首页不再显示分页；`layouts/_partials/helper/paginator.html` 跳过首页，避免主题标题模板隐式生成首页分页。全部笔记、分类等完整列表仍按现有规则分页，每页 8 篇。

标题展示清理不回写源笔记或生成元数据，搜索和分享数据仍可能使用原始 `.Title`。

首页采用与视口等高的整屏封面，文案居中，底部无文字箭头链接到 `#notes`，支持键盘和减少动态效果偏好。首页导航初始透明，封面底部滚过导航高度后切换为实色；其他页面仍使用原导航。背景图是外部资源，地址失效或加载失败时由 `assets/ts/custom.ts` 切换到本地回退图。

已确认的界面约定：保留分类导航和详细分类列表；不要重新加入首页“算法与 SLAM / C++ / Linux”专题跳转块，也不要重新加入横幅中的“探索我的笔记”入口。

## 7. 搜索索引与构建

当前存在两份不同用途的索引：

- `static/search-index.json`：同步脚本生成，仅含标题、分类、路径和源位置，不含全文；其中路径未经 Hugo 最终 URL 规范化，不应直接替代真实文章链接。
- `/search.json`：Hugo 根据 `content/search/index.md` 的 JSON 输出配置及主题 `layouts/page/search.json` 生成，包含文章标题、实际 `RelPermalink`、日期和正文；**现有搜索页使用这一份全文索引**。

新增笔记后必须同步并构建，不能只更新手写静态索引。只改样式或模板时通常不必重跑同步，避免无意义地重写全部文章日期。

需要 Python 3 与 Hugo Extended，版本至少满足当前 Stack 要求；当前项目要求的最低版本为 0.157.0，后续如升级主题，应重新核对版本要求。

```bash
# 新增、更新笔记后，在博客根目录运行
python3 scripts/sync_notes.py
hugo --minify

# 本地预览，默认地址 http://localhost:1313/
hugo server --bind 127.0.0.1 --port 1313 --disableFastRender
```

若已有预览服务运行，不重复启动占用同一端口的服务。新增资源后若页面仍使用旧脚本或模板，先核对输出，再考虑重启服务并刷新。

## 8. 子模块与发布

[.github/workflows/pages.yml](../.github/workflows/pages.yml) 在推送 `main` 或手动触发时执行：检出父仓库及子模块记录的版本 → 安装 Hugo Extended → 同步笔记 → 构建 → 上传 `public/` → 部署 GitHub Pages。

CI 不会自动跟踪笔记子模块的远端最新提交。本地未提交的笔记修改也不会出现在 CI 中。需要正式发布笔记时，先确保笔记仓库中的内容有可获取的已提交版本，再更新父仓库记录的子模块指针。**提交、推送与部署均需用户授权**，不能因为文档描述了流程而自动执行。

不要默认执行 `git submodule update --remote`，它会改变子模块版本，可能引入与本次任务无关的内容。

## 9. 按改动范围验证

- 仅文档：核对规则与代码一致，检查引用文件存在，运行 `git diff --check`，不必重跑笔记同步。
- 新增笔记或图片：先运行 `python3 scripts/check_note_links.py`，再同步、生产构建；检查新文章和分类可访问、搜索能找到、图片无 404 且可放大，特别检查中文路径与大小写。
- 修改同步机制：运行 `python3 -m unittest discover -s tests -v`，并检查代表性笔记、共享图片、PDF、跨笔记链接、清理保护及旧地址跳转。
- 修改外观或交互：构建并在浏览器检查桌面、手机宽度，按范围验证导航、分页、搜索、目录、深色切换或图片预览；相关记录见 [design-qa.md](../design-qa.md)。

当前已知限制：全量同步时间被当作文章日期；本次迁移已修复 `.y/media/GetImage65.jpeg` 路径笔误并规范了一处 Obsidian 图片引用，少量原有残缺 Markdown 仍待按内容任务处理。遇到这些问题应区分“原笔记内容问题”和“生成机制问题”，不要通过改写生成文件掩盖问题。

## 10. 论文阅读导入与维护

论文阅读分类源目录为 `notes/papers/`，配图位于 `notes/media/papers/<文章文件名>/`。已授权迁移的 98 篇来源、目标路径、图片 SHA-256 和公式兼容修正记录在 `data/paper-reading-sources.json`，迁移范围与验证见 [论文阅读迁移记录](paper-reading-import.md)。

普通新增论文笔记直接按第 2 节流程操作，不依赖原站或导入依赖。只有需要重建这批迁移文章时，才安装 `scripts/requirements-paper-import.txt` 并运行 `scripts/import_paper_readings.py`。该脚本会覆盖带对应来源标记的已导入文件，并重建 README 论文索引；**重跑前先保留迁入后的人工作业**，不允许覆盖无对应标记的现有笔记。源 HTML 与图片缓存位于忽略的 `resources/paper-import-cache/`，失败后可使用缓存继续。

Goldmark 启用 `\(...\)` 的 passthrough，保留行内公式转义。导入公式保留 LaTeX，用 `paper-math` 的 HTML span/div 包装并转义 HTML 字符，由主题现有 KaTeX 渲染 `\(...\)` 和 `\[...\]`。这样避免公式中的 `<` 被当成 HTML、独立 `=` 行被当成 Markdown 标题；复杂表格保留 HTML，表格内公式同样检查。PDF 和中文完整译文链接保留源站地址，这批迁移数量只计算阅读报告。
