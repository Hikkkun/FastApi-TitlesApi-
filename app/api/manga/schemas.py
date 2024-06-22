from typing import List, Optional
from pydantic import BaseModel

class MangaInfo(BaseModel):
    id: str
    slug: str
    description: Optional[str] = None
    title_name: str
    alternativeNames: Optional[str] = None
    chapters: int
    status: str
    translitionStatus: Optional[str] = None
    branches: str
    genres: Optional[str] = None
    tags: Optional[str] = None
    cover: Optional[str] = None

class MangaSearch(BaseModel):
    id: str
    slug: str
    originalName: Optional[str] = None
    titles: Optional[str] = None
    alternativeNames: Optional[str] = None
    cover: Optional[str] = None

class MangaChapters(BaseModel):
    id: str
    name: Optional[str] = None
    number: Optional[str] = None
    slug: Optional[str] = None
    volume: Optional[str] = None
    
    
class MangaImages(BaseModel):
    links: List[str]