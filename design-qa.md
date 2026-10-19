# Butterfly 风格预览检查

final result: passed

本次为现有 Hugo 博客的风格改版预览，参考 Butterfly 的顶部导航、图片横幅与卡片布局；不是对 Butterfly 官网的逐像素复刻，也未迁移到 Hexo。

## 视觉证据

截图目录：`/home/lvc/.codex/visualizations/2026/10/19/01a15240-272c-7192-af6c-17d782893dd3/hanlin-preview/`

- 参考：`02-butterfly-home.png`，来自 https://butterfly.js.org/，首页顶部、默认主题，1271 × 715 像素。
- 实现：`03-desktop.png`，http://localhost:1313/，浅色首页顶部，1265 × 791 像素；请求的 CSS 视口为 1280 × 800。
- 同一输入并排对照：`comparison.png`。两张截图等比缩放并填充至 1280 × 800，未裁掉页面内容。截图实际尺寸与请求视口存在浏览器边界差异，故不进行逐像素差异判断。
- 手机：`06-mobile.png`，请求的 CSS 视口为 390 × 844；已检查标题换行、导航、专题入口、列表和搜索页无横向溢出。
- 文章页：`05-article.png`，占据栅格地图构建文章。
- 深色模式：`04-dark.png`。
- 局部检查：原始桌面和手机截图中已直接检查导航文字、外观按钮、卡片摘要与文章目录；本次是风格参考，不需要对照字体字距的像素裁切。

## 五项视觉检查

- 字体：使用本地系统中文与拉丁字体，移除外部 Google Fonts 请求；标题、正文、摘要层级清楚，手机标题自然换行。
- 布局：移除左侧固定栏，桌面采用内容与右侧资料栏；手机隐藏次要资料栏；首页专题入口已按反馈移除，分类保留在导航与侧栏中。
- 色彩：浅灰背景、白色卡片与青蓝强调色；深色模式采用独立的背景和文字色变量，提供可见键盘焦点。
- 图片：本地 WebP 山景横幅约 121 KB，1920 × 640；文章列表不再自动放大正文截图，头像沿用现有资源。
- 文案：使用真实笔记、真实分类数量和阅读时间；首页优先展示 SLAM 相关文章，不把同步时间包装成最近更新。

## 修复与复查记录

1. 首页与资料栏顶部不齐：去掉 Stack 默认的主内容额外顶部间距；`03-desktop.png` 复查对齐。
2. 手机专题块换行过碎、外观按钮偏左：简化手机专题文案，修正按钮自动外边距；`06-mobile.png` 复查通过。
3. 深色模式外观图标消失：同时提供主题已有的左右切换图标；深色切换可用。
4. Markdown 图片相对地址忽略源目录大小写：渲染时依据 source.path 生成静态图片地址，代表文章图片正常加载；静态检查覆盖 377 个本地图片路径。
5. 文章标题重复、目录项目有双层列表标记：保留原正文标题锚点，去掉重复显示，简化目录样式；`05-article.png` 复查。
6. 固定导航遮住目录定位：加入导航高度偏移；点击第二节后目标标题距视口顶部约 94.9px，导航高度 75px，复查通过。为加载新建的脚本资源，已重启 Hugo 预览服务。

## 功能与构建

- Hugo 完整生产构建通过：132 个页面，104 篇笔记；生成文件另存于忽略目录 `resources/qa-build/`。
- 桌面搜索 SLAM 返回 13 项，手机搜索 Eigen 返回 7 项。
- 分类入口、首页第二页（8 篇）、文章入口、目录链接和深浅色切换均已浏览器验证。
- 检查浏览器控制台，未发现本次改动引入的 JavaScript 错误；曾有上游目录脚本的调试日志，修复重复标题后不影响操作。
- `git diff --check` 通过。未修改主题子模块或笔记子模块，未提交、未发布。

## 范围外的内容问题

