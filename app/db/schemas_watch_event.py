from pydantic import BaseModel
from typing import Optional
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, desc
from app.db.models import WatchEvent

class MySessionEvent():

    def __init__(self, session:AsyncSession):
        self.session = session
    
    async def get_resume_video(self, host_id, user_id):

        resume_time = 0
        statement = select(WatchEvent).where(WatchEvent.host_id == host_id,
                    WatchEvent.owner_id == user_id).order_by(desc(WatchEvent.event_id))
        user_db = await self.session.exec(statement)
        user = user_db.first()

        if user is not None:

            if not user.completed:

                resume_time = user.end_time
        
        return resume_time


class WatchEventSchema(BaseModel):

    host_id : str
    path : Optional[str]
    start_time : float
    end_time :float
    duration :float
    complete : bool
