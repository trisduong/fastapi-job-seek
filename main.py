from app.api.base import api_router
from app.db.base import Base
from app.db.session import engine
from fastapi import FastAPI
from fastapi.exceptions import HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")


@app.exception_handler(HTTPException)
async def exception_handler(request, exc):
    return templates.TemplateResponse(
        "general_pages/homepage.html", {"request": request, "msg": exc}
    )


app.include_router(api_router)
app.mount("/static", StaticFiles(directory="app/static"), name="static")
Base.metadata.create_all(bind=engine)