- 已有原笔记 `notes/Algorithm/本质矩阵基础矩阵的自由度及其解法.md:355` 使用 `.y/media/GetImage65.jpeg`，而实际图片位于 `media/GetImage65.jpeg`。377 个本地图片路径中仅此项未找到；这是原笔记路径笔误，本次未修改笔记子模块。
- 文章日期仍沿用现有同步脚本生成逻辑；未迁移日期数据。部分正文自身存在残缺 Markdown，未在外观改版中改写。
- 公式及代码复制沿用 Stack 实现，未逐篇审查所有数学公式和源笔记内容。
- 上游 Stack 使用 libsass，当前 Hugo 会给出弃用提示，构建成功。

## 图像素材

横幅：`static/img/mountain-hero.webp`。使用内置 Image Gen 生成，再压缩为本地 WebP。

生成提示词：Create one landscape photograph asset for a personal software engineer technical blog hero. Wide panorama 3:1 ratio, 1920x640 if possible. Photorealistic layered alpine mountains with deep forest-covered ridges, distant hazy blue mountains, soft peach dawn light at upper horizon, calm muted teal and blue palette, fine natural detail, cinematic editorial landscape photography, no people no buildings no logos no text no interface. Center area has gently shaded mountain slopes suitable for white heading text overlay. Main mountains in lower two thirds, sky upper third. Sophisticated tranquil outdoors mood.


## 本轮反馈：移除专题入口与图片放大

- 移除首页算法与 SLAM、C++、Linux 三个专题跳转块，同时清理对应样式。
- 文章页使用本地原生 dialog 预览图片，不依赖 PhotoSwipe CDN，也不要求静态图片有构建时尺寸。
- 图片可点击打开预览，再次点击图片或点击“放大细节”放大，可滚动查看细节；提供适应屏幕、关闭按钮与 Esc 关闭。
- 支持键盘聚焦图片入口；关闭后焦点回到原图片按钮，恢复页面滚动。已有指向其他内容的图片链接保留其原有行为。
- 桌面与 390 × 844 手机视口验证：打开、放大、适应屏幕、关闭正常；手机放大后可横向滚动查看细节。Esc 关闭与焦点恢复已验证。浏览器错误日志为空。
- Hugo 生产构建与 git diff --check 通过。
- 证据：同一截图目录中的 `07-home-simplified.png`、`08-image-viewer.png`、`09-image-viewer-mobile.png`。
- 本轮 final result: passed

## 本轮：八分类与本地最新笔记迁移

- 子仓库从本地源更新到 `7b7ddec` 后，迁移为八个主分类和共享 media；保留既有外观及用户修改过的个人文案。
- 浏览器分类页显示 106 篇、8 个分类，分类名称和计数与同步结果一致。
- 搜索 cuVSLAM 得到最新笔记；旧占据栅格地图文章 URL 自动跳转到 robotics 新地址。
- 代表文章前三张图正常加载到 `/notes/media/Algorithm/`，图片放大与关闭正常。
- 控制台仅观察到上游 TOC 的 debug 日志，没有本轮引入的脚本错误。
- 证据：既有截图目录下 `10-eight-categories.png`。完整迁移与完整性验证见 `docs/note-migration.md`。
- 原先记录的 `.y/media/GetImage65.jpeg` 源路径笔误已修复；不再属于当前未解决项。
- 本轮 final result: passed


## 本轮：论文阅读分类与 98 篇迁移

- 新增论文阅读分类，98 篇正文、423 张原图、471 张表格与 3,270 处正文公式；全站 204 篇、9 个分类。
- 分类页显示论文阅读 98，搜索 NavGPT-3 返回相应文章。
- NavGPT-3 图片点击放大、关闭与目录锚点正常；OVSegDT 的 65 处公式全部渲染，无 KaTeX 解析错误。
- 390×844 手机视口验证公式区域，页面没有横向溢出；最终截图使用恢复后的正常桌面视口交付分类预览。
- 全部 98 个生产输出页面经与主题同版本 KaTeX auto-render 做 DOM 校验，成功渲染 3,270 处公式，与来源清单逐篇一致。源站六处公式语法兼容修正已记录；HTML 包装与 passthrough 防止小于号、等号和转义字符被 Markdown/HTML 改写。
- 图片真实性与 SHA-256 校验、1,008 个源本地引用、3,277 个输出正文本地链接及锚点校验通过。10 项测试和 Hugo 生产构建通过。
- 证据：既有截图目录 `11-paper-category.png`、`12-paper-image-viewer.png`。
- 完整范围与维护步骤见 `docs/paper-reading-import.md`。未提交、未推送、未部署。
- 本轮 final result: passed

