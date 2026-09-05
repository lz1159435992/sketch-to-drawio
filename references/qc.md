# 质量检查与待确认项（C 路径判定 + QC 文件）

## C 路径保守形状映射

| 已知语义 | 替代形状 |
|---|---|
| 数据/信息 | 文件形（`shape=note`）或圆柱体（`shape=cylinder3`） |
| 处理/算法 | 圆角矩形或齿轮 |
| 系统/平台 | 容器框、云形或服务器框 |
| 人员/参与者 | 人物轮廓或圆形 |
| 输入 | 向内箭头或表单框 |
| 输出 | 向外箭头、文件框或图表框 |
| 无法确定 | 无装饰圆角矩形 + 清晰文字标签 |
| 标题与图标语义均不可靠 | 无装饰圆角矩形 + `[需确认]` 占位文本，不用具象图标 |

## QC 文件 schema（`<fig>-QC.md`）

两项内容：

1. **自检结果表**：每次导出的 PNG 目检结论（裁切/重叠/错位/断线/箭头方向/字号/图标一致性/颜色可区分性/CJK 缺字/插画风格一致性（illustrations.md 硬约束 5 条）与保真度），以及对应的修复动作。
2. **待确认清单**，每项含：

```yaml
- id: qc-003
  类型: icon_semantic | text_missing | data_missing | style_override | tool_fallback | illustration_replacement | license_attribution
  位置: 模块名或图标位置描述
  不确定原因: 例如“草图图标模糊，标题无法辨认”
  采用方案: 例如“generic_shape：无装饰圆角矩形 + [需确认]”
  保守语义: 该替代图形代表的最保守含义
  needs_user_confirmation: true
```

## 交付要求

- 最终回复必须汇总全部 `needs_user_confirmation: true` 项（id + 一句话说明）。
- 纯布局问题（重叠、错位、断线）属于自动修复范围，改 XML 重导即可，不进待确认清单；只有语义、内容、风格决策才进。
