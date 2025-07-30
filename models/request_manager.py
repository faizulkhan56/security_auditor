from fastapi import FastAPI
import httpx
import asyncio
from pydantic import BaseModel


class TextInput(BaseModel):
    text: str


app = FastAPI(title="Request Manager", description="It will get the requests from input and in backend it will request",
              version="1.0.0",
              docs_url="/docs",
              redoc_url="/redoc")

SERVICE_URLS = [
    "http://localhost:9001/validate",
    # "http://localhost:8003/data",
    "http://localhost:9003/validate",
]


async def fetch(client: httpx.AsyncClient, url: str, payload: dict):
    try:
        response = await client.post(url, json=payload, timeout=5.0)
        response.raise_for_status()
        return {"url": url, "data": response.json()}
    except Exception as e:
        return {"url": url, "error": str(e)}


@app.post("/aggregate")
async def aggregate(input_data: TextInput):
    async with httpx.AsyncClient() as client:
        tasks = [fetch(client, url, input_data.dict()) for url in SERVICE_URLS]
        results = await asyncio.gather(*tasks)

    return {"merged": results}
