from wsgiref.util import request_uri
from fastapi import FastAPI
from fastapi.responses import FileResponse,RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from decouple import config
import hashlib
import base64
import time
import redis

HASH_LENGTH=int(config("HASH_LENGTH"))

class CreateShortUrlRequest(BaseModel):
    url: str

app = FastAPI()
redis_client = redis.Redis(host=config("REDIS_HOST"),
    port=config("REDIS_PORT"),
    username=config("REDIS_USER"),
    password=config("REDIS_PASSWORD"))

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=FileResponse)
async def index():
    return "static/index.html"

@app.post("/")
async def create_short_url(request: CreateShortUrlRequest):

    shortened_url_key = get_key_from_url(request.url)
    saved_url = redis_client.setnx(name=shortened_url_key, value=request.url)
    
    if saved_url == 0:
        if (redis_client.get(request.url) != None):
            return {
                "shortUrl": shortened_url_key
            }

        while saved_url == 0:
            shortened_url_key = get_key_from_url(request_uri, time.time_ns())
            saved_url = redis_client.setnx(name=shortened_url_key, value=request.url)
    
    redis_client.set(request.url, shortened_url_key)
    
    return {
        "shortUrl": shortened_url_key
    }
    

@app.get("/{short_id}")
async def get_short_url(short_id: str):
    long_url = redis_client.get(short_id)

    if long_url == None:
        return FileResponse("static/404.html")
    
    return RedirectResponse(long_url.decode("utf-8"))

def get_key_from_url(url: str, salt=""):
    url_to_shorten = f'{url}{salt}'.encode('utf-8')
    url_hash_bytes = hashlib.sha1(url_to_shorten).digest()
    url_safe_hash = base64.urlsafe_b64encode(url_hash_bytes)
    url_safe_str = url_safe_hash.decode("utf-8")
    return url_safe_str[0:HASH_LENGTH]