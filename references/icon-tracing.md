# 草图图标描摹（B 路径）

SKILL.md 的 B 路径展开：清晰化、矢量化、重绘判定。核心约束：**不补造原图不存在的细节**；任何一步工具缺失就降 C 路径并在 QC 记录。

## 步骤

1. **裁剪**：从草图裁出单个图标，存 `<ref-dir>/<icon-id>-raw.png`。用 ImageMagick：
   ```bash
   magick sketch.png -crop <w>x<h>+<x>+<y> +repage <icon-id>-raw.png
   ```
2. **清晰化**（适度，默认放大 3 倍，可按图标尺寸 2–4 倍调整）：
   ```bash
   magick <icon-id>-raw.png -resize 300% -despeckle -contrast-stretch 2%x2% -sharpen 0x1 <icon-id>-clean.png
   # 背景干扰大时：-fuzz 10% -transparent white（白底情形）
   ```
3. **矢量化**（任一可用工具）：
   ```bash
   vtracer --input <icon-id>-clean.png --output <icon-id>-reference.svg --colormode bw --filter_speckle 8
   # 或 Inkscape：
   inkscape <icon-id>-clean.png --actions="select-all;trace-bitmap;export-filename:<icon-id>-reference.svg;export-do" --batch-process
   ```
4. **重绘判定**：参考 SVG 轮廓清晰、语义确定 → 在 draw.io 中用几何形状原生重绘（`来源=reconstructed_from_user_sketch`，`处理方式=redrawn_native`）；轮廓复杂、几何重绘会失真 → 把该独立 SVG 作为单独图标对象插入（`来源=traced_from_user_sketch`，`处理方式=inserted_svg`），不栅格化、不嵌入整张草图。
5. **目检参考 SVG** 后再判定；描摹结果与原图语义对不上 → 降 C，不强行使用。

## 工具检测

开始前一次性探测：

```bash
for b in magick convert vtracer inkscape; do command -v $b >/dev/null && echo "have $b"; done
```

`magick` 与 `convert` 任一即可；两者皆无但可用 Python PIL 时，裁剪/缩放/对比度用 PIL 完成，矢量化仍依赖 vtracer/inkscape——都缺则整段降 C。

## 彩色插画不要走本路径

本路径的 `--colormode bw` 黑白描摹只适用于单色图标。草图中的彩色场景/插画请走 [illustrations.md](illustrations.md) 的 B′ 彩色描摹（`--colormode color`），黑白化会失去插画的表现力。
