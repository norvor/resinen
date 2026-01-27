# backend/app/services.py
import httpx
import random
import xml.etree.ElementTree as ET
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
    return [{"name": "NET", "status": "operational"}, {"name": "CORE", "status": "operational"}, {"name": "UPLINK", "status": "operational"}]

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

async def get_met_art(client):
    """Fetches a random masterpiece from The MET (New York)"""
    try:
        # 1. Search for paintings with images (Classic & Landscape focus)
        # We assume a static search to get valid IDs, or we could cache this.
        # "Oil on canvas" usually guarantees a painting.
        search_url = "https://collectionapi.metmuseum.org/public/collection/v1/search?hasImages=true&q=oil%20on%20canvas&medium=Paintings"
        
        resp = await client.get(search_url)
        data = resp.json()
        
        if data['total'] > 0:
            # Pick a random object ID
            obj_id = random.choice(data['objectIDs'][:100]) # Limit to top 100 for relevance
            
            # 2. Get Object Details
            obj_resp = await client.get(f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{obj_id}")
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
    """Fetches a random masterpiece from Art Institute of Chicago"""
    try:
        # AIC allows random page fetching, which is faster/easier
        # Page 1-100 contains the most popular/curated works
        page = random.randint(1, 50)
        url = f"https://api.artic.edu/api/v1/artworks?page={page}&limit=1&fields=id,title,image_id,artist_display"
        
        resp = await client.get(url)
        data = resp.json()
        artwork = data['data'][0]
        
        if artwork['image_id']:
            # Construct IIIF Image URL
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

# --- 3. VISUALS (World, Nature, Food, Animals) ---
async def get_visual_feeds():
    async with httpx.AsyncClient() as client:
        results = {}
        
        # A. WORLD VIEW (Cities & Wonders) - Replaces APOD
        # High-res Unsplash IDs for specific locations
        

        art_data = None
        if art_source == "aic":
            results['art_data'] = await get_aic_art(client)
        
        # Fallback to MET if AIC fails or if MET is selected
        if not art_data: 
            results['art_data'] = await get_met_art(client)
        
        # Ultimate Fallback
        if not art_data:
            results['art_data'] = {
                "url": "https://images.unsplash.com/photo-1549490349-8643362247b5",
                "title": "Connection Lost",
                "artist": "System",
                "source": "OFFLINE"
            }

        # B. ANIMALS (Cat/Dog/Fox)
        try:
            choice = random.choice(['fox', 'dog', 'cat'])
            if choice == 'fox':
                r = await client.get("https://randomfox.ca/floof/", timeout=2.0)
                results['animal'] = {"type": "FOX", "url": r.json()['image']}
            elif choice == 'dog':
                r = await client.get("https://dog.ceo/api/breeds/image/random", timeout=2.0)
                results['animal'] = {"type": "DOG", "url": r.json()['message']}
            else:
                r = await client.get("https://api.thecatapi.com/v1/images/search", timeout=2.0)
                results['animal'] = {"type": "CAT", "url": r.json()[0]['url']}
        except: 
            results['animal'] = {"type": "OFFLINE", "url": ""}

        # C. NATURE (Pure Landscapes for bottom right)
        ids = ["1472214103451-9374bd1c798e", "1441974231531-c6227db76b6e", "1507525428034-b723cf961d3e"]
        results['nature'] = f"https://images.unsplash.com/photo-{random.choice(ids)}?q=80&w=800&auto=format&fit=crop"
        
        # D. FOODISH

        # 1. GET FOOD (TheMealDB)
        # This is the "Better API" - High res, real recipes.
        food_data = None
        try:
            resp = await client.get("https://www.themealdb.com/api/json/v1/1/random.php")
            data = resp.json()
            meal = data['meals'][0]
            results['food'] = meal['strMealThumb'] # High Res Image URL
        except:
            results['food'] = "https://images.unsplash.com/photo-1546069901-ba9599a7e63c" # Fallback

        return results

# --- 4. DATA FEEDS (Sports, History, Uplifting, Markets, Jokes) ---
async def get_new_feeds():
    headers = { "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)" }
    async with httpx.AsyncClient(headers=headers, follow_redirects=True) as client:
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

        # B. GLOBAL SPORTS (BBC)
        try:
            r = await client.get("http://feeds.bbci.co.uk/sport/rss.xml", timeout=4.0)
            root = ET.fromstring(r.content)
            items = []
            for item in root.findall(".//item")[:4]:
                items.append({"title": item.find("title").text, "link": item.find("link").text})
            data['sports'] = items
        except:
            data['sports'] = [{"title": "Sports Feed Offline", "link": "#"}]

        # C. HISTORY FACT
        try:
            month = datetime.now().month
            day = datetime.now().day
            r = await client.get(f"https://history.muffinlabs.com/date/{month}/{day}", timeout=3.0)
            json_data = r.json()
            fact = random.choice(json_data['data']['Events'])
            data['history'] = {"year": fact['year'], "text": fact['text']}
        except:
            data['history'] = {"year": "2024", "text": "The Resinen Dashboard v2.0 was successfully deployed."}

        # D. UPLIFTING (Good News Network)
        try:
            r = await client.get("https://www.goodnewsnetwork.org/feed/", timeout=4.0)
            root = ET.fromstring(r.content)
            items = []
            for item in root.findall(".//item")[:2]:
                items.append({"title": item.find("title").text, "url": item.find("link").text})
            data['uplifting'] = items
        except: 
            data['uplifting'] = [{"title": "Scientists discover new coral reef", "url": "#"}]

        # E. JOKE
        try:
            r = await client.get("https://official-joke-api.appspot.com/random_joke", timeout=2.0)
            data['joke'] = r.json()
        except: data['joke'] = {"setup": "Loading...", "punchline": "..."}

        return data

# --- 5. ZEN ---
async def get_zen_wisdom():
    quotes = ["The obstacle is the path.", "Act without expectation.", "Stillness speaks.", "Nature does not hurry.", "Be water, my friend."]
    return {"text": random.choice(quotes)}