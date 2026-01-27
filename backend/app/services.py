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

# --- 3. VISUALS (World, Nature, Food, Animals) ---
async def get_visual_feeds():
    async with httpx.AsyncClient() as client:
        results = {}
        
        # A. WORLD VIEW (Cities & Wonders) - Replaces APOD
        # High-res Unsplash IDs for specific locations
        

        WORLD_WONDERS = [
    # --- ASIA ---
            {"title": "Tokyo, Japan", "url": "https://images.unsplash.com/photo-1503899036084-c55cdd92da26?auto=format&fit=crop&w=800&q=80"},
            {"title": "Kyoto, Japan", "url": "https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?auto=format&fit=crop&w=800&q=80"},
            {"title": "Mount Fuji", "url": "https://images.unsplash.com/photo-1490806843957-31f4c9a91c65?auto=format&fit=crop&w=800&q=80"},
            {"title": "Great Wall of China", "url": "https://images.unsplash.com/photo-1508804185872-d7badad00f7d?auto=format&fit=crop&w=800&q=80"},
            {"title": "Hong Kong Night", "url": "https://images.unsplash.com/photo-1506318137071-a8bcbf90d346?auto=format&fit=crop&w=800&q=80"},
            {"title": "Seoul, South Korea", "url": "https://images.unsplash.com/photo-1517154421773-052f83c4217c?auto=format&fit=crop&w=800&q=80"},
            {"title": "Bali, Indonesia", "url": "https://images.unsplash.com/photo-1537996194471-e657df975ab4?auto=format&fit=crop&w=800&q=80"},
            {"title": "Ha Long Bay, Vietnam", "url": "https://images.unsplash.com/photo-1559592413-7cec4d0cae2b?auto=format&fit=crop&w=800&q=80"},
            {"title": "Taj Mahal, India", "url": "https://images.unsplash.com/photo-1564507592333-c60657eea523?auto=format&fit=crop&w=800&q=80"},
            {"title": "Petra, Jordan", "url": "https://images.unsplash.com/photo-1579606622384-8253119191d9?auto=format&fit=crop&w=800&q=80"},
            {"title": "Singapore Supertrees", "url": "https://images.unsplash.com/photo-1525625293386-3f8f99389edd?auto=format&fit=crop&w=800&q=80"},
            {"title": "Jaipur, India", "url": "https://images.unsplash.com/photo-1477587458883-47145ed94245?auto=format&fit=crop&w=800&q=80"},

            # --- EUROPE ---
            {"title": "Paris, France", "url": "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?auto=format&fit=crop&w=800&q=80"},
            {"title": "London, UK", "url": "https://images.unsplash.com/photo-1513635269975-59663e0ac1ad?auto=format&fit=crop&w=800&q=80"},
            {"title": "Swiss Alps", "url": "https://images.unsplash.com/photo-1531366936337-7c912a4589a7?auto=format&fit=crop&w=800&q=80"},
            {"title": "Santorini, Greece", "url": "https://images.unsplash.com/photo-1613395877344-13d4c79e4284?auto=format&fit=crop&w=800&q=80"},
            {"title": "Rome, Italy", "url": "https://images.unsplash.com/photo-1552832230-c0197dd311b5?auto=format&fit=crop&w=800&q=80"},
            {"title": "Venice, Italy", "url": "https://images.unsplash.com/photo-1514890547357-a9ee288728e0?auto=format&fit=crop&w=800&q=80"},
            {"title": "Amalfi Coast", "url": "https://images.unsplash.com/photo-1533105079780-92b9be482077?auto=format&fit=crop&w=800&q=80"},
            {"title": "Iceland Aurora", "url": "https://images.unsplash.com/photo-1476610182048-b716b8518aae?auto=format&fit=crop&w=800&q=80"},
            {"title": "Amsterdam Canals", "url": "https://images.unsplash.com/photo-1512470876302-972faa2ab9af?auto=format&fit=crop&w=800&q=80"},
            {"title": "Barcelona, Spain", "url": "https://images.unsplash.com/photo-1583422409516-2895a77efded?auto=format&fit=crop&w=800&q=80"},
            {"title": "Prague, Czechia", "url": "https://images.unsplash.com/photo-1519677100203-a0e668c92439?auto=format&fit=crop&w=800&q=80"},
            {"title": "Neuschwanstein Castle", "url": "https://images.unsplash.com/photo-1543783207-c1056d231478?auto=format&fit=crop&w=800&q=80"},
            {"title": "Hallstatt, Austria", "url": "https://images.unsplash.com/photo-1506355683710-bd071c0a5828?auto=format&fit=crop&w=800&q=80"},
            {"title": "Dubrovnik, Croatia", "url": "https://images.unsplash.com/photo-1555990538-1a525e838634?auto=format&fit=crop&w=800&q=80"},
            {"title": "Lofoten, Norway", "url": "https://images.unsplash.com/photo-1506703719100-a0f3a48c0f86?auto=format&fit=crop&w=800&q=80"},

            # --- AMERICAS ---
            {"title": "New York City", "url": "https://images.unsplash.com/photo-1496442226666-8d4d0e62e6e9?auto=format&fit=crop&w=800&q=80"},
            {"title": "San Francisco", "url": "https://images.unsplash.com/photo-1501594907352-04cda38ebc29?auto=format&fit=crop&w=800&q=80"},
            {"title": "Grand Canyon", "url": "https://images.unsplash.com/photo-1474044159687-195d0f127146?auto=format&fit=crop&w=800&q=80"},
            {"title": "Yosemite National Park", "url": "https://images.unsplash.com/photo-1532274402911-5a369e4c4bb5?auto=format&fit=crop&w=800&q=80"},
            {"title": "Banff, Canada", "url": "https://images.unsplash.com/photo-1561134643-63305d28ef33?auto=format&fit=crop&w=800&q=80"},
            {"title": "Machu Picchu", "url": "https://images.unsplash.com/photo-1526392060635-9d6019884377?auto=format&fit=crop&w=800&q=80"},
            {"title": "Rio de Janeiro", "url": "https://images.unsplash.com/photo-1483729558449-99ef09a8c325?auto=format&fit=crop&w=800&q=80"},
            {"title": "Patagonia", "url": "https://images.unsplash.com/photo-1518182170546-0766ce6fec93?auto=format&fit=crop&w=800&q=80"},
            {"title": "Havana, Cuba", "url": "https://images.unsplash.com/photo-1503923053744-b04071536750?auto=format&fit=crop&w=800&q=80"},
            {"title": "Mexico City", "url": "https://images.unsplash.com/photo-1518105779142-d975f22f1b0a?auto=format&fit=crop&w=800&q=80"},
            {"title": "Tulum, Mexico", "url": "https://images.unsplash.com/photo-1504730635926-28109ae43b23?auto=format&fit=crop&w=800&q=80"},

            # --- AFRICA & MIDDLE EAST ---
            {"title": "Dubai, UAE", "url": "https://images.unsplash.com/photo-1512453979798-5ea904ac6605?auto=format&fit=crop&w=800&q=80"},
            {"title": "Pyramids of Giza", "url": "https://images.unsplash.com/photo-1539650116455-251d9a05a218?auto=format&fit=crop&w=800&q=80"},
            {"title": "Cape Town", "url": "https://images.unsplash.com/photo-1580060839134-75a5edca2e99?auto=format&fit=crop&w=800&q=80"},
            {"title": "Sahara Desert", "url": "https://images.unsplash.com/photo-1509316975850-ff9c5deb0cd9?auto=format&fit=crop&w=800&q=80"},
            {"title": "Marrakech, Morocco", "url": "https://images.unsplash.com/photo-1597212720117-6d60527c9287?auto=format&fit=crop&w=800&q=80"},
            {"title": "Serengeti, Tanzania", "url": "https://images.unsplash.com/photo-1516426122078-c23e76319801?auto=format&fit=crop&w=800&q=80"},
            {"title": "Seychelles", "url": "https://images.unsplash.com/photo-1537551080512-fb7dd14fbf90?auto=format&fit=crop&w=800&q=80"},

            # --- OCEANIA ---
            {"title": "Sydney Opera House", "url": "https://images.unsplash.com/photo-1506973035872-a4ec16b8e8d9?auto=format&fit=crop&w=800&q=80"},
            {"title": "New Zealand", "url": "https://images.unsplash.com/photo-1469521669194-babb45f8a8d4?auto=format&fit=crop&w=800&q=80"},
            {"title": "Bora Bora", "url": "https://images.unsplash.com/photo-1589979481223-deb893043163?auto=format&fit=crop&w=800&q=80"}
        ]

        results['world'] = random.choice(WORLD_WONDERS)

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