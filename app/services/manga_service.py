import httpx
import json
from app.api.manga.schemas import MangaQueryPayload, MangaInfo
from app.core.config import settings

URL = "https://api.senkuro.com/graphql"
HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
}

async def get_manga_info(slug: str, redis) -> MangaInfo:
    cached_data = await redis.get(slug)

    if cached_data:
        try:
            data = json.loads(cached_data)
            return MangaInfo(**data)
        except json.JSONDecodeError:
            pass
    
    query = '''
        query($slug: String!) {
        manga(slug: $slug) {
            id
            slug
            localizations {
            lang
            description {
                __typename
                ... on TiptapNodeNestedBlock {
                content {
                    ... on TiptapNodeText {
                    text
                    }
                }
                }
            }
            }
            titles { lang content }
            alternativeNames { content }
            chapters
            status
            translitionStatus
            branches { id lang chapters }
            genres { id titles { content } }
            tags { id titles { content } }
            cover { id blurhash original { url } }
        }
    }'''
            
    payload = MangaQueryPayload(query=query, variables={'slug': slug})

    async with httpx.AsyncClient(headers=HEADERS) as client:
        response = await client.post(URL, json=payload.dict())
        response.raise_for_status()

    data = MangaInfo(slug=slug, response=response.json())
    await redis.set(slug, data.json(), ex=3600) 

    return data