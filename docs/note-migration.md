# 笔记更新与分类迁移记录

## 内容基线

本次读取 `/home/lvc/my_code/slam-study-note` 的本地 `master` 最新提交 `7b7ddec`，通过本地 Git fetch 更新博客的 `notes/` 子模块，再在子模块工作区移动文件和修改链接。原始本地源仓库保持不变。

迁移开发使用 `lvcheng/improvement/note-taxonomy` 分支，既有博客外观与文档改动全部保留。随后用户明确授权合并并推送主分支；笔记迁移提交为 `68d9480`，已快进合并并推送至笔记仓库 `master`。博客将以该提交作为子模块指针合并至 `main`。

最新源仓库有 106 篇笔记。相对旧版新增 5 个 Markdown、移除 3 个 Markdown，并更新了 README 和一篇已有笔记。源仓库删除的 `command/LIO-SAM运行.md`、`command/Orb-slam2运行.md`、`slam_config/xavier装机文档.md` 没有重新添加。

## 八个主分类

- 数学基础 `math/`：15 篇。
- SLAM 与机器人 `robotics/`：28 篇。
- ROS 与中间件 `ros/`：9 篇。
- C++ 开发 `cpp/`：27 篇。
- 开发工具与工程实践 `engineering/`：13 篇。
- Linux 与嵌入式 `linux/`：8 篇。
- Qt 开发 `qt/`：4 篇。
- 应用与杂记 `misc/`：2 篇。

两个名为 `Ubuntu-xavier.md` 的源文件分别记录环境配置与常用命令，迁移为 `linux/Ubuntu-xavier.md` 和 `linux/Jetson常用命令.md`，没有覆盖或合并内容。

## 文件与链接

- 414 个附件全部保留，逐文件 SHA-256 与最新源仓库一致。
- 图片集中在 `media/<原目录>/`；保留历史命名空间避免同名冲突，笔记使用 `../media/...` 相对路径引用。
- 6 个 PDF 参考文件归入对应的数学或机器人分类。
- 重写真实 Markdown/HTML/wiki 链接时跳过代码示例，106 篇笔记的代码块和行内代码与源版本一致。
- 修复原来的 `.y/media/GetImage65.jpeg` 路径笔误；将协方差笔记的 Obsidian 图片嵌入规范为标准 Markdown。
- README 重新按八类索引全部 106 篇 Markdown 笔记，保留后续资源、软件和其他章节；按用户反馈移除新增的“参考资料”分组与 PDF 列表，PDF 文件仍保留。
- 更新博客同步脚本、图片与普通链接渲染钩子，使共享图片、HTML 图片、跨笔记链接和附件在生成后仍可访问。
- [迁移清单](../data/note-migration.json) 保存全部新旧路径、源提交与 101 个仍存在旧文章地址的跳转映射。已被源仓库删除的 3 篇不生成跳转；旧的直接附件 URL 没有建立独立兼容层，站内引用已全部更新。

## 验证

已完成以下检查：

```bash
python3 -m unittest discover -s tests -v
python3 scripts/check_note_links.py
python3 scripts/sync_notes.py
hugo --minify
```

- 7 项回归测试通过：带括号/空格的链接、代码保护、HTML/引用/wiki 解析、共享附件复制、分类与 aliases、空笔记目录清理保护。
- 源笔记与 README 的 494 处本地引用均可找到目标。
- 干净构建目录中的 530 个不同站内链接和图片目标全部存在。
- 101 个旧文章跳转文件全部生成。
- 本次不更改日期策略：同步仍会把本次 UTC 时间写为文章日期。

## 之后如何维护

分类边界与源笔记约定见 [子仓库 CONTRIBUTING.md](../notes/CONTRIBUTING.md)；完整生成流程见 [博客生成规则](blog-generation.md)。修改目录时应同时维护源文件引用及旧 URL 映射，不要直接修改生成目录。

父仓库只记录子模块提交指针；发布顺序为先提交并推送笔记仓库，再提交并推送父仓库指针，确保 CI 可以取得对应内容。博客主分支推送后由 GitHub Actions 构建和部署。
