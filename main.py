from collections import OrderedDict
from typing import Annotated

import uvicorn
from fastapi import FastAPI, Form
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic_core import from_json
from starlette.middleware.sessions import SessionMiddleware

templates = Jinja2Templates(directory="templates")

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="some-random-string")

questions = from_json(open("questions.json", "r").read())
secret_key = "questions"


async def get_answered(request):
    answered = request.session.get(secret_key)
    if not answered:
        answered = request.session[secret_key] = OrderedDict()
    return answered


async def get_question(request, answer=None, label=None):
    answered = await get_answered(request)
    if label and answer:
        answered[label] = answer

    q = questions
    textqa = []
    for prev_label, prev_answer in answered.items():
        textq = q["question"]
        for a in q.get("answers"):
            if a.get("label") == prev_answer:
                q = a
                break
        texta = q["text"]
        textqa.append((textq, texta, prev_label))

    if "category" in q:
        return {"category": q["category"], "textqa": textqa}
    return {"question": q, "textqa": textqa}


@app.delete(path="/delete/{label}", response_class=HTMLResponse)
async def delete(label: str, request: Request):
    answered = await get_answered(request)
    delete_next = False
    for k in list(answered.keys()):
        if k == label:
            delete_next = True
        if delete_next:
            del answered[k]

    context = await get_question(request)
    return templates.TemplateResponse(request=request,
                                      name="question.html",
                                      context=context)


@app.post(path="/question/{label}", response_class=HTMLResponse)
async def question(label: str, answer: Annotated[str, Form()], request: Request):
    context = await get_question(request, answer, label)
    return templates.TemplateResponse(request=request,
                                      name="question.html",
                                      context=context)


@app.get(path="/", response_class=HTMLResponse)
async def index(request: Request):
    context = await get_question(request)
    return templates.TemplateResponse(request=request,
                                      name="index.html",
                                      context=context)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
