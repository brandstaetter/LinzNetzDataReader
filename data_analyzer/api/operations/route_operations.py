import logging
import os
import tempfile
from os import path
from typing import List, Optional

import aiofiles
from api.response_model import Message
from fastapi import APIRouter, File, Request, Response, UploadFile
from fastapi.templating import Jinja2Templates
from service.data_services import is_persist_csv

templates = Jinja2Templates(directory=path.abspath(path.join(path.dirname(__file__), "..", "..", "templates")))
operations_router = APIRouter()


@operations_router.post("/api/upload-file")
async def process_upload_file(file: UploadFile = File(...)) -> Message:
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
async def process_upload_files(files: List[UploadFile] = File(...)) -> Message:
    result, success = await _upload_files(files)
    if result is not None:
        return Message(
            success=success,
            filenames=[k for k, v in result.items() if v],
            problems=[k for k, v in result.items() if not v],
            message="Files processed successfully." if success else "There were some problems!",
        )
    return Message(success=False, message="No files provided")


@operations_router.post("/do/upload-files")
async def do_upload_files(request: Request, files: List[UploadFile] = File(...)) -> Response:
    result, success = await _upload_files(files)
    if result is None:
        return templates.TemplateResponse(
            "general_pages/upload.html",
            context={
                "request": request,
                "result": True,
                "success": success,
                "filenames": "unknown",
                "problems": "unknown",
                "message": "No files selected!",
            },
        )
    return templates.TemplateResponse(
        "general_pages/upload.html",
        context={
            "request": request,
            "result": True,
            "success": success,
            "filenames": [k for k, v in result.items() if v],
            "problems": [k for k, v in result.items() if not v],
            "message": "Files processed successfully." if success else "There were some problems!",
        },
    )


async def _upload_files(files: List[UploadFile]) -> tuple[Optional[dict], bool]:
    result = {}
    for file in files:
        if file.filename == "":
            return None, False
        destination_file_path = os.path.join(tempfile.gettempdir(), file.filename)  # output file path
        async with aiofiles.open(destination_file_path, "wb") as out_file:
            while content := await file.read(1024):  # async read file chunk
                if isinstance(content, str):
                    await out_file.write(content.encode("utf-8"))
                else:
                    await out_file.write(content)  # async write file chunk
        result[file.filename] = is_persist_csv(file.filename, destination_file_path)

    success = len([k for k, v in result.items() if not v]) == 0
    return result, success
