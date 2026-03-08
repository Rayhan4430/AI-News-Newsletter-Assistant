import feedparser
import requests
import schedule
import time
import traceback
import os
import configparser
import xml.etree.ElementTree as ET
import concurrent.futures
import re
import html
import json
from datetime import datetime
from dotenv import load_dotenv
from emailer import send_newsletter_email
from google import genai
import dashscope

# ==========================================
# ⚙️ 全局核心配置区 (读取 .env 和 config.ini)
# ==========================================
load_dotenv()

config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "").strip()
dashscope.api_key = DASHSCOPE_API_KEY

ACTIVE_MODEL = config.get('Settings', 'ACTIVE_MODEL', fallback='qwen').strip()
TARGET_LANGUAGE = config.get('Settings', 'TARGET_LANGUAGE', fallback='简体中文').strip()
USER_PROMPT = config.get('Settings', 'USER_PROMPT', fallback='总结新闻').strip()
SCHEDULE_TIME = config.get('Settings', 'SCHEDULE_TIME', fallback='08:00').strip()

OPML_FILE_PATH = "feeds.opml"
CACHE_FILE = "seen_links.json"


# ==========================================
# 🛠️ 辅助功能与数据清洗
# ==========================================

def load_rss_from_opml(file_path):
    """从 OPML 文件加载 RSS 订阅源"""
    rss_dict = {}
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        for outline in root.findall('.//outline'):
            if outline.get('type') == 'rss':
                title = outline.get('title')
                xmlUrl = outline.get('xmlUrl')
                category = outline.get('category') or "默认分类"
                if category not in rss_dict:
                    rss_dict[category] = []
                rss_dict[category].append(xmlUrl)
        return rss_dict
    except Exception as e:
        print(f"❌ 解析 OPML 文件出错: {e}")
        return {}


def load_cache():
    """读取本地新闻链接缓存"""
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                return set(json.load(f))
        except Exception:
            return set()
    return set()


def save_cache(seen_links):
    """保存新闻链接缓存 (保留最近 2000 条)"""
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(list(seen_links)[-2000:], f, ensure_ascii=False)


def clean_text(raw_text):
    """清洗摘要文本：去除 HTML，限制长度"""
    if not raw_text:
        return "无摘要"
    clean = re.sub(r'<[^>]+>', '', raw_text)
    clean = html.unescape(clean)
    clean = re.sub(r'\s+', ' ', clean).strip()
    return clean[:200] + "..." if len(clean) > 200 else clean


# ==========================================
# 🕸️ 核心抓取逻辑 (返回列表而非长文本)
# ==========================================

def fetch_single_feed(category, url, seen_links):
    """抓取单个 RSS 源并提取首图"""
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36'}
    results = []
    try:
        response = requests.get(url.strip(), headers=headers, timeout=10)
        response.raise_for_status()
        feed = feedparser.parse(response.content)

        for entry in feed.entries[:10]:
            link = entry.get("link", "#")
            if link in seen_links:
                continue

            title = entry.get("title", "无标题")
            raw_summary = entry.get("summary", "")

            # 🖼️ 提取首图链接
            image_url = ""
            if 'media_content' in entry and len(entry.media_content) > 0:
                image_url = entry.media_content[0].get('url', '')
            elif 'media_thumbnail' in entry and len(entry.media_thumbnail) > 0:
                image_url = entry.media_thumbnail[0].get('url', '')
            elif '<img' in raw_summary:
                img_match = re.search(r'<img[^>]+src=[\'"]([^\'"]+)[\'"]', raw_summary)
                if img_match:
                    image_url = img_match.group(1)

            results.append({
                'category': category,
                'title': title,
                'summary': clean_text(raw_summary),
                'link': link,
                'image_url': image_url
            })
    except Exception as e:
        print(f"⚠️ 抓取跳过 ({url}) - 错误: {str(e)[:50]}")
    return results


def fetch_rss_data():
    """多线程并发抓取主入口"""
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🚀 开始多线程抓取新闻数据...")
    rss_pool = load_rss_from_opml(OPML_FILE_PATH)
    if not rss_pool:
        return []

    seen_links = load_cache()
    new_links = set()
    tasks = [(cat, url) for cat, urls in rss_pool.items() for url in urls]

    news_list = []  # 🔧 修改：使用列表存储单条新闻，方便后续分块
    total_articles = 0

    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        future_to_url = {executor.submit(fetch_single_feed, cat, url, seen_links): url for cat, url in tasks}
        for future in concurrent.futures.as_completed(future_to_url):
            for item in future.result():
                img_info = f"\n图片：{item['image_url']}" if item['image_url'] else ""
                # 将格式化后的单条新闻加入列表
                news_item = f"【领域：{item['category']}】\n标题：{item['title']}\n摘要：{item['summary']}\n链接：{item['link']}{img_info}"
                news_list.append(news_item)
                new_links.add(item['link'])
                total_articles += 1

    if new_links:
        seen_links.update(new_links)
        save_cache(seen_links)

    print(f"✅ 抓取完毕！获取了 {total_articles} 条未读新闻。")
    return news_list


