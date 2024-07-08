from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, declarative_base, relationship
from sqlalchemy.sql.expression import text
from uuid import UUID, uuid1
from sqlalchemy import ForeignKey, DateTime
from app.http.shortcuts import templates
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy import PickleType
from typing import List
from sqlmodel import select
from app.db.database import async_session, Base
from sqlmodel.ext.asyncio.session import AsyncSession

session: AsyncSession =  async_session()

#Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID]= mapped_column(primary_key=True, unique=True, default=uuid1)
    email: Mapped[str] = mapped_column(primary_key=True, nullable=False, unique=True)
    password :Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),default=text('now()'), nullable=False)

    def as_data(self):
        return {"mail":self.email, "path" : self.path}

    @property 
    def path(self):
        return f"/login/" #{self.host_id}"
    
    @staticmethod
    async def get_user(mail):

        statement = select(User).where(User.email == mail)
        user_db = await session.exec(statement)
        user = user_db.first()

        return user
    
    @staticmethod
    async def get_user_id(id):
        statement = select(User).where(User.id == id)
        user_db = await session.exec(statement)
        user = user_db.first()

        return user

class Playlist(Base):
    __tablename__ = "playlist"

    db_id: Mapped[UUID]= mapped_column(primary_key=True, unique=True, default=uuid1)
    owner_id : Mapped[UUID]= mapped_column(nullable=False)
    host_ids : Mapped[MutableList] = mapped_column(MutableList.as_mutable(PickleType), default=[])
    updated: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=text('now()'), nullable=False)
    title : Mapped[str] = mapped_column()

    def as_dict(self):
        return self.__dict__

    def as_data(self):
        return {f"db_id":self.db_id, "path" : self.path}

    @property
    def path(self):
        return f"/playlist/{self.db_id}"
    
    def get_videos(self):
        videos = [""] * len(self.host_ids)
        i = 0
        
        while i < len(self.host_ids):     
            videos[i] = self.host_ids[i]
            i = i + 1
        return videos

    @staticmethod
    async def get_list_playlists():

        statement = select (Playlist)
        playlist_db = await session.exec(statement)
        playlist_list = playlist_db.all()

        return playlist_list    

class WatchEvent(Base):
    __tablename__ = "events"

    host_id : Mapped[str] = mapped_column(primary_key=True) # 0 es ASC
    event_id : Mapped[datetime]= mapped_column(DateTime(timezone=True), primary_key=True, 
                                               sort_order=0, default=text('now()'))
    owner_id : Mapped[UUID]= mapped_column(primary_key=True, nullable=False)
    path : Mapped[str] = mapped_column(nullable=False)
    start_time : Mapped[float] = mapped_column(nullable=False)
    end_time : Mapped[float] = mapped_column(nullable=False)
    duration : Mapped[float] = mapped_column(nullable=False)
    complete : Mapped[bool] = mapped_column(default=False)

    @property
    def completed(self):
        return (self.duration *0.97) < self.end_time


class Video(Base):
    __tablename__ = "videos"

    db_id: Mapped[UUID]= mapped_column(unique=True, default=uuid1)
    host_service: Mapped[str] = mapped_column(default="youtube", nullable=False)#youtube, vimeo...
    host_id: Mapped[str] = mapped_column(primary_key=True, nullable=False)
    url: Mapped[str] = mapped_column(nullable=False)
    title : Mapped[str] = mapped_column(nullable=False)
    owner_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), 
                                          nullable=False)#Cascade que pasa con el post cuando el user 
                                                         # es eliminado
    owner = relationship("User")

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return f"Video(title={self.title}, host_id={self.host_id}, owner_id={self.owner_id})"

    def render(self):  # Front end uses
        basename = self.host_service #youtube, vimeo...
        template_name = f"videos/renderers/{basename}.html"
        context = {"host_id" : self.host_id}
        t = templates.get_template(template_name)
        return t.render(context)

    def as_data(self):
        return {f"{self.host_service}":{self.host_id}, "path" : self.path, "title" : self.title}
    
    def as_dict(self):
        return self.__dict__

    @property #al ser property no se llama como function
    def path(self):
        return f"/videos/{self.host_id}"
    
    @staticmethod
    async def get(host_id):

        statement = select (Video).where(Video.host_id == host_id)
        video_db = await session.exec(statement)
        video = video_db.first()

        return video
    
    @staticmethod
    async def get_list_videos():

        statement = select (Video)
        video_db = await session.exec(statement)
        video_list = video_db.all()

        return video_list
    


    


