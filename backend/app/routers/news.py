from fastapi import APIRouter
from ..services import (
    get_planetary_state, get_visual_feeds, get_zen_wisdom,
    get_audio_config, get_system_status, get_new_feeds
)

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/planetary")
def planetary(): return get_planetary_state()

@router.get("/visuals")
async def get_visuals(): return await get_visual_feeds()

@router.get("/zen")
async def zen(): return await get_zen_wisdom()

@router.get("/feeds")
async def feeds(): return await get_new_feeds()

@router.get("/audio")
def audio(): return get_audio_config()

@router.get("/system")
async def system(): return await get_system_status()