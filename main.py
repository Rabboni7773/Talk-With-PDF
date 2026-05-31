from fastapi import Request, FastAPI, UploadFile, File
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

templates = Jinja2Templates(directory="/home/rabboni/Desktop/talk_with_pdf/templates")


@app.get("/")
def main_page(request : Request):
    return templates.TemplateResponse(request, name="index.html")

@app.post("/upload")
async def file_upload(request : Request, file : UploadFile = File(...)):
    os.makedirs("/home/rabboni/Desktop/talk_with_pdf/data/files", exist_ok=True)


    file_location = f"/home/rabboni/Desktop/talk_with_pdf/data/files/{file.filename}"


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


async def response_generator(user_query: str):
    full_text = rag.retrive(user_query)
    for word in full_text.split(" "):
        yield f"{word} "
        await asyncio.sleep(0.09)

@app.post("/chat/retrive")
async def retriving(data: ChatQuery):
    return StreamingResponse(response_generator(data.query), media_type="text/event-stream")
