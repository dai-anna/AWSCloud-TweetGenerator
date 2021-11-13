from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

# app.mount("/static", StaticFiles(directory="static"), name="static")


templates = Jinja2Templates(directory="application/templates")


def get_available_hashtags():
    return ["#python", "#fastapi", "#swagger"]  # dummy data


@app.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    params = {
        "request": request,  # do not change, has to be passed
        "hashtags": get_available_hashtags(),  # populates dropdown
    }

    return templates.TemplateResponse("index.html", params)
