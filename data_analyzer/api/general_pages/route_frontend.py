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


@general_pages_router.get("/graph-qh")
async def graph_qh(request: Request, aggregate: str = "", step: int = 4, lower: str = "", upper: str = "") -> Response:
    return templates.TemplateResponse(
        "general_pages/graph.html",
        context={
            "request": request,
            "source": "qh",
            "aggregate": aggregate,
            "step": step,
            "lower": lower,
            "upper": upper,
        },
    )


@general_pages_router.get("/graph-d")
async def graph_h(request: Request, aggregate: str = "", step: int = 4, lower: str = "", upper: str = "") -> Response:
    return templates.TemplateResponse(
        "general_pages/graph.html",
        context={
            "request": request,
            "source": "d",
            "aggregate": aggregate,
            "step": step,
            "lower": lower,
            "upper": upper,
        },
    )
