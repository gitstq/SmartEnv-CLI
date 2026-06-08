<div align="center">

# SmartEnv-CLI

**Intelligent Environment Variable Manager for Developers**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![PyPI](https://img.shields.io/badge/PyPI-Coming%20Soon-orange)](https://pypi.org/)

[English](#english) | [简体中文](#简体中文) | [繁體中文](#繁體中文)

</div>

---

<a name="english"></a>
## English

### 🎉 Introduction

SmartEnv-CLI is an intelligent environment variable management tool designed for developers. It solves the pain points of manually maintaining `.env` files, easily making mistakes across multiple environments, and the risk of leaking sensitive information.

**Core Value:**
- Automatically detects project type and generates `.env` templates
- One-click synchronization of multi-environment configurations
- Encrypts sensitive data to ensure security
- Beautiful CLI interface for an exceptional developer experience

**Inspiration:** Every developer has experienced the frustration of manually copying `.env.example` to `.env` and then forgetting to update it when adding new variables. SmartEnv-CLI completely automates this process.

### ✨ Core Features

| Feature | Description |
|---------|-------------|
| **Auto-Detection** | Automatically identifies Django, Flask, FastAPI, Node, React, Docker projects |
| **Smart Templates** | Generates `.env.example` with default values and security annotations |
| **Multi-Env Sync** | Synchronizes variables from template to all environment files |
| **Diff Comparison** | Compares differences between two `.env` files |
| **Security Validation** | Detects empty sensitive values and weak passwords |
| **Encryption** | Encrypts sensitive values using Fernet algorithm |
| **Beautiful CLI** | Rich terminal output with progress indicators and tables |

### 🚀 Quick Start

**Requirements:**
- Python 3.8+
- pip

**Installation:**
```bash
pip install smartenv-cli
```

**Basic Usage:**
```bash
# Initialize .env.example (auto-detects project type)
smartenv init

# Validate .env file
smartenv validate

# Compare two .env files
smartenv diff -c .env.production

# Sync all .env files from template
smartenv sync

# Encrypt sensitive values
smartenv encrypt

# View .env file (sensitive values masked)
smartenv show
```

### 📖 Detailed Usage Guide

**Project Type Auto-Detection:**
SmartEnv-CLI automatically detects your project type based on file indicators:
- **Django**: `manage.py`, `settings.py`
- **Flask**: `app.py`, `config.py`
- **FastAPI**: `main.py`, `app/main.py`
- **Node.js**: `package.json`, `server.js`
- **React**: `src/App.js`, `public/index.html`
- **Docker**: `Dockerfile`, `docker-compose.yml`

**Working with Multiple Environments:**
```bash
# Generate template
smartenv init -o .env.example

# Create environment-specific files
cp .env.example .env.development
cp .env.example .env.production

# Sync missing variables from template to all env files
smartenv sync -t .env.example
```

**Security Best Practices:**
```bash
# Validate before committing
smartenv validate

# Encrypt before sharing
smartenv encrypt -e .env.production -o .env.production.enc

# Decrypt when needed
smartenv decrypt -e .env.production.enc -o .env.production
```

### 💡 Design & Roadmap

**Design Philosophy:**
- Convention over configuration
- Security by default
- Developer experience first

**Tech Stack:**
- Python 3.8+ for broad compatibility
- Click for CLI framework
- Rich for beautiful terminal output
- Cryptography for Fernet encryption

**Roadmap:**
- [ ] Support for more project types (Go, Rust, Ruby)
- [ ] Integration with CI/CD pipelines
- [ ] Web dashboard for team collaboration
- [ ] Cloud secret manager integration (AWS KMS, Azure Key Vault)

### 📦 Packaging & Deployment

**Local Development:**
```bash
git clone https://github.com/gitstq/SmartEnv-CLI.git
cd SmartEnv-CLI
pip install -e ".[dev]"
make test
```

**Build & Publish:**
```bash
make build
make publish
```

### 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

- Fork the repository
- Create a feature branch
- Submit a Pull Request

### 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.

---

<a name="简体中文"></a>
## 简体中文

### 🎉 项目介绍

SmartEnv-CLI 是一款专为开发者设计的智能环境变量管理工具。它解决了手动维护 `.env` 文件繁琐、多环境配置易出错、敏感信息泄露风险等痛点。

**核心价值：**
- 自动检测项目类型，生成 `.env` 模板
- 一键同步多环境配置
- 加密敏感数据，确保安全
- 精美的 CLI 界面，卓越的开发者体验

**灵感来源：** 每个开发者都经历过手动复制 `.env.example` 到 `.env`，然后添加新变量时忘记更新的痛苦。SmartEnv-CLI 完全自动化了这一过程。

### ✨ 核心特性

| 特性 | 说明 |
|------|------|
| **自动检测** | 自动识别 Django、Flask、FastAPI、Node、React、Docker 项目 |
| **智能模板** | 生成带默认值和安全标注的 `.env.example` |
| **多环境同步** | 从模板同步变量到所有环境文件 |
| **差异对比** | 对比两个 `.env` 文件的差异 |
| **安全校验** | 检测空敏感值和弱密码 |
| **加密保护** | 使用 Fernet 算法加密敏感值 |
| **精美 CLI** | 富文本终端输出，带进度条和表格 |

### 🚀 快速开始

**环境要求：**
- Python 3.8+
- pip

**安装：**
```bash
pip install smartenv-cli
```

**基础用法：**
```bash
# 初始化 .env.example（自动检测项目类型）
smartenv init

# 校验 .env 文件
smartenv validate

# 对比两个 .env 文件
smartenv diff -c .env.production

# 从模板同步所有 .env 文件
smartenv sync

# 加密敏感值
smartenv encrypt

# 查看 .env 文件（敏感值已脱敏）
smartenv show
```

### 📖 详细使用指南

**项目类型自动检测：**
SmartEnv-CLI 根据文件特征自动检测项目类型：
- **Django**：`manage.py`、`settings.py`
- **Flask**：`app.py`、`config.py`
- **FastAPI**：`main.py`、`app/main.py`
- **Node.js**：`package.json`、`server.js`
- **React**：`src/App.js`、`public/index.html`
- **Docker**：`Dockerfile`、`docker-compose.yml`

**多环境配置管理：**
```bash
# 生成模板
smartenv init -o .env.example

# 创建各环境文件
cp .env.example .env.development
cp .env.example .env.production

# 从模板同步缺失变量到所有环境文件
smartenv sync -t .env.example
```

**安全最佳实践：**
```bash
# 提交前校验
smartenv validate

# 分享前加密
smartenv encrypt -e .env.production -o .env.production.enc

# 需要时解密
smartenv decrypt -e .env.production.enc -o .env.production
```

### 💡 设计思路与迭代规划

**设计理念：**
- 约定优于配置
- 默认安全
- 开发者体验优先

**技术选型：**
- Python 3.8+ 保证广泛兼容性
- Click 作为 CLI 框架
- Rich 实现精美终端输出
- Cryptography 提供 Fernet 加密

**迭代计划：**
- [ ] 支持更多项目类型（Go、Rust、Ruby）
- [ ] CI/CD 流水线集成
- [ ] Web 仪表盘团队协作
- [ ] 云密钥管理服务集成（AWS KMS、Azure Key Vault）

### 📦 打包与部署

**本地开发：**
```bash
git clone https://github.com/gitstq/SmartEnv-CLI.git
cd SmartEnv-CLI
pip install -e ".[dev]"
make test
```

**构建与发布：**
```bash
make build
make publish
```

### 🤝 贡献指南

欢迎贡献！请参阅 [CONTRIBUTING.md](CONTRIBUTING.md) 了解规范。

- Fork 仓库
- 创建功能分支
- 提交 Pull Request

### 📄 开源协议

本项目采用 MIT 协议 - 详见 [LICENSE](LICENSE)。

---

<a name="繁體中文"></a>
## 繁體中文

### 🎉 專案介紹

SmartEnv-CLI 是一款專為開發者設計的智慧環境變數管理工具。它解決了手動維護 `.env` 檔案繁瑣、多環境配置易出錯、敏感資訊洩露風險等痛點。

**核心價值：**
- 自動檢測專案類型，生成 `.env` 模板
- 一鍵同步多環境配置
- 加密敏感資料，確保安全
- 精美的 CLI 介面，卓越的開發者體驗

**靈感來源：** 每個開發者都經歷過手動複製 `.env.example` 到 `.env`，然後新增變數時忘記更新的痛苦。SmartEnv-CLI 完全自動化了這一過程。

### ✨ 核心特性

| 特性 | 說明 |
|------|------|
| **自動檢測** | 自動識別 Django、Flask、FastAPI、Node、React、Docker 專案 |
| **智慧模板** | 生成帶預設值和安全標註的 `.env.example` |
| **多環境同步** | 從模板同步變數到所有環境檔案 |
| **差異對比** | 對比兩個 `.env` 檔案的差異 |
| **安全校驗** | 檢測空敏感值和弱密碼 |
| **加密保護** | 使用 Fernet 演算法加密敏感值 |
| **精美 CLI** | 富文字終端輸出，帶進度條和表格 |

### 🚀 快速開始

**環境要求：**
- Python 3.8+
- pip

**安裝：**
```bash
pip install smartenv-cli
```

**基礎用法：**
```bash
# 初始化 .env.example（自動檢測專案類型）
smartenv init

# 校驗 .env 檔案
smartenv validate

# 對比兩個 .env 檔案
smartenv diff -c .env.production

# 從模板同步所有 .env 檔案
smartenv sync

# 加密敏感值
smartenv encrypt

# 查看 .env 檔案（敏感值已脫敏）
smartenv show
```

### 📖 詳細使用指南

**專案類型自動檢測：**
SmartEnv-CLI 根據檔案特徵自動檢測專案類型：
- **Django**：`manage.py`、`settings.py`
- **Flask**：`app.py`、`config.py`
- **FastAPI**：`main.py`、`app/main.py`
- **Node.js**：`package.json`、`server.js`
- **React**：`src/App.js`、`public/index.html`
- **Docker**：`Dockerfile`、`docker-compose.yml`

**多環境配置管理：**
```bash
# 生成模板
smartenv init -o .env.example

# 建立各環境檔案
cp .env.example .env.development
cp .env.example .env.production

# 從模板同步缺失變數到所有環境檔案
smartenv sync -t .env.example
```

**安全最佳實踐：**
```bash
# 提交前校驗
smartenv validate

# 分享前加密
smartenv encrypt -e .env.production -o .env.production.enc

# 需要時解密
smartenv decrypt -e .env.production.enc -o .env.production
```

### 💡 設計思路與迭代規劃

**設計理念：**
- 約定優於配置
- 預設安全
- 開發者體驗優先

**技術選型：**
- Python 3.8+ 保證廣泛相容性
- Click 作為 CLI 框架
- Rich 實現精美終端輸出
- Cryptography 提供 Fernet 加密

**迭代計劃：**
- [ ] 支援更多專案類型（Go、Rust、Ruby）
- [ ] CI/CD 流水線整合
- [ ] Web 儀表盤團隊協作
- [ ] 雲端金鑰管理服務整合（AWS KMS、Azure Key Vault）

### 📦 打包與部署

**本地開發：**
```bash
git clone https://github.com/gitstq/SmartEnv-CLI.git
cd SmartEnv-CLI
pip install -e ".[dev]"
make test
```

**構建與發布：**
```bash
make build
make publish
```

### 🤝 貢獻指南

歡迎貢獻！請參閱 [CONTRIBUTING.md](CONTRIBUTING.md) 了解規範。

- Fork 倉庫
- 建立功能分支
- 提交 Pull Request

### 📄 開源協議

本專案採用 MIT 協議 - 詳見 [LICENSE](LICENSE)。
