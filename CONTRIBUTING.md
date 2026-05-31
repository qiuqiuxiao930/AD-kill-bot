# 贡献指南

感谢你对 TG-ScamGuard 的关注和贡献！

## 开发流程

1. Fork 本仓库
2. 创建功能分支：`git checkout -b feature/your-feature`
3. 安装依赖：`pip install -r requirements.txt`
4. 进行开发和测试
5. 提交更改：`git commit -m 'feat: add your feature'`
6. 推送分支：`git push origin feature/your-feature`
7. 发起 Pull Request

## 代码规范

- 使用 Python 3.10+
- 遵循 PEP 8 代码风格
- 使用类型注解
- 为新功能编写单元测试

## 运行测试

```bash
pip install pytest
pytest tests/
```

## 提交规范

使用 [Conventional Commits](https://www.conventionalcommits.org/) 格式：

- `feat:` 新功能
- `fix:` 修复
- `docs:` 文档
- `test:` 测试
- `refactor:` 重构

## 问题反馈

如果发现 Bug 或有功能建议，请提交 Issue。
