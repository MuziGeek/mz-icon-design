# MZ Icon Design

一个独立、评审优先的 Agent Skill，用于创建统一的 MZ 界面图标与具有表现力的 Spot 图标系统。

![MZ 蜡笔图标系统](mz-icon-design/assets/mz-crayon-v2/contact-sheet.png)

## 三条生产路线

| 路线 | 适用场景 | 输出 |
| --- | --- | --- |
| `mz-line-v1` | 16–32 px 导航、按钮与紧凑 UI | 原创 SVG 与明暗预览 |
| `mz-crayon-v2` | 栏目、功能、分类与空状态 | 手绘透明 PNG Spot 图标 |
| `mz-block-v1` | 技术产品与空间概念 | 等距积木风透明 PNG 图标 |

![MZ Block 图标系统](mz-icon-design/assets/mz-block-v1/contact-sheet.png)

Skill 会根据用途与显示尺寸自动路由，验证每个输出，并停在 `READY_FOR_REVIEW`，不会自动发布或冒充用户验收。

## 安装

```text
$skill-installer install https://github.com/MuziGeek/mz-icon-design/tree/v1.0.0/mz-icon-design
```

## 示例

```text
Use $mz-icon-design to create a 24px search icon for navigation.
Use $mz-icon-design to create nine crayon spot icons for a personal portfolio.
Use $mz-icon-design to audit these SVG icons against the MZ design system.
```

## 可靠性

- 在 UI SVG 与两种 Spot 风格之间进行明确路由。
- SVG 静态检查与 16/24/32 px 视觉复核。
- PNG 集合的透明边缘、裁切、尺寸与 QA 预览检查。
- 区分草稿、生成受阻、验证失败与待评审状态。

## 许可证

代码与文档使用 MIT 许可证；MZ 参考图像使用 [MZ Reference Asset License 1.0](ASSET_LICENSE.md)。具体边界见 [NOTICE.md](NOTICE.md)。

[English](README.md)
