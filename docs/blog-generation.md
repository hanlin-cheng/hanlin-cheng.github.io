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

子仓库与博客联动是每次内容增删改的完成条件，不能只新增源文件。若从独立笔记仓库开始工作，应定位关联博客工作区并完成上述流程；无法访问时明确记录博客侧待办。“同时更新”不意味着每次都要修改博客模板或提交 Git；生成结果仍忽略，正式发布时需在用户授权后先提交推送子仓库，再同步笔记以刷新日期快照，最后提交父仓库的子模块指针与日期快照。

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

Markdown 同步跳过 `.git`、`.agents`、`.codex` 目录。附件复制排除 `.md`、`.whl`、`.pyc`，覆盖上述分类目录及共享 `media/`。PDF 等参考文件放在其所属分类下，所有公开附件都需要核对是否适合发布。

## 4. 同步脚本的实际行为

脚本先检查至少存在一篇可发布笔记，避免空子模块清空生成结果；正常同步时会删除并重建 `content/notes/`、`static/notes/` 和 `static/search-index.json`，不能在这些位置保存需要长期保留的编辑。

生成的元数据包括：

- `title`：正文第一处匹配 `# 标题` 的行，没有则使用文件名。
- `date`：笔记 Git 历史中首次记录该文件的提交时间（跟随重命名），标准化为 UTC；不代表入库前的真实写作时间。
- `lastmod`：笔记已提交历史中的最后变更时间。同步不使用构建时钟，未提交编辑不刷新 lastmod。`scripts/note_dates.py` 管理历史读取与日期快照，`data/note-dates.json` 必须随新增笔记和发布更新一起维护；无 Git 历史或浅克隆时优先使用快照，新文件无历史/快照时首次登记文件 mtime，之后固定。
- `draft: false`：匹配分类范围的 Markdown 默认全部发布，没有源笔记草稿开关。
- `weight`：相对路径 SHA-1 的前六位转换成整数，用于稳定权重；并非编辑人员设置的优先级。
- `categories`：对应顶层目录的中文分类。
- `source.path`：相对于 `notes/` 的源文件路径，保留目录大小写，用于图片解析与来源定位。
- `image`：按正文顺序匹配本地 Markdown 或 HTML 图片；若没有，仍会尝试分类目录自身的 `media/`。共享图片目录不会被随机用作其他文章的封面。
- `aliases`：从 `data/note-migration.json` 的 `legacy_urls` 读取旧文章地址，Hugo 为迁移后仍存在的文章生成兼容跳转。

自动封面选择不会检查图片是否适合当封面。当前定制首页使用纯文字摘要卡片，文章头部也不展示自动封面，但元数据仍可能用于分享卡片、搜索数据等位置。

路径解析工具为 `scripts/note_links.py`，识别本仓库常用的 Markdown、HTML 和引用式链接，跳过代码块与行内代码；它不是完整的 CommonMark 解析器。同步时规范化旧 media 写法，并将 HTML 本地链接转换为基于 `source.path` 的站内地址。它不从正文猜测原始日期，不生成标签，也不会自动修复所有源文件错误。

## 5. 图片、附件与 URL

- 推荐用标准 Markdown 图片语法 `![说明](../media/<文章名>/图片.png)`，严格匹配文件名大小写。
- [layouts/_markup/render-image.html](../layouts/_markup/render-image.html) 根据 `source.path` 的父目录解析相对地址，并清理 `..` 路径段。
- 例：`robotics/文章.md` 中的 `../media/Algorithm/a.png` 指向 `/notes/media/Algorithm/a.png`。
- 静态附件保留源文件大小写，不要根据文章 URL 将图片目录统一转换为小写。
- 原始 HTML 不经过 Markdown 渲染钩子；同步脚本会处理 HTML 标签中的本地 `src`/`href`，仍需在浏览器验证。
- [layouts/_markup/render-link.html](../layouts/_markup/render-link.html) 将普通 Markdown 的 `.md` 目标解析为 Hugo 页面的真实 `RelPermalink`，其他附件链接解析为 `/notes/` 下的静态地址，并保留查询参数和锚点。
- 源笔记仅使用标准 Markdown 链接与图片语法，不维护编辑器专属双链、嵌入或插件配置；链接检查器不再识别 wiki 链接。
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

