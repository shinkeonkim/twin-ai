import os
import sys

import uvicorn
from fastapi import FastAPI, Request
from pydantic import BaseModel

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from llm import llm_api
from persona import prompt_engineering

app = FastAPI()


class AskRequest(BaseModel):
    question: str
    model: str = "gemini"  # 'gemini' or 'openai'


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ask")
def ask(req: AskRequest):
    prompt = prompt_engineering.build_prompt(req.question)
    if req.model == "gemini":
        answer = llm_api.call_gemini_api(prompt)
    else:
        answer = llm_api.call_openai_api(prompt)
    return {"answer": answer, "prompt": prompt}


if __name__ == "__main__":
    uvicorn.run("server.api_server:app", host="0.0.0.0", port=8000, reload=True)
