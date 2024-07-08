from pydantic import BaseModel
from pydantic_async_validation import async_field_validator, async_model_validator ,AsyncValidationModelMixin
from uuid import UUID
from sqlmodel.ext.asyncio.session import AsyncSession
from app.db.models import User, Video
from app.videos.extractors import extract_video_id
from app.http.exceptions import InvalidUserIDException, VideoAlreadyAddedException, InvalidYouTubeVideoURLException
from sqlmodel import select

class MySession:

    def __init__(self, session:AsyncSession):
        self.session = session
    
    async def my_validation(self, raw_data: dict, BaseSchema: BaseModel):

        cleaned_data = await BaseSchema.validate_data(self, raw_data)
        return cleaned_data
    
    async def modify_host_id(self, url, title, video_obj:Video, save=True):

        host_id = extract_video_id(url)
        if not host_id:
            return None
        
        video_obj.title = title
        video_obj.host_id = host_id
        video_obj.url = url
        await self.session.commit()
        return url

class VideoEditSchema(AsyncValidationModelMixin, BaseModel):
    url: str 
    title : str

    @async_field_validator("url")
    async def validate_url(self, value: str):
        url = value
        video_id = extract_video_id(url)
        if video_id is None:
            raise ValueError(f"{url} is not valid")
        return value 
    
    async def validate_data(self, video_info:dict):

        video = VideoEditSchema(**video_info) 
        await video.model_async_validate()
        return video
    
        #host_id = extract_video_id(video_info.url) # porque estaria evaluando si ya esta pero incluiria el mismo host_id
        #statement = select(Video).where(Video.host_id == host_id)
        #video_db = await self.session.exec(statement)
        #video = video_db.first()

        #if video is not None:
        #    raise ValueError(f"{video_info.url} has already been added.")

class VideoCreateSchema(AsyncValidationModelMixin, BaseModel):
    url: str 
    title : str
    owner_id: str 
    host_id: str

    @async_field_validator("url")
    async def validate_youtube_url(self, value: str):
        url = value
        video_id = extract_video_id(url)
        if video_id is None:
            raise ValueError(f"{url} is not valid")
       
    #@async_model_validator(mode="after")
    async def validate_data(self, video_info:dict):
        
        new_video = VideoCreateSchema(**video_info)
        await new_video.model_async_validate() # esta verificando dos veces
        url = new_video.url
        if url is None:
            raise ValueError("A valid url is required.")
        
        try:
            new_video.host_id = extract_video_id(url)
        
            if new_video.host_id is None:
                raise InvalidYouTubeVideoURLException("Invalid URL video")
        
            statement = select(User).where(User.id == UUID(new_video.owner_id))
            user_db = await self.session.exec(statement)
            user = user_db.first()  

            if user is None:
                raise InvalidUserIDException("Invalid user_id")

            #statement = select(Video).where(Video.host_id == new_video.host_id)
            #video_db = await self.session.exec(statement)
            #video = video_db.first()
            video = await Video.get(new_video.host_id)

            if video is not None:
                raise VideoAlreadyAddedException("Video already added")
            
            new_video = Video(**new_video.model_dump())
            self.session.add(new_video)
            await self.session.commit()
            await self.session.refresh(new_video)

            return new_video.as_data()

        except InvalidYouTubeVideoURLException:
            raise ValueError(f"{url} is not a valid YouTube URL")
        except VideoAlreadyAddedException:
            raise ValueError(f"{url} has already been added.")
        except InvalidUserIDException:
            raise ValueError("There's a problem with your account, please try again.")
        except:
            raise ValueError("There's a problem with your account, please try again.")
        #if video_obj is None:
        #    raise ValueError("There's a problem with your account, please try again.")
        #if not isinstance(video_obj, Video):
        #    raise ValueError("There's a problem with your account, please try again.")

class Token (BaseModel):
    access_token : str
    token_type: str

class TokenData (BaseModel):
    id: str