import asyncio
import logging
from typing import List
import httpx

from app.api.manga.schemas import MangaInfo, MangaSearch, MangaChapters, MangaImages

URL = "https://api.senkuro.com/graphql"
HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("senkuro_handler")

async def fetch(payload: dict) -> dict:
    retry_count = 0
    max_retries = 10

    while retry_count < max_retries:
        async with httpx.AsyncClient(headers=HEADERS) as client:
            try:
                response = await client.post(url=URL, json=payload)
                response.raise_for_status()
                return response.json()

            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:
                    retry_count += 1
                    await asyncio.sleep(0.5)
                else:
                    logger.error(f"HTTP error: {e}")
                    raise e
            except Exception as e:
                logger.error(f"An error occurred: {e}")
                raise e

    raise Exception("Max retries reached")

async def title_info(slug: str) -> MangaInfo:
    query = '''
        query($slug: String!) { 
            manga(slug: $slug) { 
                id slug localizations { lang description { __typename ... on TiptapNodeNestedBlock { content { ... on TiptapNodeText { text } } } } }
                titles { lang content } 
                alternativeNames { content } 
                chapters status translitionStatus 
                branches { id lang chapters } 
                genres { id titles { content } } 
                tags { id titles { content } } 
                cover { id blurhash original { url } } 
            } 
        }
    '''
    variables = {'slug': slug}
    
    response = await fetch({'query': query, 'variables': variables})
    if response:
        data = response.get('data', {}).get('manga', {})
        return MangaInfo(
            id=data['id'],
            slug=data['slug'],
            description=" ".join(
                inner_content.get('text', '').replace('\\', '').replace('"', '\'')
                for content in next(
                    (loc for loc in response.get('data', {}).get('manga', {}).get('localizations', []) if loc.get('lang') == 'RU'),
                    {'description': []}
                ).get('description', [])
                for inner_content in content.get('content', [])
            ),
            title_name=next((item['content'] for item in data.get('titles', []) if item.get('lang') == 'RU'), None),
            alternativeNames=", ".join(item['content'] for item in data.get('alternativeNames', [])),
            chapters=data['chapters'],
            status=data['status'],
            translitionStatus=data['translitionStatus'],
            branches=max(data['branches'], key=lambda x: x['chapters'])['id'],
            genres=", ".join(item['titles'][0]['content'] for item in data.get('genres', [])),
            tags=", ".join(item['titles'][0]['content'] for item in data.get('tags', [])),
            cover=data.get('cover', {}).get('original', {}).get('url', '')
        )

async def title_search(text: str) -> List[MangaSearch]:
    query = '''
        query searchTachiyomiManga($query: String) { 
            mangaTachiyomiSearch(query: $query) { 
                mangas { id slug originalName { lang content } titles { lang content } alternativeNames { lang content } cover { original { url } } } 
            } 
        }
    '''
    variables = {'query': text}
    response = await fetch({'query': query, 'variables': variables})
    
    mangas_list = []
    if response:
        for manga in response['data']['mangaTachiyomiSearch']['mangas']:
            transformed_manga = MangaSearch(
                id=manga['id'],
                slug=manga['slug'],
                originalName=manga.get('originalName', {}).get('content', '').replace('"', '\''),
                titles=next((title['content'].replace('"', '\'') for title in manga.get('titles', []) if title['lang'] == 'RU'), None),
                alternativeNames=", ".join(name['content'].replace('"', '\'') for name in manga.get('alternativeNames', [])),
                cover=manga.get('cover', {}).get('original', {}).get('url')
            )
            mangas_list.append(transformed_manga.model_dump())
        
    return mangas_list

async def title_chapters(data: dict) -> List[MangaChapters]:
    query = '''
        query($branchId: ID!, $after: String, $first: Int) { 
            mangaChapters(branchId: $branchId, after: $after, first: $first) { 
                pageInfo { endCursor hasNextPage } 
                edges { node { slug id name number volume } } 
            } 
        }
    '''
    variables = {'branchId': data['branches'], 'after': None, 'first': 100}
    chapters_list = []
    has_next_page = True
    
    while has_next_page:
        response = await fetch({'query': query, 'variables': variables})
        if response:
            page_info = response['data']['mangaChapters']['pageInfo']
            has_next_page = page_info['hasNextPage']
            variables['after'] = page_info['endCursor']
            
            for manga in response['data']['mangaChapters']['edges']:
                chapters = MangaChapters(
                    id=manga['node']['id'],
                    name=manga['node']['name'],
                    number=manga['node']['number'],
                    slug=manga['node']['slug'],
                    volume=manga['node']['volume'],
                )
                chapters_list.append(chapters.model_dump())
                
    return chapters_list

async def title_images(mangaId: str, chapter_id: str):   
    query = '''
        query fetchTachiyomiChapterPages($mangaId: ID!, $chapterId: ID!) { 
            mangaTachiyomiChapterPages(mangaId: $mangaId, chapterId: $chapterId) { pages { url } } 
        }
    '''
    variables = {'mangaId': mangaId, 'chapterId': chapter_id}
    
    response = await fetch({'query': query, 'variables': variables})
    
    images = [image.get('url', '') for image in response.get('data', {}).get('mangaTachiyomiChapterPages', {}).get('pages', [])]
    return MangaImages(links=images)
