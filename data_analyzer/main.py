import logging
import os.path
from typing import List

import aiofiles
import uvicorn
from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel

app = FastAPI()


class Message(BaseModel):
    message: str
    filenames: List = []


@app.get("/", response_model=Message)
async def root() -> Message:
    logging.debug("Hello Log!")
    return Message(message="Hello World")


@app.post("/upload-file")
async def create_upload_file(file: UploadFile = File(...)) -> Message:
    logging.debug("filename = %s", file.filename)  # getting filename
    destination_file_path = os.path.join("~", file.filename)  # location to store file
    async with aiofiles.open(destination_file_path, "wb") as out_file:
        while content := await file.read(1024):  # async read file chunk
            if isinstance(content, str):
                await out_file.write(content.encode("utf-8"))
            else:
                await out_file.write(content)  # async write file chunk

    return Message(message="OK")


@app.post("/upload-files")
async def create_upload_files(files: List[UploadFile] = File(...)) -> Message:
    # OPENTODO check for unique filenames
    for file in files:
        destination_file_path = os.path.join("/home/abc/videos/", file.filename)  # output file path
        async with aiofiles.open(destination_file_path, "wb") as out_file:
            while content := await file.read(1024):  # async read file chunk
                if isinstance(content, str):
                    await out_file.write(content.encode("utf-8"))
                else:
                    await out_file.write(content)  # async write file chunk
    return Message(message="OK", filenames=[file.filename for file in files])


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8005)
    logging.info("uvicorn is running")
    logging.debug("It's corn!")
