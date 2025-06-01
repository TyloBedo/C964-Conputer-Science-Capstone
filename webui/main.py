from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path

app_path:Path = Path(__file__).parent

data_path:Path = Path(__file__).parent.parent / "data"

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

@app.get("/load-data/{dataset_id}")
def load_data(dataset_id: str):
    print("yes")
    with open(data_path / f"test_{dataset_id}.csv", "r") as file:
        data:str = file.read()
        return {'data': data}



class DataObject(BaseModel):
    data:str
@app.post("/submit-data")
def submit_data(data: DataObject):
    print(data)
    return {"data": "okay"}


