import httpx

from app.api.manga.schemas import MangaQueryPayload, MangaInfo, MangaSearch

URL = "https://api.senkuro.com/graphql"
HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
}


async def fetch(payload: str):
    async with httpx.AsyncClient(headers=HEADERS) as client:
        response = await client.post(url=URL, json=payload.dict())
        response.raise_for_status()
        return response.json()


async def title_info(slug: str):
    query = 'query($slug: String!) { manga(slug: $slug) { id slug localizations { lang description { __typename ... on TiptapNodeNestedBlock { content { ... on TiptapNodeText { text } } } } } titles { lang content } alternativeNames { content } chapters status translitionStatus branches { id lang chapters } genres { id titles { content } } tags { id titles { content } } cover { id blurhash original { url } } } }'
    variables={'slug': slug}
    return MangaInfo(slug=slug, response=await fetch(MangaQueryPayload(query=query, variables=variables)))


async def title_search(text: str):
    query = 'query searchTachiyomiManga($query: String) { mangaTachiyomiSearch(query: $query) { mangas { id slug originalName { lang content } titles { lang content } alternativeNames { lang content } cover { original { url } } } } }'
    variables={'query': text}
    return MangaSearch(text=text, response=await fetch(MangaQueryPayload(query=query, variables=variables)))


async def title_chapters(slug: str):
    # async with httpx.AsyncClient() as client:
    #     response = await client.get(f'https://api.mangadex.org/title/{title}')
    #     return response.json()
    pass


async def title_images(slug: str):
    # async with httpx.AsyncClient() as client:
    #     response = await client.get(f'https://api.mangadex.org/title/{title}')
    #     return response.json()
    pass