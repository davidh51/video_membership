from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse
from app.http.shortcuts import render, redirect
from app.http.decorators import login_required
from app.db.database import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from app.db.models import User
from app.authentication.oauth2 import create_access_token, get_current_user
from app.mail.send_mail import password_reset
from app.db.schemas_users import UserChangePassword, MySession
from app.authentication.utils import hash
from app.db.schema_errors import schema_or_error
from pydantic import ValidationError
import json

router = APIRouter(prefix='/account')


@router.get('/', response_class=HTMLResponse)
@login_required
async def account_view(request: Request):
    
    session_id = request.cookies.get("session_id") or None
    context = {"logged_in":session_id is not None}

    return render(request, "account.html", context)

@router.post('/', response_class=HTMLResponse)
@login_required
async def update_password(request: Request, email: str = Form(...),
                       db: AsyncSession= Depends(get_session)):
    
    user = await User.get_user(email)
    context = {"confirm_mail" : True}

    if request.user.is_authenticated:
        
        token =  create_access_token({"id" : str(user.id)})
        #reset_link = f"http://localhost:8000/account/{token}"
        reset_link = f"https://video-membership.onrender.com/account/{token}"

        await password_reset("Password Reset", email, 
                             {"title" : "Password Reset",
                             "id" : user.id,
                             "reset_link" : reset_link})

    return render(request, "dashboard.html", context)

@router.get('/{token}',response_class=HTMLResponse)
@login_required
async def reset_request(request:Request, token:str,
                        db: AsyncSession= Depends(get_session)):

    session_id = request.cookies.get("session_id") or None
    context = {"logged_in":session_id is not None, "token":token}

    return render(request, "account.html", context)    

@router.post('/{token}',response_class=HTMLResponse)
@login_required
async def change_password(request:Request, token:str, password:str= Form(...), confirm_password: str = Form(...),
                        db: AsyncSession= Depends(get_session)):
    
    user_id: str = await get_current_user(token, db)
    user_obj = await User.get_user_id(user_id.id)
                                      #no se esta usando la session, solo para no cambiar todo el esquema
    try:
        raw_data = {"password":password, "confirm_password":confirm_password}
        data = UserChangePassword(**raw_data)
        hashed_paswword = hash(data.password.get_secret_value())
        user_obj.password = hashed_paswword #todo esto puede hacerse en los esquemas o models
        await db.commit()
        context = {"changed" : True , "token":token}

    except ValidationError as e:
        error_str = e.json()
        error = json.loads(str(error_str))
        context = {"token":token, "errors" :  error[0]["msg"]}

    return render(request, "account.html", context) 


    
