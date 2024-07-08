import json
from pydantic import BaseModel, ValidationError
from sqlmodel.ext.asyncio.session import AsyncSession
#from app.db.schemas_videos import MySessionVideo
#from app.db.schemas_users import MySessionUser

async def schema_or_error(raw_data: dict, db:AsyncSession, SchemaModel:BaseModel, BaseSession):

    data: dict = {}
    error: list = []
    error_str: str = None
    
    try:  #cleaned_data = SchemaModel(**raw_data)
        data = await BaseSession(db).my_validation(raw_data, SchemaModel) #SchemaModel(**raw_data)
        
    except ValidationError as e:
        error_str = e.json()

    except ValueError as e:
        error = e.args
        
    if error_str is not None or len(error) > 0:
        try:
            error = json.loads(str(error_str))
        except ValueError as e:
            error= [{"msg": error[0]}]
        except Exception as e:
            error: [{"msg" : "Unknown error"}]
    return data, error
'''
async def users_schema_or_error(raw_data: dict, SchemaModel:BaseModel, db:AsyncSession):

    data: dict = {}
    error: list = []
    error_str: str = None

    try:  #cleaned_data = SchemaModel(**raw_data)
        data = await MySessionUser(db).my_users_validation(SchemaModel, raw_data) #SchemaModel(**raw_data)
        
    except ValidationError as e:
        error_str = e.json()
    except ValueError as e:
        error = e.args

    if error_str is not None or len(error) > 0:
        try:
            error = json.loads(str(error_str))
        except ValueError as e:
            error= [{"msg": error[0]}]
        except Exception as e:
            error: [{"msg":"Unknown error"}]
    return data, error
'''





