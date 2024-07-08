from fastapi import APIRouter, Request, Form, Depends, status
from fastapi.responses import HTMLResponse
from app.http.shortcuts import render, redirect, get_object_or_404, is_htmx
from app.http.decorators import login_required
from app.db.schema_errors  import schema_or_error
from sqlmodel import select
from app.db.models import Video, User
from sqlmodel.ext.asyncio.session import AsyncSession
from app.db.database import get_session
from app.db.schemas_watch_event import MySessionEvent
from app.db.schemas_videos import MySession, VideoCreateSchema, VideoEditSchema
from app.http.exceptions import HTTPException
from typing import Optional

router = APIRouter(prefix="/videos")

#def is_htmx (request : Request):    
#    return request.headers.get("hx-request") == "true" #htmx request incluye un header con hx-...

@router.get("/create", response_class=HTMLResponse)
@login_required
async def video_create_view(request:Request): #, is_htmx=Depends(is_htmx)):

#    if is_htmx:
#        return render(request, "videos/htmx/create.html", {})

    return render(request, "videos/create.html", {})

@router.post("/create", response_class=HTMLResponse)
@login_required
async def video_create_view(request:Request, url:str=Form(...), title:str=Form(...),
                            db:AsyncSession=Depends(get_session)): #, is_htmx=Depends(is_htmx)):

    raw_data:dict = {"url":  url , "title":title, "host_id": "",
                     "owner_id" : str(request.user.username)}
    
    data, errors = await schema_or_error(raw_data, db, VideoCreateSchema, MySession)
    context = {"data" : data  , "errors" : errors , "url" : url, "title" : data.get('title')}
    redirect_path =  data.get("path") or "/videos/detail"

    """ HANDLE htmX REQUESTS """
#    if is_htmx:# al ser un get request no deberia tener errores
#        if len(errors) > 0:
#            context = {"data" : data , "errors" : errors[0]["msg"]}
#            return render(request, "videos/htmx/create.html",context) #no incluir el status de error al ser htmx
        
#        context = {"path" : redirect_path , "title" : data.get('title')} 
#        return render(request, "videos/htmx/link.html", context)
    
    """ HANDLE normAL html REQUESTS """
    if len(errors) > 0:
    
        context["errors"] = context["errors"][0]["msg"]
        return render(request, "videos/create.html",context ,status_code=400)
    
    return redirect(redirect_path)

@router.get("/", response_class=HTMLResponse)
@login_required
async def video_list_view(request:Request, db: AsyncSession=Depends(get_session)):

    statement = select(Video).order_by(Video.db_id)
    video_db = await db.exec(statement)

    context = {"object_list" : video_db}

    return render(request, "videos/list.html", context)

@router.get("/{host_id}", response_class=HTMLResponse)
@login_required
async def video_detail_view(request:Request, host_id: str, db: AsyncSession=Depends(get_session),):
    
    video = await get_object_or_404(Video, host_id, db, request, path = request.url.path) 
    start_time = 0
    if request.user.is_authenticated:

        user_id = request.user.username
        start_time = await MySessionEvent(db).get_resume_video(host_id, user_id)
    
    context = {"host_id" : host_id , "object" : video, "start_time" : start_time}
    
    return render(request, "videos/detail.html", context)

@router.get("/{host_id}/edit", response_class=HTMLResponse)
@login_required
async def edit_view(request:Request,host_id:str, db: AsyncSession=Depends(get_session)):

    video_obj = await get_object_or_404(Video, host_id, db, request, path = f"/videos/{host_id}")

    context = {"object" : video_obj}

    return render(request, "videos/edit.html", context)

@router.post("/{host_id}/edit", response_class=HTMLResponse)
@login_required
async def video_edit_view(request:Request, host_id:str, url:str=Form(...), title:str=Form(...),
                        db:AsyncSession=Depends(get_session)): 

    raw_data:dict = {"url":  url , "title":title, "owner_id" : str(request.user.username)}
    
    video_obj = await get_object_or_404(Video, host_id, db, request, path = f"/videos/{host_id}")

    data, errors = await schema_or_error(raw_data, db, VideoEditSchema, MySession)
    context = {"object" : video_obj, "data" : data , "errors" : errors}
    
    if len(errors) > 0:
    
        context["errors"] = context["errors"][0]["msg"]
        return render(request, "videos/edit.html",context ,status_code=400)
    
    host_id_updated = await MySession(db).modify_host_id(url,title, video_obj, save=True) 
    
    return render(request, "videos/edit.html",context)

@router.get("/{host_id}/hx-edit", response_class=HTMLResponse)
@login_required
async def edit_hx_view(request:Request,host_id:str, is_htmx=Depends(is_htmx),
                       db: AsyncSession=Depends(get_session)):
    
    if not is_htmx:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    
    obj = None
    not_found = False

    try:
        video_obj = await get_object_or_404(Video, host_id, db, request, path = f"/videos/{host_id}")
    except:
        not_found = True
    if not_found:
        return HTMLResponse("Not found, try again")
    
    context = {"object" : video_obj}

    return render(request, "videos/htmx/edit.html", context)

@router.post("/{host_id}/hx-edit", response_class=HTMLResponse)
@login_required
async def video_hx_edit_view(request:Request, host_id:str, url:str=Form(...), title:str=Form(...),
                            delete: Optional[bool] =Form(default=False), is_htmx=Depends(is_htmx),
                            db:AsyncSession=Depends(get_session)): 
    if not is_htmx:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    
    video_obj = None
    not_found = False

    try:
        video_obj = await get_object_or_404(Video, host_id, db, request, path = f"/videos/{host_id}")
    except:
        not_found = True

    if not_found:
        return HTMLResponse("Not found, try again")
    
    if delete:
        await db.delete(video_obj)
        await db.commit()
        return HTMLResponse("Deleted")
    
    raw_data:dict = {"url":  url , "title":title, "owner_id" : str(request.user.username)}

    data, errors = await schema_or_error(raw_data, db, VideoEditSchema, MySession)
    context = {"object" : video_obj, "data" : data , "errors" : errors}#agregar el obj porque viene del template
                                                            #en el hx-post de una request diferente y no sabe quien es el host_id objec
    if len(errors) > 0:
    
        context["errors"] = context["errors"][0]["msg"]
        return render(request, "videos/htmx/edit.html",context )
    
    host_id_updated = await MySession(db).modify_host_id(url,title, video_obj, save=True) 

    return render(request, "videos/htmx/list_inline.html",context)
  