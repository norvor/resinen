# backend/app/services.py
import httpx
import random
import feedparser
from datetime import datetime, timezone, timedelta

# --- 0. ROBUST FALLBACKS (The Safety Net) ---
FALLBACKS = {
    "art": {
        "url": "https://www.artic.edu/iiif/2/25c31d8d-21a4-9ea9-11c1-ac333d963f7b/full/843,/0/default.jpg",
        "title": "Nighthawks (Offline Mode)",
        "artist": "Edward Hopper",
        "source": "AIC ARCHIVE"
    },
    "animal": {
        "type": "FOX",
        "url": "https://images.pexels.com/photos/47547/squirrel-animal-cute-rodents-47547.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1" 
    },
    "food": "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80",
    "uplifting": [
        {"title": "Global Reforestation Efforts Hit Record High", "link": "https://www.dailygood.org/"},
        {"title": "Community Garden Feeds Thousands in Local City", "link": "https://www.dailygood.org/"}
    ]
}

# --- 1. CONFIG & SYSTEM ---
def get_audio_config():
    return {
        "lotr": { "name": "RIVENDELL", "id": "WsnlMXBPDnE", "icon": "💍", "color": "#fbbf24" },
        "disney": { "name": "MAGIC KINGDOM", "id": "FZmm7u4NZ4U", "icon": "🏰", "color": "#60a5fa" },
        "hp": { "name": "HOGWARTS", "id": "-6tapuMp8Z4", "icon": "⚡", "color": "#facc15" },
        "atla": { "name": "SPIRIT OASIS", "id": "_MD4tmvFADs", "icon": "🌊", "color": "#2dd4bf" }
    }

async def get_system_status():
    return [
        {"name": "NET", "status": "operational"}, 
        {"name": "CORE", "status": "operational"}, 
        {"name": "UPLINK", "status": "operational"}
    ]

# --- 2. PLANETARY STATE ---
def get_planetary_state():
    now = datetime.now(timezone.utc)
    start = datetime(now.year, 1, 1, tzinfo=timezone.utc)
    end = datetime(now.year + 1, 1, 1, tzinfo=timezone.utc)
    percent = ((now - start).total_seconds() / (end - start).total_seconds()) * 100
    
    cities = [
        {"name": "PARIS", "tz": 1, "icon": "☁️"},
        {"name": "MUMBAI", "tz": 5.5, "icon": "🌫️"},
        {"name": "NYC", "tz": -5, "icon": "☀️"},
        {"name": "TOKYO", "tz": 9, "icon": "🌧️"}
    ]
    watch = [{"city": c['name'], "time": (now + timedelta(hours=c['tz'])).strftime("%H:%M"), "icon": c['icon']} for c in cities]
    return {"year_pct": f"{percent:.6f}", "watch": watch}

# --- 3. VISUALS AGGREGATOR ---
async def get_visual_feeds(art_source: str = "met"):
    async with httpx.AsyncClient(timeout=5.0) as client:
        results = {}

        # A. ART (Try AIC -> MET -> Fallback)
        try:
            # Art Institute of Chicago (Specific Fields for lighter payload)
            page = random.randint(1, 40)
            url = f"https://api.artic.edu/api/v1/artworks?page={page}&limit=1&fields=id,title,image_id,artist_display"
            resp = await client.get(url)
            data = resp.json()
            if data['data'] and data['data'][0]['image_id']:
                artwork = data['data'][0]
                results['art'] = {
                    "url": f"https://www.artic.edu/iiif/2/{artwork['image_id']}/full/843,/0/default.jpg",
                    "title": artwork['title'],
                    "artist": artwork['artist_display'],
                    "source": "AIC CHICAGO"
                }
            else:
                raise Exception("No Image ID")
        except:
            # Fail silently to fallback
            results['art'] = FALLBACKS['art']

        # B. ANIMALS (Try Dog CEO -> RandomFox -> Fallback)
        try:
            # Dog CEO
            r = await client.get("https://dog.ceo/api/breeds/image/random")
            data = r.json()
            if data['status'] == 'success':
                url = data['message']
                # Clean breed name from URL
                breed = "DOG"
                if "/breeds/" in url:
                    try:
                        breed = url.split("/breeds/")[1].split("/")[0].replace("-", " ").title()
                    except: pass
                results['animal'] = {"type": breed, "url": url}
            else:
                raise Exception("Dog API Failed")
        except:
            # Fallback to RandomFox if Dog fails
            try:
                r = await client.get("https://randomfox.ca/floof/")
                results['animal'] = {"type": "FOX", "url": r.json()['image']}
            except:
                results['animal'] = FALLBACKS['animal']

        # C. FOOD (TheMealDB -> Fallback)
        try:
            r = await client.get("https://www.themealdb.com/api/json/v1/1/random.php")
            data = r.json()
            if data['meals']:
                results['food'] = data['meals'][0]['strMealThumb']
            else:
                raise Exception("No Meal Data")
        except:
            results['food'] = FALLBACKS['food']

        return results

