from fastapi import Request, HTTPException, status
from functools import wraps
#from app.authentication.oauth2 import get_current_user
from app.http.exceptions import LoginRequiredException
from app.http.shortcuts import redirect


def login_required(func):
    @wraps(func)
    async def wrapper (request: Request, *args, **kwargs):

        #session_token = request.cookies.get("session_id")
        #user_session = await get_current_user (session_token)
        
        if not request.user.is_authenticated:# cambia cuando se implementa el backend

            raise LoginRequiredException(status_code=status.HTTP_401_UNAUTHORIZED)
        
        return await func(request, *args, **kwargs)
    
    return wrapper