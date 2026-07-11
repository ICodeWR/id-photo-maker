# 贡献指南

感谢您对 **智能证件照制作工具** 的关注！欢迎任何形式的贡献——报告 Bug、提出新功能、改进文档、提交代码。

## 行为准则

本项目采用了 [贡献者行为准则](CODE_OF_CONDUCT.md)，所有参与者都应遵守。请阅读并遵循该准则。

## 如何贡献

### 报告 Bug

1. 在 [Issues](https://github.com/ICodeWR/id-photo-maker/issues) 中搜索是否已有类似报告
2. 若无，创建新 Issue，标题清晰描述问题
3. 在 Issue 中提供：
   - 操作系统版本、Python 版本
   - 完整的错误日志或截图
   - 可复现的操作步骤
   - 期望行为与实际行为

### 提出新功能

1. 在 [Issues](https://github.com/ICodeWR/id-photo-maker/issues) 中标记为 `enhancement`
2. 清晰描述功能需求和使用场景
3. 如果涉及 UI 改动，请说明预期的交互方式

### 提交代码

#### 分支规范

```bash
# 功能分支
feature/your-feature-name

# Bug 修复分支
fix/bug-description

# 文档改进
docs/what-changed
```

#### 开发流程

1. Fork 本仓库并克隆到本地
2. 创建特性分支：`git checkout -b feature/your-feature`
3. 安装开发依赖：`uv sync`
4. 编写代码，确保通过现有测试：`uv run pytest`
5. 为新功能添加测试（覆盖率不低于 80%）
6. 提交代码：`git commit -m 'feat: add some feature'`
7. 推送到远程：`git push origin feature/your-feature`
8. 发起 Pull Request 到 `main` 分支

#### Commit 规范

建议使用 [Conventional Commits](https://www.conventionalcommits.org/) 格式：

```
feat: 新功能
fix: Bug 修复
docs: 文档变更
style: 代码格式调整（不影响功能）
refactor: 代码重构
test: 测试相关
chore: 构建/工具链相关
```

### 贡献文档

- 教程文档位于项目根目录，采用 Markdown 格式
- 示意图 SVG 文件位于项目根目录
- 修改文档后请确保目录与内容一致

## 代码审查

所有 Pull Request 需要至少一名维护者审查通过后才能合并。审查标准：

- 代码风格与项目一致（遵循 pylint 配置）
- 新功能有对应的测试覆盖
- UI 改动遵循 Qt Designer 分离原则（不修改 `main.py` 中的 UI 布局代码）
- 兼容 Windows 中文路径（使用 PIL 作为 `cv2.imwrite` 降级方案）

## 开发环境

- Python ≥ 3.10
- uv（推荐）或 pip
- Windows 10+ / macOS / Linux

## 联系方式

如有疑问，请通过 Issue 发起讨论。
