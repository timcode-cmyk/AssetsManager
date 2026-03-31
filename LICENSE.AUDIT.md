# 项目协议合规参考报告

> 本文件由 AI 依赖协议审计自动生成，旨在帮助了解项目的协议合规情况。
> 本文件为合规参考，不构成法律建议。如有疑问请咨询法律专业人士。
> 生成时间：2026-03-31
> 审计工具：AI 依赖协议审计 (https://tpscsm-docs.pages.dev/license-audit/)

## 项目协议

项目当前声明协议为 `MIT`。

> ✅ 已选择 MIT 许可证。

## 直接依赖协议摘要

| 依赖名称 | 版本 | 协议 | 风险 |
|---------|------|------|------|
| PySide6 | >=6.6.0 | LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only | ⚠️ 需关注 |
| SQLAlchemy | >=2.0.0 | MIT | ✅ 兼容 |
| Pillow | >=10.0.0 | MIT (MIT-CMU) | ✅ 兼容 |
| av | >=11.0.0 | BSD-3-Clause | ✅ 兼容 |

## 合规结论

当前审计结果：

- 所有直接依赖均为开源协议。
- 其中 `PySide6` 具有 Copyleft 属性，通常以 `LGPL-3.0` 方式分发；MIT 项目与 `PySide6` 兼容，但必须遵守 Qt/LGPL 的运行时分发义务。
- `SQLAlchemy`、`Pillow`、`av` 均为宽松协议，与 MIT 兼容。

## 建议

1. 请尽快在项目根目录添加标准开源协议文件 `LICENSE`，例如：
   - `MIT`
   - `Apache-2.0`
   - `GPL-3.0-only`
2. 补充项目协议后，应重新执行依赖协议兼容性审核，特别关注 `PySide6` 的 Copyleft 义务。
3. 依赖中 `SQLAlchemy`、`Pillow`、`av` 为宽松协议，可正常用于开源分发。

## 依赖协议义务提示

- MIT / BSD-3-Clause：保留版权声明和许可声明。
- LGPL-3.0-only / GPL-2.0-only / GPL-3.0-only：如果以 LGPL/GPL 方式分发，需遵守相应 Copyleft 条款；若在应用中以动态链接方式使用 Qt，则通常可满足 LGPL 要求，但仍需保留版权声明并遵守 Qt 许可条款。

## 需要手动确认的事项

- 项目自身协议：请补充标准开源许可证后继续审计。
- `PySide6` 使用方式：请确认是否符合 Qt-for-Python 运行时分发要求。

## 后续文件

- `LICENSE.LIST`：依赖协议清单
- `LICENSE`：项目 MIT 协议文件
- `LICENSE.AUDIT.md`：本次合规参考报告
