from fastapi import Request, FastAPI, UploadFile, File
from fastapi.exceptions import HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import asyncio
import os
import shutil
from pydantic import BaseModel
from utils.rag_system import RAGSystem



app = FastAPI()
app.add_middleware(
    CORSMiddleware, 
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"]
)

templates = Jinja2Templates(directory="/app/templates")


@app.get("/")
def main_page(request : Request):
    return templates.TemplateResponse(request, name="index.html")

@app.post("/upload")
async def file_upload(request : Request, file : UploadFile = File(...)):
    contents = await file.read()
    MAX_SIZE = 5 * 1024 * 1024

    if len(contents) > MAX_SIZE:
        raise HTTPException(
            status_code=400,
            detail="file size excedded limit is 5MB !"
        )

    if not file.filename.endswith(".pdf"):
        raise HTTPException(
            status_code= 400,
            detail= "file is not in pdf format!"
        )
    os.makedirs("/app/file_storage", exist_ok=True)


    file_location = f"/app/file_storage/{file.filename}"


    file.file.seek(0)

    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    responce = {"message" : "File Upload Sucessful", "code" : 200}
     
    return responce

rag = RAGSystem()

@app.get("/chat")
async def chat(request : Request):
    rag.create_vec_store()
    return templates.TemplateResponse(request, name = "n_chat.html")


class ChatQuery(BaseModel):
    query: str
    sessionId : str


async def response_generator(user_query: str, session_id : str):
    full_text = rag.retrive(user_query, session_id)
    for word in full_text.split(" "):
        yield f"{word} "
        await asyncio.sleep(0.07)

@app.post("/chat/retrive")
async def retriving(data: ChatQuery):
    return StreamingResponse(response_generator(data.query, data.sessionId), media_type="text/event-stream")
