from app.config import settings
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import status, Request
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
#from app.db.database import get_session
from starlette.exceptions import HTTPException as StarletteHTTPException


templates = Jinja2Templates(directory=str(settings.TEMPLATES_DIR))

def is_htmx (request : Request):
    return request.headers.get("hx-request") == "true"

async def get_object_or_404(KlassName, id, db:AsyncSession, request:Request, path):

    if path == f"/videos/{id}":

        statement = select(KlassName).where(KlassName.host_id == id)
        obj_db = await db.exec(statement)
        obj = obj_db.first()
    
    elif path == f"/playlist/{id}":
        
        statement = select(KlassName).where(KlassName.db_id == id)
        obj_db = await db.exec(statement)
        obj = obj_db.first()

    if obj is not None:
        return obj 
    elif obj is None:
        raise StarletteHTTPException(status_code=status.HTTP_404_NOT_FOUND)
    else:
        raise StarletteHTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
   
def redirect (path, cookies: dict= {}, remove_session=False):

    response = RedirectResponse(path, status_code=status.HTTP_303_SEE_OTHER)
                                   #303 hace un redirect con GET y no el ultimousado, como post
    for k,v in cookies.items():
        response.set_cookie(key=k, value=v, httponly=True)

    if remove_session:
        response.set_cookie(key="session_ended", value=1, httponly=True)
        response.delete_cookie("session_id")
          
    return response
    
def render(request, template_name, context:dict={}, status_code=status.HTTP_200_OK, 
           cookies:dict={}):

    ctx = context.copy()
    ctx.update({"request": request})
    t = templates.get_template(template_name)
    html_str = t.render(ctx)  #vuelve str el template, hace el render, no llama la misma fncion!!!
    response = HTMLResponse(html_str, status_code=status_code)

    if len(cookies.keys()) > 0:
        for k, v in cookies.items():
            response.set_cookie(key=k, value=v, httponly=True)#htttponly no permite que alteren las cookies
                                                            #desde la pag web fuera del backend
    
    #print (request.cookies)
    return response
    #return templates.TemplateResponse(template_name, ctx, status_code)


