from typing import Annotated

import uvicorn
from fastapi import FastAPI, Form
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic_core import from_json

templates = Jinja2Templates(directory="templates")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

QUESTIONS = from_json(open("questions.json", "r").read())


async def get_context(request, path=""):
    q = QUESTIONS
    answered = []
    parts = path.split(".") if path else []
    for i, p in enumerate(parts):
        if "answers" in q:
            textq = q["question"]
            q = q["answers"][int(p)]
            texta = q.get("text")
            answered.append((".".join(parts[:i]), textq, texta))

    context = {"answered": answered,
               "host": str(request.base_url).rstrip("/")}  # .replace("http://", "https://")

    if "category" in q:
        return {"category": q["category"], **context}

    answers = [(".".join(parts + [str(i)]), a.get("text")) for i, a in enumerate(q.get("answers"))]

    return {"question": q["question"], "answers": answers, **context}


@app.delete(path="/delete/{path}", response_class=HTMLResponse)
async def delete(path: str, request: Request):
    context = await get_context(request, path)
    return templates.TemplateResponse(request=request,
                                      name="card.html",
                                      context=context)


@app.delete(path="/delete", response_class=HTMLResponse)
async def delete(request: Request):
    context = await get_context(request)
    return templates.TemplateResponse(request=request,
                                      name="card.html",
                                      context=context)


@app.post(path="/answer", response_class=HTMLResponse)
async def answer(path: Annotated[str, Form()], request: Request):
    context = await get_context(request, path)
    return templates.TemplateResponse(request=request,
                                      name="card.html",
                                      context=context)


@app.get(path="/", response_class=HTMLResponse)
async def index(request: Request):
    context = await get_context(request)
    return templates.TemplateResponse(request=request,
                                      name="index.html",
                                      context=context)


@app.get(path="/embedded", response_class=HTMLResponse)
async def embedded(request: Request):
    context = await get_context(request)
    return templates.TemplateResponse(request=request,
                                      name="embedded.html",
                                      context=context)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
