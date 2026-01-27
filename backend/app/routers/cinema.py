# backend/app/routers/cinema.py
from fastapi import APIRouter

router = APIRouter(prefix="/cinema", tags=["cinema"])

# --- THE CURATED CATALOG (Updated for Playlists) ---
CATALOG = {
    "hero": {
        "id": "PLztAHXmlMZFS9ZN7GTlZ2UOB2JmxICdt8", # The Big Bang Theory Playlist
        "type": "playlist",
        "title": "Vogue Beauty Secrets",
        "desc": "Great Skincare Routines with Amazing Tips",
        "tags": ["Skincare", "Beauty", "Makeup"]
    },
    "categories": [
        {
            "title": "TV Shows & Series",
            "videos": [
                {
                    "id": "PLztAHXmlMZFS9ZN7GTlZ2UOB2JmxICdt8", # User Provided
                    "type": "playlist",
                    "title": "Vogue Beauty Secrets", 
                    "img": "https://img.youtube.com/vi/WBb3fojgW0Q/hqdefault.jpg" # Using Intro thumbnail
                },
                {
                    "id": "PL59187CC33D0F950A", 
                    "type": "playlist",
                    "title": "The Office (US) - Best Of", 
                    "img": "https://img.youtube.com/vi/gO8N3L_aERg/hqdefault.jpg"
                },
                {
                    "id": "PL72C62342291D5DAE", 
                    "type": "playlist",
                    "title": "Breaking Bad - Iconic Scenes", 
                    "img": "https://img.youtube.com/vi/HhesaQXLuRY/hqdefault.jpg"
                }
            ]
        },
        {
            "title": "Focus & Ambience",
            "videos": [
                {
                    "id": "PL6NdkXsPL07KN01gH2vucNpHrYNYMSFzp", 
                    "type": "playlist",
                    "title": "Lofi Girl - Radio", 
                    "img": "https://img.youtube.com/vi/jfKfPfyJRdk/maxresdefault.jpg"
                },
                {
                    "id": "PLzQjZPtdeFYJ5a8V9T7q_Vp07I41z1s-w", 
                    "type": "playlist",
                    "title": "Blade Runner Soundscapes", 
                    "img": "https://img.youtube.com/vi/wN9b9yZPHJA/maxresdefault.jpg"
                }
            ]
        },
        {
            "title": "Intellectual Downloads",
            "videos": [
                {
                    "id": "PLZHQObOWTQDPD3MizzM2xVFitgF8hE_ab", 
                    "type": "playlist",
                    "title": "3Blue1Brown - Math Essence", 
                    "img": "https://img.youtube.com/vi/zlwQERpksnw/maxresdefault.jpg"
                },
                {
                    "id": "PLFE30746974776587", 
                    "type": "playlist",
                    "title": "Kurzgesagt - Universe", 
                    "img": "https://img.youtube.com/vi/h6fcK_fRYaI/maxresdefault.jpg"
                }
            ]
        }
    ]
}

@router.get("/catalog")
def get_catalog():
    return CATALOG