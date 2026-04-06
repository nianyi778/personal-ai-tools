#!/usr/bin/env python3
"""Auto-publish video to Douyin creator platform with QR code login."""

from playwright.sync_api import sync_playwright
import time, os

VIDEO   = "/Users/likai/Downloads/gujo_01_highlight_final.mp4"
TITLE   = "雨の日だから、この町が好きになった"
DESC    = """雨天的郡上八幡，比晴天更让人想念。

古街、水声、雾气——
这种安静，城市里找不到。

🎧 建议戴耳机
#郡上八幡 #日本旅行 #城市漫步 #治愈系 #沉浸式旅行 #旅行vlog"""

def wait(msg, secs=2):
    print(f"  ⏳ {msg}")
    time.sleep(secs)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, slow_mo=500)
    ctx = browser.new_context(
        viewport={"width": 1280, "height": 900},
        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    page = ctx.new_page()

    # ── Step 1: Open login page ──────────────────────────
    print("\n📱 打开抖音创作者平台...")
    page.goto("https://creator.douyin.com/", wait_until="networkidle")
    wait("等待页面加载", 3)

    # Screenshot for user to see
    page.screenshot(path="/tmp/douyin_step1.png")
    print("  截图已保存: /tmp/douyin_step1.png")

    # Check if already logged in
    if "creator-micro" in page.url or page.query_selector(".creator-header"):
        print("  ✅ 已登录")
    else:
        print("\n🔐 请在打开的浏览器窗口中扫码登录...")
        print("  等待登录完成（最多60秒）...")
        try:
            page.wait_for_url("**/creator-micro/**", timeout=60000)
            print("  ✅ 登录成功！")
        except:
            # Try waiting for any sign of login
            wait("继续等待...", 5)

    wait("跳转到上传页面", 2)

    # ── Step 2: Go to upload page ────────────────────────
    print("\n📤 跳转到视频上传页面...")
    page.goto("https://creator.douyin.com/creator-micro/content/upload", wait_until="networkidle")
    wait("等待上传页面加载", 3)
    page.screenshot(path="/tmp/douyin_step2.png")

    # ── Step 3: Upload video file ────────────────────────
    print(f"\n🎬 上传视频: {os.path.basename(VIDEO)}")
    try:
        # Find file input
        file_input = page.query_selector('input[type="file"]')
        if file_input:
            file_input.set_input_files(VIDEO)
            print("  文件已选择，等待上传...")
            wait("上传中（视频较大，请耐心等待）", 10)
        else:
            print("  ⚠️ 未找到文件输入框，尝试点击上传区域...")
            upload_area = page.query_selector('.upload-drag-content') or \
                         page.query_selector('[class*="upload"]') or \
                         page.query_selector('[class*="drag"]')
            if upload_area:
                upload_area.click()
                wait("等待文件对话框", 2)
    except Exception as e:
        print(f"  ⚠️ 上传异常: {e}")

    page.screenshot(path="/tmp/douyin_step3.png")

    # ── Step 4: Fill title ───────────────────────────────
    print(f"\n✏️  填写标题: {TITLE}")
    wait("等待表单加载", 5)
    try:
        # Try various title input selectors
        title_selectors = [
            'input[placeholder*="标题"]',
            'textarea[placeholder*="标题"]',
            '.title-input input',
            '[class*="title"] input',
        ]
        title_filled = False
        for sel in title_selectors:
            el = page.query_selector(sel)
            if el:
                el.click()
                el.fill(TITLE)
                title_filled = True
                print(f"  ✅ 标题已填写 (selector: {sel})")
                break
        if not title_filled:
            print("  ⚠️ 未找到标题输入框，请手动填写")
    except Exception as e:
        print(f"  ⚠️ 标题填写异常: {e}")

    # ── Step 5: Fill description ─────────────────────────
    print("\n📝 填写正文描述...")
    wait("", 1)
    try:
        desc_selectors = [
            'textarea[placeholder*="描述"]',
            'textarea[placeholder*="介绍"]',
            '.desc-input textarea',
            '[class*="desc"] textarea',
            '[contenteditable="true"]',
        ]
        desc_filled = False
        for sel in desc_selectors:
            el = page.query_selector(sel)
            if el:
                el.click()
                el.fill(DESC)
                desc_filled = True
                print(f"  ✅ 描述已填写 (selector: {sel})")
                break
        if not desc_filled:
            print("  ⚠️ 未找到描述输入框，请手动填写")
    except Exception as e:
        print(f"  ⚠️ 描述填写异常: {e}")

    # ── Step 6: Screenshot for confirmation ─────────────
    wait("截图确认", 2)
    page.screenshot(path="/tmp/douyin_step4_confirm.png")
    print("\n📸 截图已保存: /tmp/douyin_step4_confirm.png")
    print("\n" + "="*50)
    print("⚠️  请检查浏览器窗口中的内容是否正确")
    print("    确认无误后，请手动点击【发布】按钮")
    print("    或按 Enter 键让脚本尝试自动点击发布")
    print("="*50)
    input("\n按 Enter 继续（自动点击发布）或 Ctrl+C 取消...")

    # ── Step 7: Publish ──────────────────────────────────
    print("\n🚀 尝试点击发布按钮...")
    try:
        publish_selectors = [
            'button:has-text("发布")',
            'button:has-text("提交")',
            '[class*="publish"] button',
            '.publish-btn',
        ]
        published = False
        for sel in publish_selectors:
            btn = page.query_selector(sel)
            if btn and btn.is_visible():
                btn.click()
                published = True
                print(f"  ✅ 已点击发布 (selector: {sel})")
                break
        if not published:
            print("  ⚠️ 未找到发布按钮，请手动点击")
    except Exception as e:
        print(f"  ⚠️ 发布异常: {e}")

    wait("等待发布结果", 5)
    page.screenshot(path="/tmp/douyin_step5_result.png")
    print("\n📸 发布结果截图: /tmp/douyin_step5_result.png")
    print("\n浏览器保持开启，请查看结果。按 Enter 关闭...")
    input()
    browser.close()
    print("\n✅ 完成！")
