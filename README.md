# 📰 AI 新闻简报助手 (AI News Newsletter Assistant)

这是一个高度自动化的 AI 新闻聚合与摘要工具。它能够定时抓取你指定的 RSS 订阅源，使用多线程加速获取内容，并通过大语言模型（支持 **Gemini** 和 **Qwen**）对海量资讯进行浓缩与全局宏观分析，最终将排版精美的图文简报准时发送到你的邮箱。



## ✨ 核心特性

- **🪄 一键交互式引导**：告别繁琐的手动配置。运行 `setup.py`，跟随引导自动生成 `.env` 和 `config.ini`，并可立刻执行首次抓取。
- **🚀 并发抓取引擎**：采用多线程并发拉取 RSS 源，极大提升网络请求速度。
- **🧠 智能长文本处理**：采用 Map-Reduce 架构，先按批次“脱水”浓缩，再进行全局深度总结，完美避开大模型 Token 限制。
- **🖼️ 图文精美排版**：自动提取新闻首图，并在 HTML 邮件中进行精美的自适应排版。
- **🗂️ 智能去重机制**：本地缓存历史链接，确保每天推送的简报只包含全新的资讯。
- **🛡️ 隐私与安全**：敏感 API 密钥与邮箱授权码仅保存在本地 `.env` 中。项目已预配置 `.gitignore`，杜绝密钥泄露风险。

---

## 🛠️ 快速上手指南

### 1. 准备工作
在开始之前，请确保你拥有：
- **AI API Key**: [Google Gemini](https://aistudio.google.com/) 或 [阿里通义千问 (DashScope)](https://dashscope.console.aliyun.com/)。
- **邮箱授权码**: 用于发送邮件的 Gmail 应用专用密码或 QQ 邮箱授权码。

### 2. 获取代码与安装
```bash
# 克隆仓库
git clone [https://github.com/Msecala/AI-News-Newsletter-Assistant.git](https://github.com/Msecala/AI-News-Newsletter-Assistant.git)
cd AI-News-Newsletter-Assistant

# 安装依赖
pip install -r requirements.txt
3. 一键初始化 (🌟 推荐)
直接运行交互式安装脚本，按照提示输入你的配置：

Bash
python setup.py
小技巧：在配置完成后，脚本会询问你是否“立刻执行第一次抓取”。输入 y，你将在 1 分钟内收到第一份 AI 简报！

⚙️ 进阶自定义
修改订阅源 (feeds.opml):
使用文本编辑器打开 feeds.opml，你可以自由添加、删除或分类你喜欢的 RSS 链接。

手动调整配置:

.env: 修改 API 密钥和邮箱密码。

config.ini: 修改 AI 模型选择、输出语言、AI 人设以及发送时间。

日常运行:
如果你想手动启动服务并进入定时调度模式，只需运行：

Bash
python main.py
📂 文件结构说明
Plaintext
.
├── main.py           # 核心调度器：负责任务分发、RSS 抓取与 AI 总结
├── emailer.py        # 邮件引擎：负责 HTML 排版与 SMTP 发送
├── setup.py          # 交互式初始化向导
├── feeds.opml        # 订阅源清单 (支持 OPML 标准)
├── requirements.txt  # 项目依赖包
└── .gitignore        # Git 忽略配置（保护敏感文件）
⚠️ 安全提示
本项目的 .env 和 config.ini 包含高度敏感的 API 密钥和邮箱密码。请务必不要删除 .gitignore 记录，也请不要将这两个文件上传至任何公开的代码仓库。

📄 开源协议
本项目采用 GPL-3.0 license 开源。