# ==========================================
# 🧠 AI 大模型生成逻辑 (Map-Reduce 架构)
# ==========================================

def call_gemini(prompt):
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        return response.text
    except Exception as e:
        print(f"❌ Gemini 调用失败: {e}")
        return None


def call_qwen(prompt):
    try:
        response = dashscope.Generation.call(
            model=dashscope.Generation.Models.qwen_turbo,
            prompt=prompt,
        )
        if response.status_code == 200:
            return response.output.text
        else:
            print(f"❌ Qwen 调用失败: {response.code} - {response.message}")
            return None
    except Exception as e:
        print(f"❌ Qwen 调用失败: {e}")
        return None


def generate_ai_report(news_list):
    if not news_list:
        print("⚠️ 没有新数据，跳过 AI 生成。")
        return None

    print(f"🧠 准备处理 {len(news_list)} 条新闻，启动分块浓缩 (Map-Reduce)...")

    # 🔧 设定每批次处理条数，控制 Token 消耗
    BATCH_SIZE = 10
    intermediate_summaries = []

    # 【阶段一：Map】分块初步浓缩，过滤无效信息
    for i in range(0, len(news_list), BATCH_SIZE):
        batch = news_list[i:i + BATCH_SIZE]
        batch_text = "\n\n".join(batch)

        print(f"⏳ 正在浓缩第 {i // BATCH_SIZE + 1} 批数据 ({len(batch)} 条)...")
        map_prompt = f"""
                请阅读以下批次的新闻数据。你的任务是进行初步的数据压缩：
                1. 剔除无效、重复或纯粹的情感宣泄类水文。
                2. 提取有价值的宏观事件和产业动态，务必保留原有的领域、标题、核心结论、链接和图片链接（如果有）。
                3. 重点留意可能影响主要经济体货币政策、资金流向或全球供应链的资讯。
                4. ⚠️ 无论原文是什么语言，请务必统一使用【{TARGET_LANGUAGE}】输出提炼结果。 # 👈 新增这一行

                批次新闻数据：
                {batch_text}
                """
        summary = call_gemini(map_prompt) if ACTIVE_MODEL.lower() == "gemini" else call_qwen(map_prompt)
        if summary:
            intermediate_summaries.append(summary)

    if not intermediate_summaries:
        return None

    # 【阶段二：Reduce】全局合并，深度解析
    print("🧠 正在根据浓缩数据生成最终深度简报...")
    combined_context = "\n\n=== 批次分割线 ===\n\n".join(intermediate_summaries)

    final_prompt = f"""
    你是一个专业的主编与宏观策略分析师。用户的定制规则是：【{USER_PROMPT}】
    以下是过去一段时间全球重点新闻的提炼汇总。
    任务：
    1. 整合报道同一事件的不同新闻源，梳理底层宏观逻辑，特别是对全球资本市场（如美股、港股、日股）的潜在影响。
    2. 无论原文是什么语言，必须统一使用【{TARGET_LANGUAGE}】输出。
    3. 严格使用以下 Markdown 格式输出：

    ### [新闻核心标题]
    > [一句话核心结论]

    [如果有图片链接，请务必在这里用Markdown格式插入配图：![封面图](图片链接)]

    **深度解析与市场前瞻：**
    [用 2-3 个要点展开说明，指出该事件对宏观资产配置的可能影响，权衡防守型资产与进攻型资产的策略倾向]
    [🔗 阅读原文](链接)

    ---
    提炼汇总数据：
    {combined_context}
    """

    final_report = call_gemini(final_prompt) if ACTIVE_MODEL.lower() == "gemini" else call_qwen(final_prompt)
    if final_report:
        print(f"✅ 最终 AI 简报生成成功！(模型: {ACTIVE_MODEL.upper()})")
        return final_report.strip()
    return None


# ==========================================
# 📧 邮件发送与主调度
# ==========================================

def safe_send_email(content):
    if not content: return
    if isinstance(content, bytes):
        content = content.decode('utf-8', errors='ignore')
    elif not isinstance(content, str):
        content = str(content)
    content = content.encode('utf-8', errors='replace').decode('utf-8')
    try:
        send_newsletter_email(content)
        print("📧 邮件发送任务完成！")
    except UnicodeEncodeError:
        content_clean = content.encode('gbk', errors='ignore').decode('gbk', errors='ignore')
        send_newsletter_email(content_clean)


def job_pipeline():
    try:
        raw_news_list = fetch_rss_data()
        ai_report = generate_ai_report(raw_news_list)
        if ai_report:
            safe_send_email(ai_report)
    except Exception as e:
        print(f"❌ 任务执行出错:\n{traceback.format_exc()}")


if __name__ == "__main__":
    print(f"🚀 AI 新闻简报服务已启动！每天 {SCHEDULE_TIME} 自动运行。按 Ctrl+C 退出。")
    # 启动时立刻执行一次测试 (测试完可注释掉)
    job_pipeline()

    schedule.every().day.at(SCHEDULE_TIME).do(job_pipeline)
    while True:
        schedule.run_pending()
        time.sleep(60)