from playwright.async_api import async_playwright
import asyncio
import re
import requests

# ----------- 展開 Google Maps 短網址 --------------
def expand_url(url: str) -> str:
    try:
        r = requests.head(url, allow_redirects=True, timeout=10)
        return r.url
    except:
        return url


# ----------- Playwright 抓 Google Maps 評論 ----------
async def scrape_reviews(url: str, limit: int = 100):
    url = expand_url(url)

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage"
            ]
        )
        context = await browser.new_context()
        page = await context.new_page()

        await page.goto(url, wait_until="networkidle")

        # 點擊「全部評論」按鈕
        try:
            await page.click("button[jsaction*='reviews']")
        except:
            print("找不到評論按鈕，但仍然嘗試直接抓資料")

        await page.wait_for_timeout(1500)

        # 滾動評論直到達到 limit
        reviews = []
        last_height = None

        while len(reviews) < limit:
            # 抓出所有評論文字
            items = await page.query_selector_all("div[jscontroller='eIu7Db']")
            for item in items:
                text = (await item.inner_text()).strip()
                if text and text not in reviews:
                    reviews.append(text)

            # 滾動到底部
            current_height = await page.evaluate("document.body.scrollHeight")
            if current_height == last_height:
                break
            last_height = current_height

            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await page.wait_for_timeout(1200)

        await browser.close()

        return reviews[:limit]
