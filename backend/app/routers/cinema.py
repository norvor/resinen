from fastapi import APIRouter

router = APIRouter(prefix="/cinema", tags=["cinema"])

# --- THE CURATED CATALOG ---
CATALOG = {
    # HERO: A Masterpiece from your list (Mozart's Lacrimosa)
    "hero": {
        "id": "Rb0UmrCXxVA", 
        "type": "video",
        "title": "MOZART: LACRIMOSA",
        "desc": "A profound and hauntingly beautiful choral masterpiece from Mozart's Requiem.",
        "tags": ["Classical", "Mozart", "Choral"]
    },
    "categories": [
        # --- 1. CLASSICAL MASTERPIECES ---
        {
            "title": "Classical Masterpieces",
            "videos": [
                {"id": "Rb0UmrCXxVA", "type": "video", "title": "Mozart - Lacrimosa", "img": "https://img.youtube.com/vi/Rb0UmrCXxVA/hqdefault.jpg"},
                {"id": "uiTrB-zA7bc", "type": "video", "title": "Beethoven - Moonlight Sonata", "img": "https://img.youtube.com/vi/uiTrB-zA7bc/hqdefault.jpg"},
                {"id": "Jn09UdSb3aA", "type": "video", "title": "Tchaikovsky - Waltz of the Flowers", "img": "https://img.youtube.com/vi/Jn09UdSb3aA/hqdefault.jpg"},
                {"id": "W-fFHeTX70Q", "type": "video", "title": "Vivaldi - Spring", "img": "https://img.youtube.com/vi/W-fFHeTX70Q/hqdefault.jpg"},
                {"id": "qnYSx-SQXiI", "type": "video", "title": "Satie - Gymnopédie No.1", "img": "https://img.youtube.com/vi/qnYSx-SQXiI/hqdefault.jpg"},
                {"id": "DG87oy53_zM", "type": "video", "title": "Debussy - Clair de Lune", "img": "https://img.youtube.com/vi/DG87oy53_zM/hqdefault.jpg"},
                {"id": "i6D8B2wFJmw", "type": "video", "title": "Chopin - Nocturne op.9 No.2", "img": "https://img.youtube.com/vi/i6D8B2wFJmw/hqdefault.jpg"},
                {"id": "zPhICi6IZ_4", "type": "video", "title": "Bach - Cello Suite No. 1", "img": "https://img.youtube.com/vi/zPhICi6IZ_4/hqdefault.jpg"},
                {"id": "FoUMsBQmGPY", "type": "video", "title": "Tchaikovsky - Swan Lake", "img": "https://img.youtube.com/vi/FoUMsBQmGPY/hqdefault.jpg"},
                {"id": "2c62lHfcizA", "type": "video", "title": "Pachelbel - Canon in D", "img": "https://img.youtube.com/vi/2c62lHfcizA/hqdefault.jpg"}
            ]
        },
        # --- 2. CLASSICAL COLLECTIONS (Playlists) ---
        {
            "title": "Classical Collections",
            "videos": [
                # Extracted Playlist ID from your link: list=PLcGkkXtask_eI44NtdwwcJ2Zxh1miU9Qh
                {"id": "PLcGkkXtask_eI44NtdwwcJ2Zxh1miU9Qh", "type": "playlist", "title": "Dark Academia Classical", "img": "https://img.youtube.com/vi/_PlEGwqB2FM/hqdefault.jpg"},
                # Extracted Playlist ID from your link: list=PLcGkkXtask_e_o4Kou_SHaRIknQrmzWlw
                {"id": "PLcGkkXtask_e_o4Kou_SHaRIknQrmzWlw", "type": "playlist", "title": "Romantic Classical", "img": "https://img.youtube.com/vi/YkL1rTvxoF4/hqdefault.jpg"}
            ]
        },
        # --- 3. JAZZ LOUNGE ---
        {
            "title": "The Jazz Lounge",
            "videos": [
                {"id": "nv_2rz5BFDA", "type": "video", "title": "Coffee Shop Jazz", "img": "https://img.youtube.com/vi/nv_2rz5BFDA/hqdefault.jpg"},
                {"id": "CfPxlb8-ZQ0", "type": "video", "title": "Night Jazz Piano", "img": "https://img.youtube.com/vi/CfPxlb8-ZQ0/hqdefault.jpg"},
                {"id": "qzyl0f3mRG0", "type": "video", "title": "New York Jazz", "img": "https://img.youtube.com/vi/qzyl0f3mRG0/hqdefault.jpg"},
                {"id": "_sI_Ps7JSEk", "type": "video", "title": "Smooth Jazz Mix", "img": "https://img.youtube.com/vi/_sI_Ps7JSEk/hqdefault.jpg"},
                {"id": "-bBzIgIaPS4", "type": "video", "title": "Late Night Saxophone", "img": "https://img.youtube.com/vi/-bBzIgIaPS4/hqdefault.jpg"}
            ]
        },
        # --- 4. RELAX & CHILL ---
        {
            "title": "Relax & Chill",
            "videos": [
                {"id": "ZBHTd3WU2To", "type": "video", "title": "Relaxing Guitar", "img": "https://img.youtube.com/vi/ZBHTd3WU2To/hqdefault.jpg"},
                {"id": "f_FSWEg9Wgk", "type": "video", "title": "Forest Sounds", "img": "https://img.youtube.com/vi/f_FSWEg9Wgk/hqdefault.jpg"},
                {"id": "Ou8B8t12-8g", "type": "video", "title": "Peaceful Piano", "img": "https://img.youtube.com/vi/Ou8B8t12-8g/hqdefault.jpg"},
                {"id": "8wwD-Jnveso", "type": "video", "title": "Ambient Soundscape", "img": "https://img.youtube.com/vi/8wwD-Jnveso/hqdefault.jpg"},
                {"id": "OO2kPK5-qno", "type": "video", "title": "Deep Focus", "img": "https://img.youtube.com/vi/OO2kPK5-qno/hqdefault.jpg"},
                {"id": "sF80I-TQiW0", "type": "video", "title": "Spa & Healing", "img": "https://img.youtube.com/vi/sF80I-TQiW0/hqdefault.jpg"}
            ]
        }
    ]
}

@router.get("/catalog")
def get_catalog():
    return CATALOG