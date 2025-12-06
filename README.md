# Google Maps Review Scraper (Playwright + FastAPI)

This project scrapes Google Maps reviews using Playwright (headless Chromium), 
as a cost-effective alternative to SerpAPI.

## Features
- Supports Google Maps short URLs (maps.app.goo.gl)
- Scrolls automatically to load more reviews
- Extracts user, rating, text, and date
- Deployable on Render / Railway

## API Usage

GET /scrape?url=<google-maps-url>&limit=100

Example:
https://your-render-app.onrender.com/scrape?url=https://maps.app.goo.gl/...&limit=100

## Run locally

pip install -r requirements.txt
playwright install chromium
uvicorn main:app --reload

## Deploy on Render
Select:
- Environment: Docker
- Dockerfile: ./Dockerfile
- Port: 10000