## 本轮：首页完全随机探索

- “探索笔记”每次进入、刷新或从往返缓存恢复时，从全部已发布笔记中等概率抽取 8 篇；同批无重复，两批间允许重复。移除固定置顶与首页分页。
- “换一批”原地替换卡片，保留焦点，支持键盘 Enter；状态区向屏幕阅读器提示换批结果。无脚本时仍有 8 篇可读卡片及“全部”入口。
- 204 张候选卡片使用 Hugo 真实文章链接，静态检查目标均存在；候选 URL 无重复。首页 HTML 约 268 KiB，不下载文章全文或依赖外部请求。
- 浏览器验证点击、键盘换批、重新加载与返回首页均重新抽取；每批 8 篇且不重复。全部笔记仍显示 26 页，首页不显示分页。
- 手机视口检查按钮最小高度 44px，可点击，页面宽度与滚动宽度一致，没有横向溢出；已恢复桌面视口。控制台错误为空。
- Hugo 生产构建和 git diff --check 通过；沿用现有主题 libsass 弃用提示。
- 截图：既有预览目录 `14-home-random-notes.png`。
- 开发分支：`lvcheng/feature/random-home-notes`。保留此前论文导入成果，未提交、推送或部署。
- 本轮 final result: passed

## 本轮：Butterfly 整屏封面与向下阅读

- 视觉目标：Butterfly 首页的整屏背景、居中文案、透明顶部导航与底部下滑箭头；沿用当前博客的个人文案、导航内容与随机探索功能。
- 背景直接引用示例站当前地址 `https://oss.012700.xyz/butterfly/2024/10/index.jpg`，未将素材下载或复制到仓库，首页页脚标注来源。未将主题代码许可推定为图片许可。外部图加载失败时回退到既有本地山景图。
- 证据位于既有预览目录：参考 `15-butterfly-source.png`（1271×715）、实现 `16-fullscreen-home.png`（1265×712）、滚动后导航 `17-home-after-scroll.png`，完整首屏并排比较 `18-cover-comparison.png`。两张首屏像素比接近 16:9，比较时分别归一到 640×360、拼为 1280×360；本轮比较范围覆盖完整首屏，无需额外局部裁图。
- 字体与文案：沿用本站系统字体、个人标语和已有导航；与示例站标题名称、英文小字、广告的差异是有意保留本站身份及功能。标题居中，手机正常换行。
- 布局与间距：桌面首屏 720px 与视口高度一致；手机 390×844 测试下文档内容宽 375px，封面高 844px，无横向溢出。箭头键盘 Enter 后笔记顶部约 105px，位于约 85px 导航下方。
- 图片与颜色：使用同一原图、居中 cover 裁切，图片已加载（naturalWidth 2449）；首次比较发现本站遮罩 0.25 明显偏亮（P2），修正为参考实际的黑色 0.6 遮罩后重新截图、并排比较，通过。保留本站浅色/深色阅读区配色。
- 交互：点击下滑箭头后笔记顶部约 95px，导航底部约 75px；滚动离开封面后导航变为实色。随机换批仍显示 8 篇，状态提示正常。其他页面导航沿用原样；支持减少动态效果偏好。
- 构建：Hugo 生产构建与 git diff --check 通过，仅有既有 libsass 弃用提示。浏览器错误日志为空；未主动模拟外部图片断网，回退分支由代码核对。
- 最终无未解决的 P0/P1/P2 问题。代码位于开发分支 `lvcheng/feature/fullscreen-scroll-home`，未提交、推送或部署。
- final result: passed
