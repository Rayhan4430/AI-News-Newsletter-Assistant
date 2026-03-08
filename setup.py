import configparser
import subprocess
import sys

def prompt(message, default=""):
    """辅助函数：带默认值的输入提示"""
    if default:
        res = input(f"{message} [默认: {default}]: ").strip()
        return res if res else default
    else:
        return input(f"{message}: ").strip()

def main():
    print("=" * 50)
    print("🚀 欢迎使用 AI 新闻简报助手初始化引导")
    print("=" * 50)
    print("接下来我们将花一分钟时间，帮你配置好项目参数。\n")

    # ---------------------------------------------------------
    # 第一部分：配置大模型 API 密钥
    # ---------------------------------------------------------
    print("--- 🧠 1. 大模型 API 配置 ---")
    active_model = prompt("请选择你想使用的主力 AI 模型 (qwen 或 gemini)", "qwen").lower()

    gemini_key = ""
    qwen_key = ""

    if active_model == "gemini":
        gemini_key = prompt("请输入你的 Gemini API Key (必填)")
        qwen_key = prompt("请输入你的 DashScope (Qwen) API Key (选填，留空即可)")
    else:
        qwen_key = prompt("请输入你的 DashScope (Qwen) API Key (必填)")
        gemini_key = prompt("请输入你的 Gemini API Key (选填，留空即可)")

    # ---------------------------------------------------------
    # 第二部分：配置邮箱服务
    # ---------------------------------------------------------
    print("\n--- 📧 2. 邮箱服务配置 ---")
    provider = prompt("请选择发件邮箱服务商 (gmail 或 qq)", "gmail").lower()
    sender_email = prompt("请输入用于【发送】简报的发件箱地址 (如 xxx@gmail.com)")

    email_password = ""
    if provider == "qq":
        print("💡 提示：QQ邮箱需要填写的不是登录密码，而是 16 位 SMTP 授权码。")
        email_password = prompt("请输入 QQ 邮箱授权码")
    else:
        print("💡 提示：Gmail 需要填写的不是登录密码，而是 16 位应用专用密码。")
        email_password = prompt("请输入 Gmail 应用专用密码")

    receiver_email = prompt("请输入用于【接收】简报的邮箱地址 (可以和发件箱一样)", sender_email)

    # ---------------------------------------------------------
    # 第三部分：个性化偏好设置
    # ---------------------------------------------------------
    print("\n--- 🎨 3. 个性化偏好配置 ---")
    target_language = prompt("请设定简报的输出语言", "简体中文")
    user_prompt = prompt("请设定 AI 的人设与关注点", "让我充分了解过去24h的世界局势，摘要里给出可能的投资建议")
    schedule_time = prompt("请设定每天自动发送的时间 (24小时制)", "08:00")

    # ---------------------------------------------------------
    # 第四部分：生成配置文件
    # ---------------------------------------------------------
    print("\n⏳ 正在生成配置文件...")

    # 1. 生成 .env 文件
    env_content = f"""# ==========================================
# 🔑 API 密钥 (切记：不要把此文件传到公开仓库)
# ==========================================
GEMINI_API_KEY={gemini_key}
DASHSCOPE_API_KEY={qwen_key}

# 邮箱密码/授权码 (根据 config.ini 里选择的提供商生效)
QQ_EMAIL_PASSWORD={email_password if provider == 'qq' else ''}
GMAIL_APP_PASSWORD={email_password if provider == 'gmail' else ''}
"""
    with open(".env", "w", encoding="utf-8") as f:
        f.write(env_content)
    print("✅ .env 文件已生成。")

    # 2. 生成 config.ini 文件
    config = configparser.ConfigParser()
    config.add_section('Settings')
    config.set('Settings', 'ACTIVE_MODEL', active_model)
    config.set('Settings', 'TARGET_LANGUAGE', target_language)
    config.set('Settings', 'USER_PROMPT', user_prompt)
    config.set('Settings', 'SCHEDULE_TIME', schedule_time)

    config.add_section('Email')
    config.set('Email', 'PROVIDER', provider)
    config.set('Email', 'RECEIVER_EMAIL', receiver_email)

    config.add_section('SMTP_QQ')
    config.set('SMTP_QQ', 'SERVER', 'smtp.qq.com')
    config.set('SMTP_QQ', 'PORT', '465')
    config.set('SMTP_QQ', 'SENDER', sender_email if provider == 'qq' else '')

    config.add_section('SMTP_Gmail')
    config.set('SMTP_Gmail', 'SERVER', 'smtp.gmail.com')
    config.set('SMTP_Gmail', 'PORT', '465')
    config.set('SMTP_Gmail', 'SENDER', sender_email if provider == 'gmail' else '')

    with open("config.ini", "w", encoding="utf-8") as f:
        config.write(f)
    print("✅ config.ini 文件已生成。")

    print("\n" + "=" * 50)
    print("🎉 初始化全部完成！")
    print("你可以随时编辑 .env 或 config.ini 文件来修改这些配置。")
    print("=" * 50)

    # ---------------------------------------------------------
    # 第五部分：询问是否立即执行抓取
    # ---------------------------------------------------------
    run_now = prompt("\n是否立即启动服务并执行第一次新闻抓取？(y/n)", "y").lower()
    if run_now == 'y':
        print("\n🚀 正在为你拉起主程序，请稍候...\n")
        try:
            # 使用 sys.executable 确保使用当前虚拟环境的 Python 解释器
            subprocess.run([sys.executable, "main.py"])
        except KeyboardInterrupt:
            print("\n⏹️ 服务已手动停止。")
        except Exception as e:
            print(f"\n❌ 启动失败，原因: {e}")
            print("请尝试手动运行: python main.py")
    else:
        print("\n好的，后续你可以随时通过运行 `python main.py` 来启动服务。")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ 初始化已取消。")