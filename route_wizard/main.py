from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from pathlib import Path
from .data_manager import Router
from .data_manager import RoutingData
from .make_plots import *


app = FastAPI()

data_path:Path = Path(__file__).parent / "data_manager/data"
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
##  Data management routes
##
############

@app.get("/load-data/{dataset_id}")
def load_data(dataset_id: str):
    with open(data_path / f"test_{dataset_id}.csv", "r") as file:
        data:str = file.read()
        return {'data': data}


class DataObject(BaseModel):
    job_data:str
    teams:int
    employees:int
    step:int

@app.post("/submit-data")
def submit_data(data: DataObject):
    rd = RoutingData(data.job_data)
    min_employees:int = max(-(int(rd.df['budget'].sum()) // -375) + 1, 2)
    min_teams:int = max(-(min_employees // -4), 1)
    if data.step == 1:
        plot = scatter_locations(rd.df)
        return {"data": plot, "min_employees": min_employees, "min_teams": min_teams}
    else:
        if data.teams < min_teams or data.employees < min_employees:
            return {"data": "didn't enter minimum number of employees!",
                    "min_employees": min_employees, "min_teams": min_teams}

        router = Router(data.teams, data.employees, rd)
        router.solve()

        plot = plot_route(router.df, rd.df)
        plot2 = labor_percentage(router.df)
        table_template = templates.get_template('data_table.html').render({"df": router.df})

        return {"data": plot, 'labor_plot': plot2, "table": table_template}

