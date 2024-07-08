from fastapi import APIRouter, Depends, Request, Form, Response
from sqlmodel.ext.asyncio.session import AsyncSession
from app.db.database import get_session
from fastapi.responses import HTMLResponse
from app.db.schema_errors import schema_or_error
from app.http.shortcuts import render, redirect
from app.db.schemas_users import UserLogin, MySession
from typing import Optional

router = APIRouter() #(prefix='/login')

@router.get('/login', response_class=HTMLResponse)
async def login_view(request: Request):
     
    #session_id = request.cookies.get("session_id") or None
    return render(request, "auth/login.html", 
                  {"logged_in": request.user.is_authenticated}) #session_id is not None})

@router.post('/login', response_class=HTMLResponse)
async def login_post (request: Request, email:str= Form(...), password:str= Form(...),
                        db: AsyncSession= Depends(get_session)):

    raw_data = {"email":email, "password":password}
    data, errors = await schema_or_error(raw_data, db, UserLogin, MySession)
    context = {"data" : data}
    redirect_path =  request.url.query[5:]
       
    if len(errors) > 0:
        context = {"data" : data , "errors" : errors[0]["msg"]}
        return render(request, "auth/login.html",context, status_code=400)
    
    if "http://127.0.0.1" not in redirect_path:
        redirect_path = "/"
    
    #response.set_cookie(key='session_id', value=context["data"], httponly=True)     
    return redirect (redirect_path or "/account/", cookies={'session_id' : context["data"]})
        #return redirect ("/login/", cookies={'session_id' : access_token})

@router.get('/logout', response_class=HTMLResponse)
async def log_out_view(request: Request):
    
    if not request.user.is_authenticated:
        return redirect("/login")
    
    return render(request, "auth/logout.html", {}) 

@router.post('/logout', response_class=HTMLResponse)
async def log_out_post(request: Request):

    return redirect("/login", remove_session=True) 


