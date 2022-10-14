from os import path

from fastapi import APIRouter, Request
from fastapi.responses import Response
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory=path.abspath(path.join(path.dirname(__file__), "..", "..", "templates")))
general_pages_router = APIRouter()


@general_pages_router.get("/")
async def home(request: Request) -> Response:
    return templates.TemplateResponse("general_pages/homepage.html", context={"request": request})


@general_pages_router.get("/upload")
async def upload(request: Request) -> Response:
    return templates.TemplateResponse("general_pages/upload.html", context={"request": request, "result": False})