深色配色以 Butterfly 示例站实际计算样式为准：页面底色 `#0d0d0d`，正文/笔记/侧栏卡片基色 `#121212`（85% 不透明度），实色导航 `#121212`，按钮底色 `#1f1f1f`；按用户的可读性反馈，标题使用纯白，正文、摘要和侧栏主要文字使用白色 90% 不透明度，辅助文字维持 60% 不透明度；这是在参考站黑灰底色上主动提高文字亮度的定制，不要回退到此前正文 70% 的设置。不要恢复旧蓝灰色卡片（`#1f2833`）或青色 GitHub 按钮；浅色模式保持现有配色。

顶部导航为通栏布局，桌面站点名距左侧 36px，末尾控件距右侧 36px，不受正文 1200px 居中容器限制；手机两侧保留 18px，导航可分行。

阅读区使用用户选定的梅里雪山卡瓦格博实景照片（JL Cogburn，CC BY-SA 2.0）。`layouts/baseof.html` 的 `.reading-backdrop` 是不接收点击的固定装饰层，首页封面保持原样。笔记、正文与侧栏等使用 `--card-background` 的阅读卡片底色设为 85% 不透明度（深色 `rgba(18,18,18,.85)`、浅色 `rgba(255,255,255,.85)`），不使用容器 `opacity`，避免文字和图片一起变淡；导航通过独立 `--navigation-background` 保持实色，首页导航仍按滚动状态切换。桌面使用本地 `static/img/meili-reading.webp`，800px 以下使用 `meili-reading-mobile.webp`，由原图等比例缩小并转为 WebP；深色覆盖黑色 38%，浅色覆盖白色 80%，保证阅读对比度。来源、作者、许可和处理说明位于独立的 `content/image-credits/index.md`，公共页脚只展示“图片来源”入口，背景本身不叠加署名。不再加载彩带脚本；旧 vendor 文件及许可证暂保留。

首页副标题“保持好奇，持续前行”在 `layouts/baseof.html` 保留完整静态文案，由 `assets/ts/custom.ts` 实现打字机循环（逐字显示、停顿、逐字删除）；光标闪烁和占位高度位于 `assets/scss/custom.scss`。不依赖外部动画库。系统开启减少动态效果时静态显示，页面隐藏时停止计时，恢复可见后重新播放；屏幕阅读器只读取完整句子，不逐字播报。

首页采用与视口等高的整屏封面，文案居中，底部无文字箭头链接到 `#notes`，支持键盘和减少动态效果偏好。首页导航初始透明，封面底部滚过导航高度后切换为实色；其他页面仍使用原导航。背景图是外部资源，地址失效或加载失败时由 `assets/ts/custom.ts` 切换到本地回退图。

已确认的界面约定：保留分类导航和详细分类列表；不要重新加入首页“算法与 SLAM / C++ / Linux”专题跳转块，也不要重新加入横幅中的“探索我的笔记”入口。

代码块采用简洁编辑器样式：根目录 `assets/ts/code-copy.ts` 覆盖 Stack 的同名模块，由现有主脚本调用；`assets/scss/code-blocks.scss` 由 `custom.scss` 导入。不要直接修改主题子模块，也不要同时启用主题旧复制按钮和另一套工具栏。高亮块与普通 `pre > code` 均增强为单一 `.code-panel`，显示源语言标签（未标注时为“纯文本”）和复制按钮，复制仅取代码的 `textContent`，不包含工具栏。成功/失败都有可访问状态提示，不支持剪贴板 API 时禁用按钮并提示手动复制。

代码面板保持实色，深色 `#191c23` / 工具栏 `#222630`，浅色 `#f6f8fa` / 工具栏 `#edf1f5`，字号 14px、行高 1.65；保留缩进与长行，横向滚动不撑宽页面，超过 560px 时面板内纵向滚动。滚动区域可键盘聚焦；不依赖外部字体或高亮库。无 JavaScript 时仍显示格式化代码，工具栏由 JavaScript 增强；准确语法高亮依赖源 Markdown 围栏语言，不猜测或批量改写旧笔记。

## 7. 搜索索引与构建

当前存在两份不同用途的索引：

