from pydantic import BaseModel, Field, field_validator, model_validator
from uuid import UUID
from typing import Optional


class VideoIndex(BaseModel):
    objectID : str = Field(alias='host_id')
    title : Optional[str]
    path : str = Field(alias="host_id")
    objectType: str = "Video"

    @field_validator("path")
    @classmethod
    def set_path(cls, value):
        host_id = value
        return f"/videos/{host_id}"
    

class PlaylistIndex(BaseModel):
    objectID : UUID = Field(alias='db_id')
    title : Optional[str]
    path : str = Field(default="/")
    objectType: str = "Playlist"

    @model_validator(mode='after')
    def set_defaults(self):
        self.objectID = str(self.objectID)
        self.path = f"/playlist/{self.objectID}"
        return self


