import asyncio
from playwright.async_api import async_playwright
import time

async def scrape_reviews(url: str, limit: int = 100):
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-setuid-sandbox"
            ]
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        )
        page = await context.new_page()

        print(f"Opening: {url}")
        await page.goto(url, timeout=60000)

        # 點擊評論面板
        try:
            await page.wait_for_selector("button[jsaction*='pane.reviewChart']", timeout=8000)
            await page.click("button[jsaction*='pane.reviewChart']")
        except:
            raise Exception("找不到評論按鈕，可能是地點不存在")

        reviews = []

        # 開始滾動抓取
        last_height = None
        for _ in range(50):  # 最多滾 50 次
            cards = await page.query_selector_all("div[jscontroller='Hi8Eje']")
            for c in cards:
                try:
                    user = await c.query_selector("div[class*='d4r55']")
                    user_name = await user.inner_text() if user else None

                    rating_el = await c.query_selector("span[class*='kvMYJc']")
                    rating_raw = await rating_el.get_attribute("aria-label") if rating_el else None
                    rating = rating_raw.replace("stars", "").strip() if rating_raw else None

                    text_el = await c.query_selector("span[class*='wiI7pd']")
                    text = await text_el.inner_text() if text_el else ""

                    date_el = await c.query_selector("span[class*='rsqaWe']")
                    date = await date_el.inner_text() if date_el else ""

                    review_obj = {
                        "user": user_name,
                        "rating": rating,
                        "text": text,
                        "date": date
                    }

                    if review_obj not in reviews:
                        reviews.append(review_obj)

                    if len(reviews) >= limit:
                        await browser.close()
                        return reviews

                except:
                    continue

            # 滾動更多評論
            await page.mouse.wheel(0, 2500)
            time.sleep(1)

        await browser.close()
        return reviews
