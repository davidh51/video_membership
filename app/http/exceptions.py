from starlette.exceptions import HTTPException 


class LoginRequiredException(HTTPException):
    pass

##Videos exceptions
class InvalidUserIDException(Exception):
    pass

class VideoAlreadyAddedException(Exception):
    pass

class InvalidYouTubeVideoURLException(Exception):
    pass

class UserHasAccountException(Exception):
    pass

class InvalidPasswordException(Exception):
    pass
