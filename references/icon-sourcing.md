# 开源图标检索（A 路径）

SKILL.md 的 A 路径展开：检索顺序、下载机制、许可与归属记录。

## 检索顺序

1. **Lucide**（默认）：单色线性、风格统一，适合学术图。语义命名直观（`camera`、`database`、`cpu`、`file-text`、`arrow-right`）。
2. **Iconify 开源集**：Lucide 无合适图标时按语义检索。常用集：
   - `mdi`（Material Design Icons，Apache-2.0）：医疗、护理、医院、患者、设备类优先；
   - `fluent`（Microsoft Fluent，MIT）：设备、办公语义；
   - `carbon`（IBM，Apache-2.0）、`tabler`（MIT）：通用补充。
3. 选许可清晰（ISC/MIT/Apache-2.0/CC-BY-4.0）、适合学术论文的图标；CC-BY 类必须在 attribution 中写署名。

## 风格一致性

同一张图只用同一图标集（默认 Lucide）。用户明确要求混合风格时，在 QC 中记录为已确认覆盖。

## 下载机制

Iconify API 免 key、确定性：

```
https://api.iconify.design/{prefix}/{name}.svg # SVG 本体
https://api.iconify.design/collections         # 全部图标集索引（含 license）
```

注意：license 要查 `/collections` 索引；单集端点 `/collection?prefix=...` 对部分集合（如 lucide）返回 `license: null`。

优先用 skill 自带脚本，它会下载 SVG 并自动追加 attribution 行：

```bash
python3 <skill-dir>/scripts/fetch_icon.py lucide:camera -o <ref-dir>/camera.svg \
    --attribution <fig>-icon-attribution.md --module "数据采集模块"
```

API 不可达时的降级：手绘等价 draw.io `shape=image` 或直接降 B/C 路径，并在 QC 记录原因。

## attribution 文件 schema

每图标一行（markdown 表）：

| icon | 模块 | 来源 | 库/名称 | 许可证 | 署名要求 | 处理方式 | 置信度 | 待确认 |
|---|---|---|---|---|---|---|---|---|

- `来源`：`open_source` / `reconstructed_from_user_sketch` / `traced_from_user_sketch` / `generic_shape`；
- `处理方式`：`as_svg` / `redrawn_native` / `inserted_svg` / `generic`；
- `置信度`：`high` / `medium` / `low`（medium 及以下必须 `待确认=yes`）。

## 嵌入 draw.io 的格式（实测不变量，2026-09-05 全矩阵）

headless Linux drawio desktop（xvfb + `--no-sandbox`）导出实测：

| 嵌入方式 | 结果 |
|---|---|
| percent-encoded SVG data URI（`data:image/svg+xml,%3Csvg...`） | 正常 |
| PNG 包进 SVG `<image>`（base64）再 percent-encode | 正常（栅格内容唯一可行路径，且自包含可移植） |
| base64 SVG data URI | 静默空白 |
| base64 PNG data URI | 静默空白 |
| percent-encoded PNG data URI | 静默空白 |
| `file://` 绝对路径 PNG | 静默空白 |

- 矢量图标：`currentColor` 替换为目标 hex、Iconify 的 `width="1em"` 换绝对像素后 percent-encode。
- 栅格补丁：用 `scripts/embed_raster.py` 生成 SVG 包裹并产出 URI（`--uri`）。
- 有显示/非 root 环境下 base64 通常可用，但 percent-encoded SVG 形式各环境均可，优先使用。
