# app/api/manga/routers.py
import json
from fastapi import APIRouter, HTTPException

from app.utils.redis import redis_client
from .hendlers.senkuro_handler import title_info, title_search, title_chapters, title_images
# from .remanga_handler import remanga_get_title, remanga_searche, remanga_get_chapters

router = APIRouter()

site_handlers = {
    "senkuro": {
        "title_info": title_info,
        "title_search": title_search,
        "title_chapters": title_chapters,
        "title_images": title_images,
    },
    # "remanga": {
    #     "get_title": remanga_get_title,
    #     "search": remanga_searche,
    #     "get_chapters": remanga_get_chapters,
    # },
}

@router.get("/{site}/title/{slug}")
async def title_info(site: str, slug: str):
    cached_value = redis_client.get(slug)
    if cached_value:
        return json.loads(cached_value)
    
    if site in site_handlers:
        result = await site_handlers[site]["title_info"](slug)
        redis_client.set(slug, result.json(), ex=300)  # Кэширование на 5 минут
        return result
    
    raise HTTPException(status_code=404, detail="Site not found")

@router.get("/{site}/search/")
async def search(site: str, text: str):
    cached_value = redis_client.get(text)
    if cached_value:
        return json.loads(cached_value)
    
    if site in site_handlers:
        result = await site_handlers[site]["title_search"](text)
        redis_client.set(text, result.json(), ex=300)  # Кэширование на 5 минут
        return result
    
    raise HTTPException(status_code=404, detail="Site not found")

# @router.get("/{site}/chapters/{slug}")
# async def get_chapters(site: str, slug: str):
#     if site in site_handlers:
#         return site_handlers[site]["get_chapters"](slug)
#     raise HTTPException(status_code=404, detail="Site not found")

# Ensure the router is registered in the FastAPI application in main.py