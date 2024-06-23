import json
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from app.utils.redis import redis_client
from .handlers.senkuro_handler import title_info, title_search, title_chapters, title_images
from app.api.manga.schemas import MangaInfo, MangaSearch, MangaChapters, MangaImages

router = APIRouter()

site_handlers = {
    "senkuro": {
        "title_info": title_info,
        "title_search": title_search,
        "title_chapters": title_chapters,
        "title_images": title_images,
    },
}


@router.get("/api/manga/{site}/title/{slug}", response_model=MangaInfo)
@router.get("/api/manga/{site}/title/{slug}/{any}", response_model=MangaInfo)
@router.get("/manga/{slug}", response_model=MangaInfo)
@router.get("/manga/{slug}/{any}", response_model=MangaInfo)
@router.get("/api/manga/{slug}", response_model=MangaInfo)
@router.get("/api/manga/{slug}/{any}", response_model=MangaInfo)
async def title_info(slug: str, site: str = 'senkuro'):
    cached_value = redis_client.get(f"site:{site}, slug:{slug}")
    if cached_value:
        return JSONResponse(content=json.loads(cached_value))
    
    if site in site_handlers:
        result = (await site_handlers[site]["title_info"](slug)).dict()
        redis_client.set(f"site:{site}, slug:{slug}", json.dumps(result), ex=43200)
        return JSONResponse(content=result)

    raise HTTPException(status_code=404, detail="Site not found")

@router.get("/manga/{site}/search/", response_model=MangaSearch)
async def search_title(site: str, text: str):
    cached_value = redis_client.get(f"site:{site}, text:{text}")
    if cached_value:
        return JSONResponse(content=json.loads(cached_value))
    
    if site in site_handlers:
        result = await site_handlers[site]["title_search"](text)
        redis_client.set(f"site:{site}, text:{text}", json.dumps(result), ex=43200)
        return JSONResponse(content=jsonable_encoder(result))
    
    raise HTTPException(status_code=404, detail="Site not found")

@router.get("/{site}/chapters/{slug}", response_model=MangaChapters)
async def get_chapters(site: str, slug: str):
    cached_value = redis_client.get(f"site:{site}, slug:{slug}")
    if cached_value:
        data = json.loads(cached_value)
        
    else:
        if site in site_handlers:
            data = (await site_handlers[site]["title_info"](slug)).dict()
            redis_client.set(f"site:{site}, slug:{slug}", json.dumps(data), ex=43200)
        else:
            raise HTTPException(status_code=404, detail="Site not found")
    
    if site in site_handlers:
        result = await site_handlers[site]["title_chapters"](data)
        return JSONResponse(content=jsonable_encoder(result))
    
    raise HTTPException(status_code=404, detail="Site not found")


@router.get("/api/manga/{site}/{slug}/{chapterId}", response_model=MangaImages)
@router.get("/api/manga/{site}/images/{slug}/{chapterId}", response_model=MangaImages)
async def get_images(site: str, slug: str, chapter_id: str):
    # Проверка кэша для изображения
    cached_value = redis_client.get(f"site:{site}, chapter_id:{chapter_id}")
    if cached_value:
        return JSONResponse(content=json.loads(cached_value))
    
    # Проверка кэша для заголовка
    cached_value = redis_client.get(f"site:{site}, slug:{slug}")
    if cached_value:
        data = json.loads(cached_value)
    
    # Проверка существования обработчика для указанного сайта
    if site in site_handlers:
        data = (await site_handlers[site]["title_info"](slug)).dict()
        redis_client.set(f"site:{site}, slug:{slug}", json.dumps(data), ex=43200)
    else:
        raise HTTPException(status_code=404, detail="Site not found")

    # Проверка существования обработчика для указанного сайта
    if site in site_handlers:
        images_data = (await site_handlers[site]["title_images"](data.get('id'), chapter_id)).dict()
        redis_client.set(f"site:{site}, chapter_id:{chapter_id}", json.dumps(images_data), ex=43200)
        return JSONResponse(content=images_data)
    
    raise HTTPException(status_code=404, detail="Site not found")