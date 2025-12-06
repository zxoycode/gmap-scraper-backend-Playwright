from fastapi import FastAPI, Query
import asyncio
from scraper import scrape_reviews

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Google Maps Playwright Scraper is running!"}

@app.get("/scrape")
async def scrape(
    url: str = Query(..., description="Google Maps URL（支援短網址）"),
    limit: int = Query(100, description="評論數量上限")
):
    reviews = await scrape_reviews(url, limit)
    return {
        "count": len(reviews),
        "reviews": reviews
    }
