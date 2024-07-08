from jose import jwt, ExpiredSignatureError
from datetime import datetime, timedelta 
from app.config import settings 
from app.db.schemas_videos import TokenData
from app.db.models import User
from fastapi import Depends, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel.ext.asyncio.session import AsyncSession
from app.db.database import get_session
from sqlmodel import select
from uuid import UUID

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/login/')

ALGORITHM = settings.ALGORITHM 
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
SECRET_KEY = settings.SECRET_KEY

def create_access_token (payload: dict):
    to_encode = payload.copy()

    expiration_time =  datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp" : expiration_time})

    jwt_token = jwt.encode (to_encode, SECRET_KEY, algorithm= ALGORITHM)

    return jwt_token

def verify_access_token (token: str):
    
    id: str = None
    try: 
        payload = jwt.decode(token, SECRET_KEY, algorithms= [ALGORITHM])
        id: str= payload.get("id")
        #if id is None:
            #raise credentials_exception
        token_data = TokenData(id=id)
        
    except ExpiredSignatureError as e:
        print(e, "Log out user, expired time")
    except:
        pass

    if id is None:
        return None
    
    return token_data.id

#async def get_current_user(token: str = Depends(oauth2_scheme),db: AsyncSession= Depends(get_session)):

async def get_current_user(token:str, db: AsyncSession= Depends(get_session)):

    #credentials_exception= HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
    #                                     detail="Token could not verify credentails", 
    #                                     headers= {"WWW-Authenticate":"Bearer"})
    if token is None: # Cambiar return a None ya que tenia errors con el middlware
        return None
        #raise LoginRequiredException(status_code=status.HTTP_401_UNAUTHORIZED)

    #credentials_exception = LoginRequiredException(status_code=status.HTTP_401_UNAUTHORIZED)

    current_user_id= verify_access_token(token)
    statement = select(User).where(User.id == UUID(current_user_id))
    user_db = await db.exec(statement)
    current_user = user_db.first()
   
    return current_user

 