# --- 4. DATA FEEDS (NEWS AGGREGATOR) ---
def parse_rss_robust(url, limit=4):
    """Parses RSS with feedparser, returns empty list on failure"""
    try:
        feed = feedparser.parse(url)
        items = []
        for entry in feed.entries[:limit]:
            items.append({
                "title": entry.title,
                "link": entry.link
            })
        return items
    except:
        return []

async def get_new_feeds():
    async with httpx.AsyncClient() as client:
        data = {}

        # A. MARKETS (Simulated)
        base_sp, base_gold, base_brent = 5200.00, 2350.00, 85.00
        sp = base_sp * random.uniform(0.995, 1.005)
        gold = base_gold * random.uniform(0.995, 1.005)
        brent = base_brent * random.uniform(0.99, 1.01)
        data['markets'] = [
            {"name": "S&P 500", "price": f"{sp:.2f}", "change": f"{random.uniform(-1.2, 1.2):.2f}%"},
            {"name": "GOLD", "price": f"{gold:.2f}", "change": f"{random.uniform(-0.8, 0.8):.2f}%"},
            {"name": "BRENT", "price": f"{brent:.2f}", "change": f"{random.uniform(-2.0, 2.0):.2f}%"}
        ]

        # B. NEWS HUB FEEDS
        data['business'] = parse_rss_robust("http://feeds.bbci.co.uk/news/business/rss.xml")
        data['sports'] = parse_rss_robust("http://feeds.bbci.co.uk/sport/rss.xml")
        data['culture'] = parse_rss_robust("https://www.theguardian.com/culture/rss")
        data['global'] = parse_rss_robust("http://feeds.bbci.co.uk/news/world/rss.xml")

        # C. UPLIFTING FEED (Using DailyGood RSS)
        uplifting = parse_rss_robust("https://www.dailygood.org/rss/", limit=2)
        data['uplifting'] = uplifting if uplifting else FALLBACKS['uplifting']

        # D. HISTORY
        try:
            # Note: history.muffinlabs.com is great but sometimes slow
            r = await client.get(f"https://history.muffinlabs.com/date/{datetime.now().month}/{datetime.now().day}", timeout=3.0)
            fact = random.choice(r.json()['data']['Events'])
            data['history'] = {"year": fact['year'], "text": fact['text']}
        except:
            data['history'] = {"year": "2026", "text": "Resinen Systems operational."}

        # E. JOKE
        try:
            r = await client.get("https://official-joke-api.appspot.com/random_joke", timeout=2.0)
            data['joke'] = r.json()
        except: 
            data['joke'] = {"setup": "Why did the server crash?", "punchline": "It had a bad driver."}

        return data

# --- 5. ZEN ---
async def get_zen_wisdom():
    quotes = ["The obstacle is the path.", "Act without expectation.", "Stillness speaks.", "Nature does not hurry.", "Be water, my friend."]
    return {"text": random.choice(quotes)}