import logging
import os
import tempfile
from os import path
from typing import List

import aiofiles
from api.response_model import Message
from fastapi import APIRouter, File, UploadFile
from fastapi.templating import Jinja2Templates
from service.data_services import is_persist_csv

templates = Jinja2Templates(directory=path.abspath(path.join(path.dirname(__file__), "..", "..", "templates")))
operations_router = APIRouter()


@operations_router.post("/api/upload-file")
async def create_upload_file(file: UploadFile = File(...)) -> Message:
    logging.debug("processing file: %s", file.filename)  # getting filename
    destination_file_path = os.path.join(tempfile.gettempdir(), file.filename)  # location to store file
    async with aiofiles.open(destination_file_path, "wb") as out_file:
        while content := await file.read(1024):  # async read file chunk
            if isinstance(content, str):
                await out_file.write(content.encode("utf-8"))
            else:
                await out_file.write(content)  # async write file chunk

    success = is_persist_csv(file.filename, destination_file_path)
    return Message(
        success=success,
        filenames=[file.filename],
        message="File processed successfully." if success else "There was a problem processing the file.",
    )


@operations_router.post("/api/upload-files")
async def create_upload_files(files: List[UploadFile] = File(...)) -> Message:
    filtered_list = list(set(files))
    logging.debug("Processing files: %s", filtered_list)
    result = {}
    for file in filtered_list:
        destination_file_path = os.path.join(tempfile.gettempdir(), file.filename)  # output file path
        async with aiofiles.open(destination_file_path, "wb") as out_file:
            while content := await file.read(1024):  # async read file chunk
                if isinstance(content, str):
                    await out_file.write(content.encode("utf-8"))
                else:
                    await out_file.write(content)  # async write file chunk
        result[file.filename] = is_persist_csv(file.filename, destination_file_path)

    success = len([k for k, v in result.items() if not v]) == 0
    return Message(
        success=success,
        filenames=[k for k, v in result.items() if v],
        problems=[k for k, v in result.items() if not v],
        message="Files processed successfully." if success else "There were some problems!",
    )
