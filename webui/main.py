import base64
from io import BytesIO

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from pathlib import Path
from route_analyzer import RouteAnalyzer
from routing_data import RoutingData
from webui.make_plots import *




app = FastAPI()

data_path:Path = Path(__file__).parent.parent / "data"
app_path:Path = Path(__file__).parent


app.mount("/static", StaticFiles(directory=app_path / "static"), name="static")
templates = Jinja2Templates(directory=app_path / "templates")

############
##
##  navigation routes
##
############

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

############
##
##  Navigation routes end
##
############



############
##
##  Data management routes
##
############


@app.get("/load-data/{dataset_id}")
def load_data(dataset_id: str):
    print("yes")
    with open(data_path / f"test_{dataset_id}.csv", "r") as file:
        data:str = file.read()
        return {'data': data}


class DataObject(BaseModel):
    job_data:str
    teams:int
    employees:int

@app.post("/submit-data")
def submit_data(data: DataObject):
    rd = RoutingData(8, 26, data.job_data)
    plot = scatter_locations(rd.df)
    return {"data": plot}

@app.post("/submit-final")
def submit_data(data: DataObject):
    ra = RouteAnalyzer(data.teams,data.employees, data.job_data)
    plot = plot_route(ra.df, ra.rd.df)

    routes = [1,2,3]
    context = {"df":ra.df}

    table_template = templates.get_template('data_table.html').render(context)

    return {"data": plot, "table": table_template}

############
##
##  Data management routes end
##
############

