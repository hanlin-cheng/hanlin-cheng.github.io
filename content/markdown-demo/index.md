---
title: "Markdown 排版示例"
slug: "markdown-demo"
---

## 公式与普通符号

两种服务的价格分别是 $10 和 $20。转义写法：\$30 和 \$40。

Shell 变量保持原样：$HOME、${PATH}、$$；行内代码：`echo "$HOME"`。

行内公式：\(a_1 + b_2 = c\)。

\[
\mathbf{R}^{\mathsf T}\mathbf{R}=\mathbf{I},\qquad
\sum_{i=1}^{n} x_i^2
\]

## 标题与目录

### 三级标题

#### 四级标题

四级标题也出现在目录中。

## 表格

| 方法名称 | 训练数据 | 视觉编码 | 几何信息 | 导航效果 | 推理速度 | 内存占用 | 适用场景 |
|---|---|---|---|---|---|---|---|
| 本文提出的新方法 | 大规模室内外混合数据 | 多尺度视觉特征 | 三维空间结构 | 较高的导航成功率 | 实时在线运行 | 中等资源占用 | 复杂室内场景 |
| 传统基线方法 | 小规模室内数据 | 单尺度特征 | 二维平面地图 | 一般导航成功率 | 接近实时 | 较低资源占用 | 简单静态场景 |

<table class="comparison"><thead><tr><th>项目</th><th>说明</th></tr></thead><tbody><tr><td>带属性的 HTML 表格</td><td>与普通表格采用相同的滚动与配色规则。</td></tr></tbody></table>

## 列表、引用与脚注

- 普通项目
  - 嵌套项目
- [x] 已完成项目
- [ ] 待完成项目

> 阅读过程中保持清晰的层级与适当的间距。

这是一个脚注示例。[^example]

[^example]: 脚注位于页面末尾。

## 代码

行内代码：`std::vector<int>`、`ros2 launch`。

```cpp
#include <vector>
int main() {
    std::vector<int> values{1, 2, 3};
    return values.size();
}
```

```text
$10 and $20 are prices; echo "$HOME"; $$ remains literal here.
```

## 图片

![竖向技术示意图](/notes/media/Algorithm/image-20250804115059584.png "竖图保持原始比例，可以点击放大")
