from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Optional
import os

print(os.system("ls -l"))

if os.getenv("IS_DOCKER") is not None:
    print(os.system("ls -l templates"))
    print("Running in Docker")
    templates = Jinja2Templates(directory="templates")
    from inference import finish_sentence, corpus
else:
    print("Running locally")
    templates = Jinja2Templates(directory="scripts/application/templates")

app = FastAPI()

# app.mount("/static", StaticFiles(directory="static"), name="static")


def get_available_hashtags():
    return ["Select trending topic...", "#python", "#fastapi", "#swagger"]  # dummy data


@app.get("/", response_class=HTMLResponse)
async def read_item(request: Request, userinput: Optional[str] = Form(None)):
    result = None
    selected_topic = None
    try:
        print(request.query_params.get("userinput"))
        result = request.query_params.get("userinput")
        selected_topic = request.query_params.get("userinput")
    except:
        result = "Your tweet will appear here."
        selected_topic = get_available_hashtags()[0]

    params = {
        "request": request,  # do not change, has to be passed
        "hashtags": get_available_hashtags(),  # populates dropdown
        "selected_topic": selected_topic,  # populates dropdown
        "result": result,
    }

    return templates.TemplateResponse("index.html", params)
