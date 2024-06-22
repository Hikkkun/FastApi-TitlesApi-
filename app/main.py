from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates

from app.api.manga.routers import router as manga_router
from app.api.ranobe.routers import router as ranobe_router

app = FastAPI()
templates = Jinja2Templates(directory="templates")

app.include_router(manga_router, prefix="/api", tags={"manga"})
app.include_router(ranobe_router, prefix="/api", tags={"manga"})

@app.get("/")
def read_form(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run('app.main:app', host="127.0.0.1", port=8000, reload=True)