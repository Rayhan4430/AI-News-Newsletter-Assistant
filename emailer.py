import smtplib
import markdown
import os
import configparser
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from email.header import Header
from email.utils import formataddr
from dotenv import load_dotenv

# 加载 .env 中的密码
load_dotenv()

# ==========================================
# ⚙️ 读取配置文件
# ==========================================
config = configparser.ConfigParser()
# 指定 utf-8 编码读取，防止中文注释或配置乱码
config.read('config.ini', encoding='utf-8')

# 读取 [Email] 基础配置
EMAIL_PROVIDER = config.get('Email', 'PROVIDER', fallback='qq').lower()
RECEIVER_EMAIL = config.get('Email', 'RECEIVER_EMAIL')

def get_email_config():
    """根据配置文件获取对应的发件服务器信息和密码"""
    if EMAIL_PROVIDER == 'qq':
        return {
            'smtp_server': config.get('SMTP_QQ', 'SERVER'),
            'smtp_port': config.getint('SMTP_QQ', 'PORT'),
            'sender_email': config.get('SMTP_QQ', 'SENDER'),
            'sender_password': os.getenv('QQ_EMAIL_PASSWORD', '')
        }
    elif EMAIL_PROVIDER == 'gmail':
        return {
            'smtp_server': config.get('SMTP_Gmail', 'SERVER'),
            'smtp_port': config.getint('SMTP_Gmail', 'PORT'),
            'sender_email': config.get('SMTP_Gmail', 'SENDER'),
            'sender_password': os.getenv('GMAIL_APP_PASSWORD', '')
        }
    else:
        return None

def send_newsletter_email(markdown_text):
    if not markdown_text:
        print("❌ 没有接收到内容，跳过邮件发送。")
        return

    email_conf = get_email_config()
    if not email_conf or not email_conf['sender_password']:
        print(f"❌ 错误：未找到提供商 '{EMAIL_PROVIDER}' 的有效配置或未在 .env 中设置密码。")
        return

    print(f"📧 正在渲染 HTML 页面并连接 {EMAIL_PROVIDER.upper()} 邮件服务器...")

    # 1. Markdown 转 HTML
    html_body = markdown.markdown(markdown_text, extensions=['extra'])

    # 2. 嵌入 Apple 风格的极简 CSS (保持你原来的代码不变)
    full_html = f"""<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", Roboto, Helvetica, Arial, sans-serif; line-height: 1.6; color: #1D1D1F; max-width: 650px; margin: 0 auto; padding: 20px; background-color: #F5F5F7; }}
        .container {{ background-color: #ffffff; padding: 40px; border-radius: 18px; box-shadow: 0 4px 20px rgba(0,0,0,0.04); }}
        h2 {{ text-align: center; font-weight: 700; letter-spacing: -0.5px; margin-bottom: 5px; }}
        .date {{ text-align: center; color: #86868B; font-size: 14px; margin-bottom: 40px; }}
        h3 {{ color: #1D1D1F; border-bottom: 1px solid #E5E5EA; padding-bottom: 8px; margin-top: 35px; font-weight: 600; }}
        blockquote {{ border-left: 4px solid #007AFF; margin: 0 0 15px 0; padding-left: 16px; color: #555; font-style: normal; background-color: #F5F8FF; padding: 10px 16px; border-radius: 0 8px 8px 0; }}
        p {{ margin-bottom: 12px; }}
        a {{ color: #007AFF; text-decoration: none; font-weight: 500; }}
        a:hover {{ text-decoration: underline; }}
        hr {{ border: 0; height: 1px; background: #E5E5EA; margin: 40px 0; }}
        img {{ width: 100%; height: 200px; object-fit: cover; border-radius: 8px; margin-bottom: 15px; display: block; }}
    </style>
</head>
<body>
    <div class="container">
        <h2>📰 专属 AI 新闻简报</h2>
        <div class="date">{datetime.now().strftime('%Y年%m月%d日')}</div>
        {html_body}
    </div>
</body>
</html>"""

    # 3. 构造邮件载体
    msg = MIMEMultipart()
    msg['From'] = formataddr(('AI简报助手', email_conf['sender_email']))
    msg['To'] = formataddr(('订阅者', RECEIVER_EMAIL))
    msg['Subject'] = Header(f"🌍 每日 AI 视野 - {datetime.now().strftime('%m月%d日')}", 'utf-8')
    msg.attach(MIMEText(full_html, 'html', 'utf-8'))

    # 4. 通过 SSL 发送
    try:
        server = smtplib.SMTP_SSL(email_conf['smtp_server'], email_conf['smtp_port'], timeout=20)
        server.login(email_conf['sender_email'], email_conf['sender_password'])
        server.sendmail(email_conf['sender_email'], [RECEIVER_EMAIL], msg.as_bytes())
        server.quit()
        print(f"\n🎉 邮件发送成功！漂亮的 HTML 简报已通过 {EMAIL_PROVIDER.upper()} 送达。")
    except Exception as e:
        print(f"\n❌ 邮件发送失败，具体原因: {e}")