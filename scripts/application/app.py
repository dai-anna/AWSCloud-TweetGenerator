from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
print(os.getcwd())
from scripts.text_generator.inference import generate_text, corpus

app = FastAPI()

# app.mount("/static", StaticFiles(directory="static"), name="static")


templates = Jinja2Templates(directory="templates")


def get_available_hashtags():
    return ["#python", "#fastapi", "#swagger"]  # dummy data


@app.get("/", response_class=HTMLResponse)
async def read_item(request: Request, userinput: str = Form(...)):
    try:
        pass
    except:
        result = "Your tweet will appear here."

    params = {
        "request": request,  # do not change, has to be passed
        "hashtags": get_available_hashtags(),  # populates dropdown
        "result": result,
    }

    return templates.TemplateResponse("index.html", params)

app.run(host="0.0.0.0", port=8080)