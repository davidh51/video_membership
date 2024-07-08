from fastapi import FastAPI, Request, status, Body
from fastapi.responses import HTMLResponse, JSONResponse
from contextlib import asynccontextmanager
#from app.db.database import init_models
from app.routers import login, sign_up, inside_account, videos, watch_event, playlist
from app.http.shortcuts import render, redirect
from starlette.middleware.authentication import AuthenticationMiddleware
from app.authentication.backend import JWTCookieBackend
#from starlette.authentication import requires
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from app.indexing.client import search_index, update_index
from app.http.decorators import login_required

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("server starting")
    #await init_models()
    yield
    print ("server shuttind down")

app = FastAPI(title= "Video Membership",
              version="1.0",
              description="Simple app",
              lifespan=lifespan)

#origins = [ "https://www.google.com" ]
#origins = [ "*" ]

origins = [
    "http://localhost",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:8000/watch-event",
    "https://127.0.0.1:8000/watch-event"
]

app.add_middleware( #permite ingresar desde un domain diferente como google y no solo desde 127.0...8000
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["POST"],   #["POST"],
    allow_headers=["Content-Type",
                   'Accept'],
)

app.add_middleware(AuthenticationMiddleware, backend=JWTCookieBackend())

from app.http.handlers import * #noqa

app.include_router(sign_up.router)
app.include_router(login.router)
app.include_router(inside_account.router)
app.include_router(videos.router)
app.include_router(watch_event.router)
app.include_router(playlist.router)

@app.get('/search', response_class=HTMLResponse)
@login_required          
async def search(request: Request, q: Optional[str]= None):

    query = None
    context = {}

    if q is not None:
        query = q
        result = search_index(query)
        hits = result.get("hits") or []
        num_hits = result.get("nbHits")
        context = {
            "query" : query, "hits" : hits , "number_hits" : num_hits}

    return render(request, "search/detail.html", context)

@app.post('/update-index', response_class=HTMLResponse)
@login_required  
async def htmx_update_index(request: Request):

    count = await update_index()
    return HTMLResponse(f"{count} refreshed") 

@app.get('/', response_class=HTMLResponse)
#@requires(['authenticate'])             #backend function
async def hello(request: Request):

    context = {"confirm_mail" : False}
    if request.user.is_authenticated:
        return render(request, "dashboard.html", context, status_code=status.HTTP_200_OK)

    #return{"Hello":"world"}
    context = {#"request" : request,
               #"abc" : 123
               }
    return render(request, "home.html", context)

    #return templates.TemplateResponse(request,"home.html", context)


#1. Video ->> Host(Youtube) , Analytics
#2. Members ->> SIgn up, login, remember things, email valid, payment

