# 📰 AI 新闻简报助手 (AI News Newsletter Assistant)

这是一个高度自动化的 AI 新闻聚合与摘要工具。它能够定时抓取你指定的 RSS 订阅源，使用多线程加速获取内容，并通过大语言模型（支持 **Gemini** 和 **Qwen**）对海量资讯进行浓缩与全局宏观分析，最终将排版精美的图文简报准时发送到你的邮箱。

## ✨ 核心特性

- **🪄 一键交互式初始化**：告别繁琐的手动配置！运行 `setup.py`，跟随引导一分钟内自动生成所有配置文件，并可立即体验首次抓取。
- **🚀 高效并发抓取**：采用多线程技术并发拉取 RSS 源，极大提升网络请求速度。
- **🧠 智能长文本处理 (Map-Reduce)**：先按批次“脱水”浓缩，再进行全局深度总结，完美避开大模型 Token 限制，显著提升宏观局势分析质量。
- **🛡️ 隐私与安全优先**：敏感 API 密钥与邮箱授权码仅保存在本地 `.env` 中，代码与配置彻底分离。
- **🖼️ 图文精美排版**：自动提取新闻首图，并在 HTML 邮件中进行精美的自适应排版。
- **🗂️ 智能去重机制**：本地缓存历史链接，确保每天推送的简报只包含全新的资讯，拒绝信息轰炸。
- **🌐 多语言无缝同化**：无障碍阅读全球多语种新闻，统一输出为你设定的目标语言（如繁体中文、简体中文或英文）。

---

## 🛠️ 快速上手指南

### 1. 准备工作

在开始之前，你需要准备好以下两样东西：
1. **大模型 API Key**：[Google Gemini API](https://aistudio.google.com/) 或 [阿里通义千问 (DashScope) API](https://dashscope.console.aliyun.com/)。
2. **邮箱授权码**：用于发信的邮箱（支持 Gmail 或 QQ 邮箱）。
   - **Gmail**: 需要在 Google 账号设置中开启两步验证，并生成“应用专用密码”。
   - **QQ 邮箱**: 需要在邮箱设置中开启 SMTP 服务，并生成“授权码”。

### 2. 获取代码与安装依赖

将代码拉取到本地或服务器，并安装必要的 Python 库（建议 Python 3.8+）：

```bash
# 克隆仓库
git clone [https://github.com/你的用户名/你的仓库名.git](https://github.com/你的用户名/你的仓库名.git)
cd 你的仓库名

# (可选) 创建并激活虚拟环境
python -m venv venv
source venv/bin/activate  # Windows 用户使用: venv\Scripts\activate

# 安装依赖项
pip install -r requirements.txt