from pydantic import BaseModel
from pydantic_async_validation import async_field_validator, async_model_validator ,AsyncValidationModelMixin
from uuid import UUID
from sqlmodel.ext.asyncio.session import AsyncSession
from app.db.models import Video, Playlist
from app.videos.extractors import extract_video_id
from app.http.exceptions import InvalidUserIDException, VideoAlreadyAddedException, InvalidYouTubeVideoURLException
from app.db import schemas_videos
from sqlmodel import select
from datetime import datetime
from typing import List

class MySession:

    def __init__(self, session:AsyncSession):
        self.session = session
    
    async def my_validation(self, raw_data: dict, SchemaModel: BaseModel):

        cleaned_data = await SchemaModel.validate_data(self, raw_data)
        return cleaned_data
    
        #@async_model_validator(mode="after")
    async def modify_host_id(self, data, replace=False, index=0):
        
        #if not isinstance (raw_data['host_id'], list):
        #    return False
        
        if replace:
            statement = select(Playlist).where(Playlist.db_id == data["db_id"])
            playlist_db = await self.session.exec(statement)
            playlist = playlist_db.first()
            host_ids = playlist.get_videos()
            host_ids.pop(index) 
            playlist.host_ids = host_ids
        
        elif not isinstance (data.host_id, list):
            return False
        
        else:
            statement = select(Playlist).where(Playlist.db_id == data.db_id)
            playlist_db = await self.session.exec(statement)
            playlist = playlist_db.first()
            playlist.host_ids += data.host_id
        
        playlist.updated = datetime.utcnow()
        await self.session.commit()
        return True

        #for key,value in data.model_dump().items():
        #    setattr (playlist, key, value)

class CreatePlaylist(AsyncValidationModelMixin, BaseModel, MySession):
 
    owner_id : UUID
    title : str

    async def validate_data(self, raw_data:dict):
        
        #host_ids = [""]
        try:
            data = CreatePlaylist(**raw_data)
            await data.model_async_validate()
            new_playlist = Playlist(**data.model_dump())
            self.session.add(new_playlist)
            await self.session.commit()
            await self.session.refresh(new_playlist)

            return new_playlist.as_data()
        except:
            raise ValueError("Invalid request.")        
    
class PlaylistVideoAddSchema(AsyncValidationModelMixin, BaseModel, MySession):
    url: str 
    title: str 
    owner_id: str 
    host_id: List
    db_id : UUID # db_id 

    @async_field_validator("url")
    async def validate_youtube_url(self, value: str):
        url = value
        video_id = extract_video_id(url)
        if video_id is None:
            raise ValueError(f"{url} is not valid")
        return value
    
    #@async_field_validator("db_id")   # no pasa la sesion al ser un validator de la clase
    #async def validate_playlist_id(self, value: str):
        
    #    statement = select(Playlist).where(Playlist.db_id == value)
    #    playlist_db = await self.session.exec(statement)
    #    playlist = playlist_db.first()

    #    if playlist is None:
    #        raise ValueError(f"{value} is not a valid Playlist")
    #    return value 
    
    #async def get_or_create(self, video_info:dict):
    async def validate_data(self, raw_data:dict): 
        
        data = PlaylistVideoAddSchema(**raw_data)#validate schema before updating
        await data.model_async_validate()
        data.host_id[0] = extract_video_id(data.url)
        video_obj = None
        extra_data = {}

        try:
            if data.host_id[0] is None:
                raise InvalidYouTubeVideoURLException

            statement = select(Playlist).where(Playlist.db_id == data.db_id)
            playlist_db = await self.session.exec(statement)
            playlist = playlist_db.first()

            if playlist is None:
                raise ValueError(f"{data.db_id} is not a valid Playlist")    
            
            video_obj, created = await PlaylistVideoAddSchema.get_or_create(self, data)
            
            if data.db_id: #db_id de playlist no video

                created = await MySession(self.session).modify_host_id(data)
            
            return video_obj

        except InvalidYouTubeVideoURLException:
           raise ValueError(f"{raw_data['url']} is not a valid YouTube URL")
        
        except:
            raise ValueError("Invalid request.")
        
    #@staticmethod
    async def get_or_create(self, data):
        
        data_copy = data.copy()
        obj = None
        created = False

        try:     
            statement = select(Video).where(Video.host_id == data_copy.host_id[0])
            video_db = await self.session.exec(statement)
            obj = video_db.first()
            
            if obj is None:
                #del data['db_id'] el mismo dict data y raw_data cambia en todas las func, con la lista host id tambn 
                data_dict = dict(**data_copy.model_dump())
                data_dict ["host_id"] =  data_copy.host_id[0]
                obj = await schemas_videos.MySession(self.session).my_validation(data_dict, schemas_videos.VideoCreateSchema)
                created = True
                
                return obj, created
            
            return obj.as_data(), created
        
        except:
            raise Exception("Invalid Request")


