# backend/app/routers/cinema.py
from fastapi import APIRouter

router = APIRouter(prefix="/cinema", tags=["cinema"])

# --- THE CURATED CATALOG ---
# You can replace these IDs with any YouTube Video ID
CATALOG = {
    "hero": {
        "id": "hYwxuQ85DCI", # Example: A cool space documentary or visual loop
        "title": "THE FUTURE OF HUMANITY",
        "desc": "An exploration of our species' trajectory into the cosmos and the digital realm.",
        "tags": ["Documentary", "Space", "4K"]
    },
    "categories": [
        {
            "title": "Deep Focus & Flow",
            "videos": [
                {"id": "jfKfPfyJRdk", "title": "Lofi Girl - beats to relax/study to", "img": "https://img.youtube.com/vi/jfKfPfyJRdk/maxresdefault.jpg"},
                {"id": "5qap5aO4i9A", "title": "Lofi Boy - Synthwave Radio", "img": "https://img.youtube.com/vi/5qap5aO4i9A/maxresdefault.jpg"},
                {"id": "wN9b9yZPHJA", "title": "Blade Runner Ambient", "img": "https://img.youtube.com/vi/wN9b9yZPHJA/maxresdefault.jpg"},
                {"id": "McMxxCs5t1w", "title": "Interstellar Main Theme - 1 Hour", "img": "https://img.youtube.com/vi/McMxxCs5t1w/maxresdefault.jpg"},
            ]
        },
        {
            "title": "Intellectual Downloads",
            "videos": [
                {"id": "zlwQERpksnw", "title": "The Map of Mathematics", "img": "https://img.youtube.com/vi/zlwQERpksnw/maxresdefault.jpg"},
                {"id": "0jHfBa0TRgg", "title": "The Essence of Calculus", "img": "https://img.youtube.com/vi/0jHfBa0TRgg/maxresdefault.jpg"},
                {"id": "F5fejhfq5uQ", "title": "The Riemann Hypothesis", "img": "https://img.youtube.com/vi/F5fejhfq5uQ/maxresdefault.jpg"},
                {"id": "aircAruvnKk", "title": "Neural Networks Explained", "img": "https://img.youtube.com/vi/aircAruvnKk/maxresdefault.jpg"},
            ]
        },
        {
            "title": "Visual Masterpieces",
            "videos": [
                {"id": "ysz5S6PUM-U", "title": "Foo Fighters - The Pretender", "img": "https://img.youtube.com/vi/ysz5S6PUM-U/maxresdefault.jpg"},
                {"id": "LXb3EKWsInQ", "title": "COSTA RICA IN 4K", "img": "https://img.youtube.com/vi/LXb3EKWsInQ/maxresdefault.jpg"},
                {"id": "tO01J-M3g0U", "title": "The World in HDR", "img": "https://img.youtube.com/vi/tO01J-M3g0U/maxresdefault.jpg"},
            ]
        }
    ]
}

@router.get("/catalog")
def get_catalog():
    return CATALOG