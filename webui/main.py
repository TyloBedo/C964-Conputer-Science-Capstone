from fastapi import FastAPI
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path

app_path:Path = Path(__file__).parent

app = FastAPI()

app.mount("/static", StaticFiles(directory=app_path / "static"), name="static")
templates = Jinja2Templates(directory=app_path / "templates")

@app.get("/", name="index", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(
        request=request, name="index.html"
    )

@app.get("/about", name="about", response_class=HTMLResponse)
def about(request: Request):
    return templates.TemplateResponse(
        request=request, name="about.html"
    )


@app.get("/documentation", name="documentation", response_class=HTMLResponse)
def documentation(request: Request):
    return templates.TemplateResponse(
        request=request, name="documentation.html"
    )

['index', 'doc', 'about' ]