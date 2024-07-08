from fastapi import APIRouter, Depends, Form, Request
from app.db.schemas_users import UserSignUp, MySession
from app.db.models import User
from app.db.database import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi.responses import HTMLResponse
from app.db.schema_errors import schema_or_error
from app.http.shortcuts import render, redirect
from app.mail.send_mail import send_registration_mail


router = APIRouter (prefix='/signup')

@router.get('/', response_class=HTMLResponse)
async def signup(request: Request):
     
     return render(request, "auth/signup.html", {})

@router.post('/', response_class=HTMLResponse)
async def create_user(request: Request, email: str = Form(...), password:str= Form(...), 
                      confirm_password: str = Form(...), db: AsyncSession= Depends(get_session)):

     raw_data = {"email":email, "password":password, "confirm_password":confirm_password}
     data, errors = await schema_or_error(raw_data, db, UserSignUp, MySession)
     context = {"data" : data , "errors" : errors, "confirm_mail" : True}

     if len(errors) > 0:
          context = {"data" : data , "errors" : errors[0]["msg"]}
          return render(request, "auth/signup.html", context, status_code=400)
     
     #redirect_path =  data.get("path") or "/login/"

     #token = create_access_token({"id" : str(user.id)})
     #activate_link = f"http://localhost:8000/login/"  #{token}"
     activate_link = f"https://video-membership.onrender.com/login/"
     
     await send_registration_mail("Activate succesfull", data.get("mail"),
                                   {"title" : "Registration succesfull",
                                   "validate_link" : activate_link,
                                   "mail" : data.get("mail")})
     
     return render(request, "dashboard.html", context)
     #return HTMLResponse("Email sent, validate email")
     #return redirect(redirect_path)
     #return redirect("/login/", context)

                   



     