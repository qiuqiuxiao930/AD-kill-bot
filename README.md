# 🛡️ TG-ScamGuard

> 一个基于 AI 的 Telegram 群组诈骗广告过滤机器人，自动识别并清除群组中的诈骗、博彩、钓鱼等违规消息。

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Telegram Bot API](https://img.shields.io/badge/Telegram%20Bot%20API-支持-blue?logo=telegram)](https://core.telegram.org/bots/api)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

---

## ✨ 功能特性

- 🤖 **自动检测** — 实时分析群组消息，识别诈骗、博彩、钓鱼链接等违规内容
- 🧠 **AI 驱动** — 结合关键词规则与语义模型，减少误判
- 🔇 **多级处置** — 支持删除消息、警告、禁言、踢出等多种处置方式
- 📊 **日志记录** — 完整记录检测结果，方便管理员审计
- ⚙️ **灵活配置** — 每个群组可独立设置规则、白名单、处置策略
- 🌐 **多语言支持** — 支持中文、英文等多语言内容检测

---

## 📸 效果预览

```
[用户] 加我微信 xxxxx，稳赚不赔，日收益 300%！
[ScamGuard 🛡️] ⚠️ 检测到可疑消息，已自动删除。
              类型：投资诈骗广告
              用户已被警告（1/3）
```

---

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/yourname/tg-scamguard.git
cd tg-scamguard
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

复制示例配置文件并填写：

```bash
cp .env.example .env
```

```env
# .env
BOT_TOKEN=your_telegram_bot_token
ADMIN_IDS=123456789,987654321
LOG_LEVEL=INFO
```

### 4. 启动机器人

```bash
python main.py
```

---

## ⚙️ 配置说明

在 `config.yml` 中进行详细配置：

```yaml
detection:
  keywords_file: rules/keywords.txt   # 关键词规则文件
  use_ai_model: true                  # 是否启用 AI 语义检测
  confidence_threshold: 0.85          # AI 置信度阈值

actions:
  on_detect:
    delete_message: true              # 自动删除违规消息
    warn_user: true                   # 发送警告
    max_warnings: 3                   # 最大警告次数
    ban_on_max_warnings: true         # 达到上限后封禁

whitelist:
  users: []                           # 白名单用户 ID
  roles: ["管理员", "版主"]            # 白名单角色

logging:
  save_to_file: true
  log_path: logs/scamguard.log
```

---

## 🧩 支持的诈骗类型

| 类型 | 说明 |
|------|------|
| 💰 投资诈骗 | 高回报、稳赚不赔、虚假理财 |
| 🎰 博彩广告 | 赌博平台推广、返利引流 |
| 🔗 钓鱼链接 | 仿冒网站、盗号链接 |
| 📱 二维码诈骗 | 可疑二维码图片 |
| 👤 色情引流 | 成人内容诱导 |
| 🤝 刷单兼职 | 虚假兼职、刷单返利 |

---

## 🤖 Bot 命令

在群组中，管理员可使用以下命令：

| 命令 | 说明 |
|------|------|
| `/scamguard on` | 启用机器人 |
| `/scamguard off` | 停用机器人 |
| `/scamguard status` | 查看当前状态和统计 |
| `/whitelist add @user` | 将用户加入白名单 |
| `/whitelist remove @user` | 移除白名单用户 |
| `/warn @user` | 手动警告用户 |
| `/unban @user` | 解除封禁 |

---

## 🏗️ 项目结构

```
tg-scamguard/
├── main.py               # 入口文件
├── config.yml            # 主配置文件
├── .env.example          # 环境变量示例
├── requirements.txt
├── bot/
│   ├── handlers.py       # 消息处理器
│   ├── commands.py       # 命令处理
│   └── actions.py        # 处置动作
├── detection/
│   ├── keyword_filter.py # 关键词过滤
│   ├── ai_classifier.py  # AI 语义分类
│   └── url_checker.py    # 链接检测
├── rules/
│   └── keywords.txt      # 关键词规则库
├── logs/                 # 日志目录
└── tests/                # 单元测试
```

---

## 🛠️ 技术栈

- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) — Telegram Bot 框架
- [scikit-learn](https://scikit-learn.org/) / [transformers](https://huggingface.co/transformers/) — 文本分类模型
- [SQLite](https://www.sqlite.org/) / [Redis](https://redis.io/) — 数据存储与缓存
- [loguru](https://github.com/Delgan/loguru) — 日志管理

---

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建功能分支：`git checkout -b feature/your-feature`
3. 提交更改：`git commit -m 'feat: add your feature'`
4. 推送分支：`git push origin feature/your-feature`
5. 发起 Pull Request

请确保提交前通过所有测试：

```bash
pytest tests/
```

---

## ⚠️ 免责声明

本项目仅供学习与合法群组管理使用。请勿将其用于任何违反 [Telegram 服务条款](https://telegram.org/tos) 或当地法律法规的用途。

---

## 📄 许可证

本项目采用 [MIT License](LICENSE) 开源协议。

---

<div align="center">
  <sub>如果这个项目对你有帮助，欢迎 ⭐ Star 支持！</sub>
</div>
