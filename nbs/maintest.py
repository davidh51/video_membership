from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import json  
from fastapi.responses import JSONResponse

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:8080",
]

app.add_middleware( #permite ingresar desde un domain diferente como google y no solo desde 127.0...8000
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#@app.post("/watch-event")
#def watch_event_view(data:dict):

#    print (data)

#    return {"working" : True}
    

@app.post("/watch-event")
async def post_record(data: str = Body(...)):
    try:
        parsed_data = json.loads(data)
# Attempt to parse the incoming JSON data
        print(parsed_data)
        
        return JSONResponse(content=parsed_data, status_code=200)
    
    except json.JSONDecodeError as e:
        print ("Raw", data)
        raise HTTPException(status_code=400, detail=str(e))
# Log the raw data when a JSON decode error occurs
        



