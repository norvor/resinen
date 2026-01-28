# backend/app/services.py
import httpx
import random
import feedparser
from datetime import datetime, timezone, timedelta

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

# --- 3. ART HELPER FUNCTIONS ---
async def get_met_art(client):
    try:
        search_url = "https://collectionapi.metmuseum.org/public/collection/v1/search?hasImages=true&q=oil%20on%20canvas&medium=Paintings"
        resp = await client.get(search_url, timeout=4.0)
        data = resp.json()
        if data['total'] > 0:
            obj_id = random.choice(data['objectIDs'][:100])
            obj_resp = await client.get(f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{obj_id}", timeout=4.0)
            obj = obj_resp.json()
            return {
                "url": obj.get('primaryImageSmall') or obj.get('primaryImage'),
                "title": obj.get('title', 'Untitled'),
                "artist": obj.get('artistDisplayName', 'Unknown Artist'),
                "source": "MET NEW YORK"
            }
    except Exception as e:
        print(f"MET Error: {e}")
    return None

async def get_aic_art(client):
    try:
        page = random.randint(1, 50)
        url = f"https://api.artic.edu/api/v1/artworks?page={page}&limit=1&fields=id,title,image_id,artist_display"
        resp = await client.get(url, timeout=4.0)
        data = resp.json()
        if data['data']:
            artwork = data['data'][0]
            if artwork['image_id']:
                img_url = f"https://www.artic.edu/iiif/2/{artwork['image_id']}/full/843,/0/default.jpg"
                return {
                    "url": img_url,
                    "title": artwork['title'],
                    "artist": artwork['artist_display'],
                    "source": "AIC CHICAGO"
                }
    except Exception as e:
        print(f"AIC Error: {e}")
    return None

# --- 4. VISUALS AGGREGATOR ---
async def get_visual_feeds(art_source: str = "met"):
    async with httpx.AsyncClient() as client:
        results = {}
        # A. ART
        art_data = None
        if art_source == "aic": art_data = await get_aic_art(client)
        if not art_data: art_data = await get_met_art(client)
        if not art_data: art_data = {"url": "https://images.unsplash.com/photo-1549490349-8643362247b5", "title": "Connection Lost", "artist": "System", "source": "OFFLINE"}
        results['art'] = art_data

        # B. ANIMALS
        try:
            choice = random.choice(['fox', 'dog', 'cat'])
            if choice == 'fox':
                r = await client.get("https://randomfox.ca/floof/", timeout=2.0)
                results['animal'] = {"type": "FOX", "url": r.json()['image']}
            elif choice == 'dog':
                r = await client.get("https://dog.ceo/api/breeds/image/random", timeout=2.0)
                msg = r.json()['message']
                breed = "DOG"
                if '/breeds/' in msg:
                    try: breed = msg.split('/breeds/')[1].split('/')[0].replace('-', ' ').title()
                    except: pass
                results['animal'] = {"type": breed, "url": msg}
            else:
                r = await client.get("https://api.thecatapi.com/v1/images/search", timeout=2.0)
                results['animal'] = {"type": "CAT", "url": r.json()[0]['url']}
        except: 
            results['animal'] = {"type": "OFFLINE", "url": ""}

        # C. FOOD
        try:
            resp = await client.get("https://www.themealdb.com/api/json/v1/1/random.php", timeout=2.0)
            meal = resp.json()['meals'][0]
            results['food'] = meal['strMealThumb']
        except:
            results['food'] = "https://images.unsplash.com/photo-1546069901-ba9599a7e63c"

        return results

# --- 5. DATA FEEDS (NEWS AGGREGATOR) ---
def parse_feed(url, limit=4):
    """Parses a public RSS feed using standard feedparser"""
    try:
        # feedparser handles HTTP requests internally in a standard way
        feed = feedparser.parse(url)
        items = []
        for entry in feed.entries[:limit]:
            items.append({
                "title": entry.title,
                "link": entry.link
            })
        return items
    except Exception as e:
        print(f"RSS Error {url}: {e}")
        return []

async def get_new_feeds():
    # We use httpx for the API calls, but feedparser for RSS
    async with httpx.AsyncClient(follow_redirects=True) as client:
        data = {}

        # A. MARKETS (Simulated for Stability)
        base_sp, base_gold, base_brent = 5200.00, 2350.00, 85.00
        sp = base_sp * random.uniform(0.995, 1.005)
        gold = base_gold * random.uniform(0.995, 1.005)
        brent = base_brent * random.uniform(0.99, 1.01)
        data['markets'] = [
            {"name": "S&P 500", "price": f"{sp:.2f}", "change": f"{random.uniform(-1.2, 1.2):.2f}%"},
            {"name": "GOLD", "price": f"{gold:.2f}", "change": f"{random.uniform(-0.8, 0.8):.2f}%"},
            {"name": "BRENT", "price": f"{brent:.2f}", "change": f"{random.uniform(-2.0, 2.0):.2f}%"}
        ]

        # B. NEWS FEEDS (Using Public RSS)
        data['business'] = parse_feed("http://feeds.bbci.co.uk/news/business/rss.xml")
        data['sports'] = parse_feed("http://feeds.bbci.co.uk/sport/rss.xml")
        data['culture'] = parse_feed("https://www.theguardian.com/culture/rss")
        data['global'] = parse_feed("http://feeds.bbci.co.uk/news/world/rss.xml")

        # C. HISTORY FACT
        try:
            r = await client.get(f"https://history.muffinlabs.com/date/{datetime.now().month}/{datetime.now().day}", timeout=3.0)
            fact = random.choice(r.json()['data']['Events'])
            data['history'] = {"year": fact['year'], "text": fact['text']}
        except:
            data['history'] = {"year": "2026", "text": "Resinen Systems operational."}

        # D. JOKE
        try:
            r = await client.get("https://official-joke-api.appspot.com/random_joke", timeout=2.0)
            data['joke'] = r.json()
        except: 
            data['joke'] = {"setup": "Loading...", "punchline": "..."}

        return data

# --- 6. ZEN ---
async def get_zen_wisdom():
    quotes = ["The obstacle is the path.", "Act without expectation.", "Stillness speaks.", "Nature does not hurry.", "Be water, my friend."]
    return {"text": random.choice(quotes)}