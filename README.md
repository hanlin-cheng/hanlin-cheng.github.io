# SLAM Study Notes Hugo Site

这是一个给 GitHub Pages 使用的 Hugo 静态博客模板，主题使用 [hugo-theme-stack](https://github.com/CaiJimmy/hugo-theme-stack)。推荐维护方式是：

1. 单独创建一个博客仓库，仓库名必须是 `hanlin-cheng.github.io`。
2. 在博客仓库中使用本目录这些 Hugo 文件。
3. 把笔记仓库作为子模块放到博客仓库的 `notes/` 目录。
4. 构建前运行 `python3 scripts/sync_notes.py`，把子模块里的 Markdown 和附件同步到 Hugo 可发布目录。

## 初始化博客仓库

```bash
git clone git@github.com:hanlin-cheng/hanlin-cheng.github.io.git
cd hanlin-cheng.github.io
git submodule add https://github.com/hanlin-cheng/slam-study-note.git notes
git submodule update --init --recursive
```

然后把本 `hugo-site/` 目录下的文件放到博客仓库根目录。

## 本地预览

需要先安装 Hugo Extended `0.157.0` 或更新版本。

```bash
python3 scripts/sync_notes.py
hugo server -D
```

浏览器打开 Hugo 输出的本地地址即可预览。

如果系统包管理器里的 Hugo 版本过旧，Stack 主题会报类似 `function "hash" not defined` 的错误。此时请升级 Hugo Extended 后再预览。

## 更新笔记内容

博客仓库只记录子模块指向的笔记仓库提交。笔记更新后：

```bash
git submodule update --remote notes
git add notes
git commit -m "Update notes"
git push
```

GitHub Actions 会自动构建并部署到 GitHub Pages。

## GitHub Pages 设置

在博客仓库的 GitHub 页面中打开：

`Settings` -> `Pages` -> `Build and deployment` -> `Source`，选择 `GitHub Actions`。

当前配置默认部署到 `https://hanlin-cheng.github.io/`。
