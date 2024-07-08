from starlette.exceptions import HTTPException as StarletteHTTPException
from app.main import app
from app.http.shortcuts import render, redirect, is_htmx
from fastapi.exceptions import RequestValidationError
from fastapi import Request, status
from app.http.exceptions import LoginRequiredException


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    
    status_code = exc.status_code
    template_name = "errors/main.html"

    if status_code == status.HTTP_404_NOT_FOUND:
    
         template_name = "errors/404.html"

    context = {"status_code" : status_code}

    return render(request, template_name, context, status_code=status_code)


@app.exception_handler(LoginRequiredException)
async def login_required_exception_handler(request, exc):
#     return redirect("/login/")
    response = redirect(f"/login?next={request.url}", remove_session=True)

    if is_htmx(request): # evitar que aparezce el cuadro de login in htmx
        response.status_code = status.HTTP_200_OK  # HTMX redirect 
        response.headers["HX-Redirect"] = "/login"
    
    return response

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request:Request, exc:RequestValidationError):
        
        errors: str = f'All fields must be filled'
        
        if (request.url.path == "/signup/"):
            return render(request, "auth/signup.html", {"errors" : errors}, status_code=400)
        
        if (request.url.path == "/login/"):
            return render(request, "auth/login.html", {"errors" : errors}, status_code=400)
        
        if (request.url.path == "/videos/create"):
            return render(request, "/videos/create.html", {"errors" : errors}, status_code=400)
        
        if (request.url.path == "/playlist/create"):
            return render(request, "/playlist/create.html", {"errors" : errors}, status_code=400)
        
        if (request.url.path[:8] == "/account"):
            return render(request, "account.html", {"errors" : errors}, status_code=400)

        

