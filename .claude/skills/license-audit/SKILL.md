---
description: 依赖协议合规检查 — 当依赖文件变更时自动检查协议合规性
---

# 依赖协议审计 Skill

## 触发条件

当以下任一文件被修改时，自动触发本 Skill：

- `package.json`
- `go.mod`
- `requirements.txt`
- `pyproject.toml`
- `Cargo.toml`
- `*.csproj`

## 执行指令

### 1. 检测变更的依赖

对比当前依赖文件与 `LICENSE.LIST` 中已记录的依赖，找出：
- 新增的依赖
- 版本变更的依赖
- 已删除的依赖

### 2. 查询新增/变更依赖的协议

对新增或版本变更的依赖，使用 WebSearch 查询其协议：
- npm 包：`<包名> npm package license`
- Go 模块：`<模块路径> go module license`
- Python 包：`<包名> pypi license`
- Rust 包：`<包名> crates.io license`
- .NET 包：`<包名> nuget license`

如果搜索结果不明确，进行二次搜索：`<包名> github LICENSE file`。

### 3. 检查协议兼容性

对新增或版本变更的依赖，检查其协议与项目协议的兼容性：
- 读取项目根目录的 `LICENSE` 文件并识别项目协议
- 对照协议兼容性矩阵，判定兼容性
- 给出兼容性结论和修复建议

### 4. 更新 `LICENSE.LIST`

- 添加新增依赖的协议信息
- 更新版本变更的依赖信息
- 移除已删除的依赖条目
- 更新统计摘要

### 5. 更新 `LICENSE`

- 重新分析协议兼容性
- 更新第三方协议声明
- 更新合规建议

### 6. 通知用户

完成后通知用户：

> 依赖协议检查完成：
> - 新增 X 个依赖，协议均为 [协议列表]
> - 更新 X 个依赖版本
> - 移除 X 个依赖
> - 兼容性检查结果：✅ / ❌
> - 如果有 UNKNOWN 或 不兼容协议，提示手动确认

## 重要说明

- 仅检查直接依赖，不检查传递依赖
- UNKNOWN 协议需要用户手动确认
- 完整参考表请访问：https://tpscsm-docs.pages.dev/license-audit/
