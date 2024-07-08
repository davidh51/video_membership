from fastapi import APIRouter, Depends, Request
from sqlmodel import select
from app.db.models import WatchEvent
from sqlmodel.ext.asyncio.session import AsyncSession
from app.db.database import get_session
from uuid import UUID
from app.db.schemas_watch_event import WatchEventSchema


router = APIRouter(prefix="/api/events/watch")  ##'/watch-event')

# json.dumps()  -> jsonstr
# json.load(jsonstr) -> dict    

@router.post("/", response_model=WatchEventSchema)   #data : dict
async def watch_event_view(request:Request, watch_event: WatchEventSchema, db:AsyncSession=Depends(get_session)): 
                                            #data : dict,str = Form(...)                                                     
    if request.user.is_authenticated:

        data = watch_event.dict()
        data.update({"owner_id" : UUID(request.user.username)})
        new_event = WatchEvent(**data)

        db.add(new_event) 
        await db.commit()
        await db.refresh(new_event)
  
    return data #{"working" : True}