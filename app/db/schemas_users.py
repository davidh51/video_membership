from pydantic import BaseModel, EmailStr, SecretStr, model_validator, Field
from pydantic_async_validation import async_field_validator, async_model_validator ,AsyncValidationModelMixin
from sqlmodel.ext.asyncio.session import AsyncSession
from app.db.models import User
from app.http.exceptions import UserHasAccountException, InvalidUserIDException, InvalidPasswordException
from app.authentication.utils import hash, verify_password
from app.authentication.oauth2 import create_access_token
from sqlmodel import select

class MySession:

    def __init__(self, session:AsyncSession):
        self.session = session
    
    async def my_validation(self, raw_data: dict, BaseSchema:BaseModel):

        cleaned_data = await BaseSchema.validate_data(self, raw_data)
        return cleaned_data
        
class UserLogin(AsyncValidationModelMixin, BaseModel, MySession):
    email: EmailStr
    password: SecretStr

    async def validate_data(self, user_info):

        try:
            user_info = UserLogin(**user_info)
            await user_info.model_async_validate()
            statement = select(User).where(User.email == user_info.email)
            user_db = await self.session.exec(statement)
            user = user_db.first()

            if user and verify_password(user_info.password.get_secret_value(), user.password):
                access_token =  create_access_token({"id" : str(user.id)})
                return access_token
            
            else:
                raise InvalidPasswordException ("Invalid password")
        
        except InvalidUserIDException:
            raise ValueError("There's a problem with your account, please try again.")
        except InvalidPasswordException:
            raise ValueError("Invalid password")

class UserSignUp(AsyncValidationModelMixin, BaseModel, MySession):
    email: EmailStr
    password: SecretStr
    confirm_password: SecretStr  

    async def validate_data(self, user_info):   

        try:
            user_info = UserSignUp(**user_info)
            await user_info.model_async_validate()
            statement = select(User).where(User.email == user_info.email)
            user_db = await self.session.exec(statement)
            user = user_db.first()

            if user_info.confirm_password != user_info.password:
                raise ValueError('passwords do not match') 

            if user is not None:
                raise UserHasAccountException("User already has account.")
               
            del user_info.confirm_password
            hashed_paswword = hash(user_info.password.get_secret_value())
            user_info.password = hashed_paswword

            new_user = User(**user_info.model_dump())
            self.session.add(new_user)
            await self.session.commit()
            await self.session.refresh(new_user)

            return new_user.as_data()

        except UserHasAccountException:
            raise ValueError(f"User already has account.")
        
class UserChangePassword(BaseModel):
    password: SecretStr
    confirm_password: SecretStr 

    @model_validator(mode='after')
    def check_passwords_match(self): 
        pw1 = self.password
        pw2 = self.confirm_password
        if pw1 is not None and pw2 is not None and pw1 != pw2:
            raise ValueError('passwords do not match')
        return self
    
        
        