import pytest
from fastapi.testclient import TestClient
from app.main import create_app
from app.api.manga.schemas import MangaInfo
from httpx import AsyncClient

app = create_app()
client = TestClient(app)

test_slug = "example-slug"
mock_response_data = {
    "data": {
        "manga": {
            "id": "1",
            "slug": test_slug,
            "localizations": [],
            "titles": [],
            "alternativeNames": [],
            "chapters": 0,
            "status": "ONGOING",
            "translitionStatus": "ONGOING",
            "branches": [],
            "genres": [],
            "tags": [],
            "cover": {"id": "1", "blurhash": "", "original": {"url": ""}}
        }
    }
}

@pytest.mark.asyncio
async def test_manga_info(monkeypatch):
    async def mock_post(*args, **kwargs):
        class MockResponse:
            def __init__(self, json_data):
                self._json = json_data

            async def json(self):
                return self._json

            def raise_for_status(self):
                pass

        return MockResponse(mock_response_data)

    monkeypatch.setattr(AsyncClient, "post", mock_post)

    response = await client.get(f"/api/manga/title/{test_slug}")
    assert response.status_code == 200
    data = response.json()
    assert data["response"] == mock_response_data["data"]
    assert data["slug"] == test_slug