from playwright.async_api import async_playwright
import requests
import asyncio


# ----------- 展開 Google Maps 短網址 --------------
def expand_url(url: str) -> str:
    try:
        r = requests.head(url, allow_redirects=True, timeout=10)
        return r.url
    except:
        return url


# ----------- Playwright 抓 Google Maps 評論（最新版） --------------
async def scrape_reviews(url: str, limit: int = 100):

    url = expand_url(url)

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"]
        )

        page = await browser.new_page()
        print("Opening:", url)
        await page.goto(url, timeout=60000)

        # 點擊全部評論
        try:
            await page.click("button[jsaction*='reviews']")
            await page.wait_for_timeout(2000)
        except Exception as e:
            print("⚠️ 找不到評論按鈕:", e)

        # 等待 modal 出現
        modal = page.locator("div[role='dialog']")
        try:
            await modal.wait_for(timeout=8000)
        except:
            print("❌ 找不到評論彈窗")
            return []

        # 滾動 modal 
        for _ in range(40):
            await modal.evaluate("(el) => el.scrollBy(0, 2000)")
            await page.wait_for_timeout(500)

        # 抓評論項目
        review_items = modal.locator("div[jscontroller='fIQfXe']")
        count = await review_items.count()

        print("找到評論數：", count)

        results = []

        for i in range(min(count, limit)):
            try:
                item = review_items.nth(i)

                author = await item.locator("div[role='heading']").inner_text()

                text_el = item.locator("span[jscontroller='MznMVe']")
                text = await text_el.inner_text() if await text_el.count() > 0 else ""

                rating_el = item.locator("span[aria-label*='星']")
                rating = await rating_el.get_attribute("aria-label") if await rating_el.count() > 0 else ""

                date_el = item.locator("span.DeMhIe")
                date = await date_el.inner_text() if await date_el.count() > 0 else ""

                results.append({
                    "author": author,
                    "text": text,
                    "rating": rating,
                    "date": date
                })
            except:
                continue

        await browser.close()
        return results
