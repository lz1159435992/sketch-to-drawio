# sketch-to-drawio

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Rebuild raster figure drafts — GPT/AI-generated mockups or hand-drawn scans of
paper framework diagrams, method overviews, and pipeline figures — as **native,
fully editable draw.io vector figures** for academic papers, with open-source
icon sourcing, sketch-icon tracing/upscaling, and mandatory attribution +
quality-control ledgers.

This is a [Codex](https://github.com/openai/codex) / Claude agent skill
(`SKILL.md` + references + scripts). Give your agent a bitmap sketch, and it
produces an editable `.drawio` source plus publication-ready SVG/PNG exports —
the sketch itself is never embedded as a background or flattened into the
final figure.

> 中文说明见文末。

## Features

- **Native redraw, not embedding**: every module, container, arrow, and label
  is rebuilt with native draw.io XML shapes; all objects stay editable.
- **Two-tier element ladders** — each graphic element is classified first,
  then handled by the appropriate fallback ladder:
  - *Simple functional icons* (single semantics: car, file, shield, search):
    **A** open-source SVG (Lucide first, then Iconify sets) → **B** trace the
    sketch icon (crop → denoise → vtracer/Inkscape → redraw as geometry) →
    **C** conservative generic shapes + text labels.
  - *Complex illustrations/scenes* (multi-element, decorative: a mountain-road
    scene): **A′** same-set composite (with a ≤3-element quality gate) →
    **B′** crop + color tracing (vtracer `--colormode color`) → **C′** crop +
    raster enhancement (upscale ×2–4, denoise, sharpen, flood-fill background
    flattening, wrapped in SVG `<image>`) → **D′** palette-mapped flat color
    sets / native shape composites → **E** minimal monochrome fallback.
- **Style consistency over semantic match**: stroke-width family, in-figure
  palette, no gradients, no own-horizon, shared baseline — enforced as hard
  constraints before any icon/illustration is accepted.
- **Anti-fabrication guardrails**: never invent workflows, numbers, or icon
  semantics; low-confidence judgments degrade to conservative shapes and are
  logged as `needs_user_confirmation` items.
- **Mandatory ledgers**: every figure ships with
  `<fig>-icon-attribution.md` (library, license, attribution requirement,
  processing method per element) and `<fig>-QC.md` (export inspection results
  and open questions).

## Repository layout

```
SKILL.md                     skill entry point (workflow, ladders, guardrails)
agents/openai.yaml           agent-facing metadata
references/
  icon-sourcing.md           icon search/download + drawio embedding matrix
  icon-tracing.md            sketch-icon tracing rules (path B)
  illustrations.md           complex-illustration ladder (A′–E) + license table
  qc.md                      conservative-shape taxonomy + QC ledger format
scripts/
  fetch_icon.py              download an Iconify icon + license + attribution row
  remap_svg_colors.py        luminance-rank-preserving palette remapping
  embed_raster.py            crop/enhance a raster patch, wrap in SVG <image>
```

## Installation

Copy the folder into your agent's skills directory:

```bash
# Codex
cp -r sketch-to-drawio ~/.codex/skills/

# Claude Code
cp -r sketch-to-drawio ~/.claude/skills/
```

Or install via a skill installer from this repo path.

## Dependencies

- **draw.io desktop** + `xvfb-run` (headless export;
  `xvfb-run -a drawio --no-sandbox -x -f png -s 2 -o out.png in.drawio`)
- **Python 3 + Pillow** (required by all scripts)
- **ImageMagick** (optional; crop/enhance helpers)
- **vtracer** or **Inkscape** (optional; sketch-icon color tracing, paths B/B′)

## Script usage

```bash
# Fetch an open-source icon and append its attribution row
python3 scripts/fetch_icon.py lucide:car -o car.svg \
    --attribution fig-icon-attribution.md --module "Col2: paired execution"

# Remap a colored SVG onto the figure palette (luminance rank preserved)
python3 scripts/remap_svg_colors.py in.svg -o out.svg \
    --palette "#8AA5BE,#39739D,#3F7E5A" --report

# Crop + enhance a sketch illustration and emit a drawio-ready image URI
python3 scripts/embed_raster.py sketch.png -o scene.svg \
    --crop 168x88+271+459 --scale 3 --denoise --bg-flatten-white 14 \
    --uri scene-uri.txt
```

## When (not) to use

Use this skill when you already have a **raster draft** of the figure. For
building draw.io figures from scratch (no sketch), route to a general
drawio-authoring skill instead — this skill deliberately reuses, and does not
duplicate, draw.io XML/CLI mechanics.

## Companion skill: icon-forge

[`icon-forge/`](icon-forge/) is a sibling skill for the **no-sketch** case:
given a text description of a module or element, it selects or generates a
matching SVG icon — **A** semantic parsing + open-source lookup (reuses this
repo's `references/icon-sourcing.md` and `scripts/fetch_icon.py`) → **B**
same-set two-element composites → **C** AI generation as a last resort
(bitmap → vtracer vectorization → palette remapping via
`scripts/remap_svg_colors.py`, one revision max) → **D** conservative generic
shapes. The same style-consistency hard constraints and anti-fabrication
guardrails apply, and every icon ships with an attribution row and QC
confidence record. Install it the same way:

```bash
cp -r sketch-to-drawio/icon-forge ~/.codex/skills/   # or ~/.claude/skills/
```

## License

MIT (see [LICENSE](LICENSE)). Third-party icons fetched through the scripts
keep their own licenses (e.g., Lucide is ISC); CC-BY icon sets require
attribution, which the attribution ledger will flag as a
`license_attribution` confirmation item.

---

## 中文说明

把位图草图（GPT/AI 生成或手绘扫描的论文框架图、方法图、流程图草稿）重绘为
**原生可编辑的 draw.io 学术矢量图**的 Codex / Claude agent skill。

- **原生重绘**：草图只作构图、模块和关系参考，绝不作为背景或整图嵌入最终产物；
  所有模块、箭头、文本均为可编辑对象。
- **双阶梯处理**：简单功能图标走 A（开源 SVG，默认 Lucide）→ B（草图描摹
  清晰化）→ C（保守通用形状）；复杂插画/场景走 A′（同集组合，≤3 元素质量
  门槛）→ B′（裁剪+彩色描摹）→ C′（裁剪+栅格高清化，含泛洪背景白底化）→
  D′（色板映射彩色集/原生形状）→ E（保底）。
- **风格一致性硬约束**：描边宽度族、图内色板、无渐变、无自带背景、基线一致，
  任一不满足即降级。
- **防虚构护栏**：不虚构流程/数值/图标语义；低置信度判断一律降级并记入
  待确认清单。
- **强制台账**：每张图交付 `<图名>-icon-attribution.md`（图标来源/许可证/
  署名要求/处理方式）与 `<图名>-QC.md`（导出目检结果与待确认项）。

安装：把整个目录复制到 `~/.codex/skills/`（Codex）或 `~/.claude/skills/`
（Claude Code）。依赖：drawio desktop + xvfb-run（headless 导出）、
Python 3 + Pillow（脚本必需）、ImageMagick 与 vtracer/Inkscape（可选，
描摹路径使用）。许可证：MIT；第三方图标保留其自身许可证（如 Lucide 为
ISC），CC-BY 类集合需要署名，attribution 台账会自动标记提醒。

### 姊妹 skill：icon-forge

[`icon-forge/`](icon-forge/) 处理**无草图**场景：按文字描述为模块/元素
选配或生成 SVG 图标——A 语义解析+开源检索（复用本仓库
`references/icon-sourcing.md` 与 `scripts/fetch_icon.py`）→ B 同集双元素
组合 → C AI 生成（最后手段：位图→vtracer 矢量化→
`scripts/remap_svg_colors.py` 色板映射，最多修订一轮）→ D 保底通用形状。
同样的风格一致性硬约束与防虚构护栏，每个图标都带 attribution 行与 QC
置信度记录。安装方式相同：`cp -r sketch-to-drawio/icon-forge
~/.codex/skills/`。
