---
name: icon-forge
description: 按文字描述或任务语义为插图/图表选择或生成合适的 SVG 图标——语义解析→开源图标检索→同集组合→AI 生成矢量化（最后手段）→保底通用形状，含归属与质量记录。Use when the user describes a module/element in words and needs a matching icon (for draw.io figures, slides, documents). 有草图要整体重绘时不要用本 skill（路由给 sketch-to-drawio）；从零画整张 drawio 图路由给 drawio-skill。
---

# Icon Forge

按**文字描述**为图形元素选配或生成 SVG 图标。输入是语义，不是图像；输出是可嵌入 draw.io / PPT / 文档的独立 SVG 及归属记录。

## 输入与输出

输入：元素的文字描述（模块名、功能说明或上下文段落），以及目标图的风格约束（已有图标集、色板；未指定时默认 Lucide 单色线性）。

输出到用户指定目录：

- `<icon-id>.svg`：图标本体（矢量，可编辑）；
- attribution 行追加到用户指定的 `<fig>-icon-attribution.md`（库/名称/许可证/处理方式/置信度）；
- 低置信度语义、AI 生成、风格覆盖一律进对应 QC 文件的待确认清单。

## 处理阶梯（每元素独立判定，逐级降级）

**A. 语义解析 + 开源检索（首选）**

1. 从描述提取功能语义，列 2–4 个候选英文语义词并做同义扩展（如"验证"→ check / shield-check / clipboard-check / search-check）。
2. 检索顺序、下载机制、许可与 attribution schema 复用 sketch-to-drawio 的 `references/icon-sourcing.md` 与 `scripts/fetch_icon.py`（同机 skills 目录）：默认 Lucide，不足时 Iconify 开源集（医疗/设备优先 mdi、fluent）。
3. 语义置信度低（候选词之间语义差距大）时选最保守的一个并记 QC，不强行匹配具象图标。

**B. 同集组合（复合语义）**

单一图标表达不足时（如"跨种子复现"= copy + refresh-cw），用**同一图标集**的 2 个元素组合：一主一从（角标式叠加或并排），≤2 个元素，共享基线与描边族。组合后目检显乱则退回语义最接近的单一图标。多元素场景/插画不是本路径的领域（那是 sketch-to-drawio 插画阶梯的事）。

**C. AI 生成（最后手段）**

仅当 A/B 均无合适匹配、且该图标的语义对读图关键时启用：

1. 用 imagegen skill 生成位图：明确指定扁平风格、单色或 ≤3 色、纯白或透明底、无文字、无渐变、无自带背景。
2. 矢量化：功能图标 vtracer 单色；彩色插画 `vtracer --colormode color`。
3. 色板映射：用 sketch-to-drawio 的 `scripts/remap_svg_colors.py` 把颜色压到图内既有色板。
4. 目检：风格一致性硬约束（见下）任一不满足即降 D；最多修订一轮，不反复打磨。
5. attribution 标记 `ai_generated`，记 QC 待用户确认。

**D. 保底通用形状**

不猜语义。数据→文件/圆柱；处理→圆角矩形/齿轮；系统→容器/云/服务器；人员→人物轮廓；输入/输出→方向箭头/文件框；完全不确定→无装饰圆角矩形+清晰文字标签。全部记 QC 待确认。

## 风格一致性硬约束（任何路径都必须满足）

- 同一张图只用同一图标集（默认 Lucide 单色线性）；用户明确要求混合风格时记 QC 为已确认覆盖。
- 颜色取自图内既有低饱和色板；无渐变（除非全图本身使用）；透明底、无自带背景/地平线。
- 描边宽度族与全图图标一致；图标是辅助元素，不得替代关键文字和逻辑关系。

## 防虚构护栏

- 描述有歧义时不猜测：列候选语义按最保守处理并记 QC；影响图理解时直接问用户。
- AI 生成不得引入描述中不存在的具象细节（人物、品牌、设备型号等）。
- 生成/组合结果不得替代开源可溯源图标——A/B 可用时禁止直接跳 C。

## 与其他 skill 的关系

- **sketch-to-drawio**：有草图整体重绘时用它；本 skill 复用其 `references/icon-sourcing.md`（检索/许可/schema）、`references/illustrations.md`（风格硬约束与质量门槛）、`scripts/fetch_icon.py`、`scripts/remap_svg_colors.py`（同机 skills 目录下按名引用）。
- **drawio-skill**：从零绘制整张 drawio 图时用它；其中"按描述配图标"的环节按本 skill 的阶梯处理。
- **imagegen**：仅 C 路径的位图生成环节使用。