- `static/search-index.json`：同步脚本生成，仅含标题、分类、路径和源位置，不含全文；其中路径未经 Hugo 最终 URL 规范化，不应直接替代真实文章链接。
- `/search.json`：Hugo 根据 `content/search/index.md` 的 JSON 输出配置及主题 `layouts/page/search.json` 生成，包含文章标题、实际 `RelPermalink`、日期和正文；**现有搜索页使用这一份全文索引**。

新增笔记后必须同步并构建，不能只更新手写静态索引。只改样式或模板时通常不必重跑同步；笔记同步会保留稳定日期，不再将构建时间写入全部文章。

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

CI 不会自动跟踪笔记子模块的远端最新提交。本地未提交的笔记修改也不会出现在 CI 中。需要正式发布笔记时，先确保笔记仓库中的内容有可获取的已提交版本，再运行笔记同步刷新 `data/note-dates.json`，最后更新父仓库记录的子模块指针与日期快照。**提交、推送与部署均需用户授权**，不能因为文档描述了流程而自动执行。

不要默认执行 `git submodule update --remote`，它会改变子模块版本，可能引入与本次任务无关的内容。

## 9. 按改动范围验证

- 仅文档：核对规则与代码一致，检查引用文件存在，运行 `git diff --check`，不必重跑笔记同步。
- 新增笔记或图片：先运行 `python3 scripts/check_note_links.py`，再同步、生产构建；检查新文章和分类可访问、搜索能找到、图片无 404 且可放大，特别检查中文路径与大小写。
- 修改同步机制：运行 `python3 -m unittest discover -s tests -v`，并检查代表性笔记、共享图片、PDF、跨笔记链接、清理保护及旧地址跳转。
- 修改外观或交互：构建并在浏览器检查桌面、手机宽度，按范围验证导航、分页、搜索、目录、深色切换或图片预览；相关记录见 [design-qa.md](../design-qa.md)。

当前已知限制：Git 日期只能追溯到仓库首次记录文件的提交，未提交编辑不计入 lastmod；本次迁移已修复 `.y/media/GetImage65.jpeg` 路径笔误并规范了一处旧图片引用，少量原有残缺 Markdown 仍待按内容任务处理。遇到这些问题应区分“原笔记内容问题”和“生成机制问题”，不要通过改写生成文件掩盖问题。

## 10. 论文阅读导入与维护

论文阅读分类源目录为 `notes/papers/`，配图位于 `notes/media/papers/<文章文件名>/`。已授权迁移的 98 篇来源、目标路径、图片 SHA-256 和公式兼容修正记录在 `data/paper-reading-sources.json`，迁移范围与验证见 [论文阅读迁移记录](paper-reading-import.md)。

普通新增论文笔记直接按第 2 节流程操作，不依赖原站或导入依赖。只有需要重建这批迁移文章时，才安装 `scripts/requirements-paper-import.txt` 并运行 `scripts/import_paper_readings.py`。该脚本会覆盖带对应来源标记的已导入文件，并重建 README 论文索引；**重跑前先保留迁入后的人工作业**，不允许覆盖无对应标记的现有笔记。源 HTML 与图片缓存位于忽略的 `resources/paper-import-cache/`，失败后可使用缓存继续。

Goldmark 仅对 `\(...\)` 和 `\[...\]` 启用 passthrough，保留公式转义；根目录覆盖 KaTeX 初始化模板，关闭单/双美元自动公式识别，金额与 Shell 符号按普通正文显示。旧笔记的美元公式已迁移到明确的定界符，不要重新开启全局美元识别。导入公式保留 LaTeX，用 `paper-math` 的 HTML span/div 包装并转义 HTML 字符，由主题现有 KaTeX 渲染 `\(...\)` 和 `\[...\]`。这样避免公式中的 `<` 被当成 HTML、独立 `=` 行被当成 Markdown 标题；复杂表格保留 HTML，表格内公式同样检查。PDF 和中文完整译文链接保留源站地址，这批迁移数量只计算阅读报告。


## 11. Markdown 兼容与回归检查

