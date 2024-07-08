from app.authentication.oauth2 import verify_access_token
from starlette.authentication import AuthenticationBackend, SimpleUser, UnauthenticatedUser,AuthCredentials
from fastapi import Depends

class JWTCookieBackend(AuthenticationBackend):
    async def authenticate(self, request):

        session_id: str = request.cookies.get("session_id")
        user_id = verify_access_token(session_id)

        if user_id is None:

            roles = ["anon"]   #not authenticated

            return AuthCredentials(roles), UnauthenticatedUser()
        
        roles = ["authenticated"]

        return AuthCredentials(roles), SimpleUser(user_id)