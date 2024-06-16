from pydantic import BaseModel

class MangaInfo(BaseModel):
    slug: str
    response: dict
    
class MangaSearch(BaseModel):
    text: str
    response: dict

class MangaQueryPayload(BaseModel):
    query: str
    variables: dict