# Agent 工作规则

本文件适用于博客仓库；进入子模块前还应检查其中是否存在额外的 `AGENTS.md`。

- 始终使用中文回答，改动前评估不必要的风险。
- 未经用户明确要求，不提交 commit，不推送，不发布。
- 开始新的开发任务时，先检查 Git 状态，再创建 `lvcheng/feature/**`、`lvcheng/bugfix/**` 或 `lvcheng/improvement/**` 开发分支；延续同一任务时沿用现有分支，保留未提交成果。
- 上下文恢复或任务中断后，先检查当前状态，从未完成处继续，不重复生成已有文件。
- 不生成 canvas 文件。
- 新增或修改笔记、分类、同步脚本、页面模板、图片或部署配置前，阅读 [博客生成与笔记维护规则](docs/blog-generation.md)。
- 笔记源位于 `notes/` 子模块；不要直接维护会被重建的 `content/notes/`、`static/notes/`、`static/search-index.json` 或 `public/`。
- 站点当前为 Hugo Extended + Stack，外观参考 Butterfly；不要误按 Hexo 项目操作。
- 博客定制优先放在根目录 `layouts/`、`assets/`，不要直接修改主题子模块。
- 生成逻辑发生变化时，同步更新上述规则文档；视觉变更还应更新相关预览验证记录。
- 当前笔记使用八个主分类与共享 `notes/media/`；移动笔记前检查子仓库 `CONTRIBUTING.md`，同步修改相对链接、README 与迁移映射，完成后运行链接检查。