- 数学：行内 `\(...\)`，独立 `\[...\]`；不再支持 `$...$` / `$$...$$` 公式。金额、Shell 的 `$HOME`、`${PATH}`、`$$` 保留为正文。不要对普通正文猜测数学表达式。新内容必须使用明确的公式定界符，现有数学笔记已迁移。KaTeX 仍跳过代码区域，代码中不得改写定界符。
- 目录：`hugo.yaml` 与 `config.yaml` 都显式设为 startLevel=2、endLevel=4，侧栏嵌套目录有缩进。四级标题可定位，五、六级不默认收录。
- 表格：`layouts/_partials/article/components/content.html` 同时包装普通和带属性的 HTML table。`assets/scss/markdown.scss` 设置表格按内容布局、列的最小宽度与长文本换行，宽度超过容器时在表格区域滚动，不挤成竖排、不撑宽页面。`assets/ts/custom.ts` 使用 ResizeObserver，仅给实际溢出的表格显示滑动提示、区域标签和键盘焦点；不要全局 nowrap。
- 行内代码：与代码面板分开配色。浅色深字 `#263445` / 底 `#edf1f5`，深色亮字 `#e1e5ed` / 底 `#242830`；不恢复浅色 `#808080` 的低对比度设置。
- 图片：正文图片等比例、居中、最大宽度 100%，不再统一限制为 650px 高。长技术图保留可读尺寸，点击放大行为不变；不要恢复固定宽高加 contain 形成留白框。
- 展示页源文件为 `content/markdown-demo/index.md`，地址 `/markdown-demo.html`，包含金额、Shell 符号、公式、四级标题、宽表格/带属性表格、列表/脚注、代码和竖图，不属于 notes 随机池，不新增子仓库文章索引。
- 自动回归：`tests/test_markdown_rendering.py` 实际调用 Hugo，在忽略的 resources 临时目录构建，检查目录锚点、金额/变量/公式保留与两种表格包装。配合同步/导入测试运行 `resources/paper-import-venv/bin/python -m unittest discover -s tests -v`。普通生成测试可只运行 test_note_generation 和 test_markdown_rendering；全量测试需要已有的导入依赖环境。
- 外观验证仍需要在浏览器检查深浅色、手机滚动、图片放大及 KaTeX 错误；不能以“链接存在”替代显示验证。笔记子仓库没有专用编辑器配置目录或现用双链，本次删除的是检查/同步链路中的专用兼容分支，并统一维护规则。


论文阅读页面不展示开头的“原文链接”入口；98 篇已统一删除，导入器也不再生成该行。迁移清单与不可见来源标记继续用于溯源、识别已导入文章及防止误覆盖；正文中的论文 PDF、译文和参考资料链接按原内容保留。此调整不增删或改名文章，子仓库 README 的文章入口保持有效。


## 12. 目录、标题与日期维护

- 正文只保留一个文章一级标题，正文分节从二级开始；修正层级时保留章节文字，从而保持既有锚点。改动文章名时联动修改 notes/README.md 的显示标签，不无故更改文件名/URL。不要通过全局替换破坏代码块内的 `#` 示例。
- 手机目录复用主题现有 `.article-toc > details`，不额外添加另一套目录。800px 以下显示、桌面隐藏；提高入口对比度，长目录内部滚动，点击后自动收起，再计算固定导航避让偏移。桌面使用侧栏目录，两者不能重复 id。
- 发布日期与更新日期来自已提交笔记历史，并分别展示。完整历史用 `git log --follow` 追踪重命名；Git 缺失/浅克隆时使用已跟踪的日期快照。`data/note-dates.json` 是生成机制的受版本管理输入/回退数据，不属于忽略的笔记输出。不要用 checkout 时间或当前时间覆盖已有快照。
- 用户授权发布时，先提交笔记，再同步博客以刷新日期快照，之后提交父仓库。CI 已配置 fetch-depth: 0；快照覆盖缺少完整历史的归档构建场景。
- i3DGS 的“新帧匹配”表格行在原 HTML 缓存中也已损坏；当前按同文技术流程重建为单格复杂度和明确的三级筛选说明，不填充未经证实的性能数值。不要重跑导入器覆盖修正后的笔记。
- 日期回归见 `tests/test_note_dates.py`（重命名历史、未提交编辑、归档回退和首次登记稳定性）；Hugo 输出回归同时检查正文无重复 H1、主章节目录、表格公式及代码末尾无残留语言标记。
