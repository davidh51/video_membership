from fastapi import APIRouter, Request, Form, Depends, status
from fastapi.responses import HTMLResponse
from app.http.shortcuts import render, redirect, get_object_or_404, is_htmx
from app.http.decorators import login_required
from app.db.schema_errors  import schema_or_error
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.db.database import get_session
from app.db.schemas_playlist import MySession, CreatePlaylist, PlaylistVideoAddSchema
from app.db.models import Playlist, Video
from uuid import UUID
from starlette.exceptions import HTTPException as StarletteHTTPException
from typing import Optional

router = APIRouter(prefix="/playlist")


@router.get("/create", response_class=HTMLResponse)
@login_required
async def playlist_create_view(request:Request):

    return render(request, "playlist/create.html", {})

@router.post("/create", response_class=HTMLResponse)
@login_required
async def playlist_create_post_view(request:Request, title:str=Form(...),
                                    db:AsyncSession=Depends(get_session)):

    raw_data:dict = {"title":title, "owner_id" : UUID(request.user.username)}
    
    data, errors = await schema_or_error(raw_data, db, CreatePlaylist, MySession)
    context = {"data" : data  , "errors" : errors }

    if len(errors) > 0:

        context = {"data" : data , "errors" : errors[0]["msg"]}
        return render(request, "playlist/create.html",context ,status_code=400)
    
    redirect_path =  data.get("path") or "/playlist/detail"
    return redirect(redirect_path)

@router.get("/", response_class=HTMLResponse)
@login_required
async def playlist_list_view(request:Request, db: AsyncSession=Depends(get_session)):

    statement = select(Playlist).order_by(Playlist.db_id)
    playlist_db = await db.exec(statement)
    playlist = playlist_db.all()

    context = {"object_list" : playlist }
        
    return render(request, "playlist/list.html", context)

@router.get("/{db_id}", response_class=HTMLResponse)
@login_required
async def playlist_detail_view(request:Request, db_id: str, db: AsyncSession=Depends(get_session)):
    
    playlist = await get_object_or_404(Playlist, db_id, db, request, path = request.url.path) 
    video_list = []

    if playlist.get_videos() != [""]:

        i = 0
        for host_id in playlist.get_videos():# para poder pasar el video como obj
            statement = select(Video).where(Video.host_id == host_id)
            video_db = await db.exec(statement)
            video_obj = video_db.first()

            if video_obj is not None:
                video_list.append(video_obj)
    
    context = {"object" : playlist, "videos_list" : video_list}
    return render(request, "playlist/detail.html", context)


@router.get("/{db_id}/add-video", response_class=HTMLResponse)
@login_required
async def playlist_video_create_view(request:Request, db_id: str, is_htmx=Depends(is_htmx)):

    context = {"db_id" : db_id}

    if not is_htmx:
        raise StarletteHTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    
    return render(request, "playlist/htmx/add-video.html", context)


@router.post("/{db_id}/add-video", response_class=HTMLResponse)
@login_required
async def playlist_video_create(request:Request, db_id: str, url:str=Form(...), title:str=Form(...),
                            db:AsyncSession=Depends(get_session), is_htmx=Depends(is_htmx)):

    raw_data:dict = {"url":  url , "title":title, "host_id": [""], "db_id" : db_id,
                     "owner_id" : str(request.user.username)}

    data, errors = await schema_or_error(raw_data, db, PlaylistVideoAddSchema, MySession)
    redirect_path =  data.get("path") or f"/playlist/{db_id}"
    context = {"data" : data  , "errors" : errors, "title" : data.get('title'),
               "path" : redirect_path}
    
    if not is_htmx:
        raise StarletteHTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    if len(errors) > 0:#no se estanm evaluando errores en el esquema, como videos repetidos
        context = {"data" : data , "errors" : errors[0]["msg"]}#no incluir el status de error al ser htmx
        return render(request, "playlist/htmx/add-video.html",context)

    return render(request, "videos/htmx/link.html", context)

@router.post("/{db_id}/{host_id}/delete", response_class=HTMLResponse)
@login_required
async def playlist_remove_video(request:Request, db_id: str, host_id: str, is_htmx=Depends(is_htmx),
                        db:AsyncSession=Depends(get_session), index: Optional[int]=Form(default=None)):

    try:
        obj = await get_object_or_404(Playlist, db_id, db, request, path = f"/playlist/{db_id}")
    except:
        return HTMLResponse("Error, try again")
    
    if not is_htmx:
        raise StarletteHTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    if isinstance(index, int):
        deleted = await MySession(db).modify_host_id(obj.as_data(), True, index)
        
    return HTMLResponse("Deleted")

@router.post("/{db_id}/delete", response_class=HTMLResponse)
@login_required
async def remove_playlist(request:Request, db_id: str, is_htmx=Depends(is_htmx),
                        db:AsyncSession=Depends(get_session)):

    try:
        obj = await get_object_or_404(Playlist, db_id, db, request, path = f"/playlist/{db_id}")
    except:
        return HTMLResponse("Error, try again")
    
    if not is_htmx:
        raise StarletteHTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    await db.delete(obj)
    await db.commit()
        
    return HTMLResponse("Removed")