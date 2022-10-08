import logging
import os.path
import tempfile
from typing import List, Union

import aiofiles
import matplotlib.pyplot as plt
import pandas as pd
import uvicorn
from api.general_pages.route_frontend import general_pages_router
from api.table_definition import CONSUMPTION, ENDDATE, FALLBACK, STARTDATE
from db.session import engine
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from util import csv_reader
from util.database_helper import table_from_filename

# general setup and base configuration

# FastAPI
app = FastAPI()
app.include_router(general_pages_router)
app.mount("/static", StaticFiles(directory="data_analyzer/static"), name="static")


class Message(BaseModel):
    message: str
    filenames: List = []


# @app.get("/", response_model=Message)
# async def root() -> Message:
#    logging.debug("Hello Log!")
#    return Message(message="Hello World")


@app.post("/upload-file")
async def create_upload_file(file: UploadFile = File(...)) -> FileResponse:
    logging.debug("filename = %s", file.filename)  # getting filename
    destination_file_path = os.path.join(tempfile.gettempdir(), file.filename)  # location to store file
    async with aiofiles.open(destination_file_path, "wb") as out_file:
        while content := await file.read(1024):  # async read file chunk
            if isinstance(content, str):
                await out_file.write(content.encode("utf-8"))
            else:
                await out_file.write(content)  # async write file chunk

    with engine.connect() as con:
        table_name = table_from_filename(file.filename)

        original_frame: pd.DataFrame = None
        if engine.has_table(table_name):
            original_frame = pd.read_sql_table(
                table_name,
                con=engine,
                index_col=STARTDATE,
                parse_dates=[STARTDATE, ENDDATE],
                columns=[STARTDATE, ENDDATE, CONSUMPTION, FALLBACK],
            )
            # original_frame.set_index(startdate, drop=False)
            logging.info(original_frame.dtypes)
            logging.debug(original_frame.head())

        fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(10, 20))
        new_frame = csv_reader.parse(destination_file_path)
        if original_frame is None:
            frame = new_frame
        elif not new_frame[ENDDATE].isin(original_frame[ENDDATE].values).any():
            frame = original_frame.concat(new_frame)
        else:
            logging.warning("Duplicate dataset uploaded!")
            frame = original_frame
        frame.to_sql(table_name, con, if_exists="replace")

    logging.info(frame.dtypes)
    logging.debug(frame.head())
    frame_hourly = frame.resample("h").sum()
    frame[CONSUMPTION].plot(ax=axes[0], kind="bar", xlabel="Datetime", ylabel="kWh")
    frame_hourly[CONSUMPTION].plot(ax=axes[1], kind="bar", xlabel="Datetime", ylabel="kWh")
    result_filepath = os.path.join(tempfile.gettempdir(), "plot1.png")
    fig.tight_layout()
    fig.savefig(result_filepath)
    return FileResponse(result_filepath)


@app.post("/api/upload-files")
async def create_upload_files(files: List[UploadFile] = File(...)) -> Union[Message, FileResponse]:
    # OPENTODO check for unique filenames
    file_count: int = len(files)
    fig, axes = plt.subplots(nrows=file_count, ncols=1, figsize=(file_count * 15, file_count * 10))
    total_frame: pd.DataFrame = None
    for file in files:
        destination_file_path = os.path.join(tempfile.gettempdir(), file.filename)  # output file path
        async with aiofiles.open(destination_file_path, "wb") as out_file:
            while content := await file.read(1024):  # async read file chunk
                if isinstance(content, str):
                    await out_file.write(content.encode("utf-8"))
                else:
                    await out_file.write(content)  # async write file chunk
        if total_frame is None:
            total_frame = csv_reader.parse(destination_file_path)
        else:
            total_frame = total_frame.concat(csv_reader.parse(destination_file_path))

    if total_frame is not None:
        logging.info(total_frame.dtypes)
        logging.debug(total_frame.head())
        frame_hourly = total_frame.resample("h").sum()
        frame_daily = total_frame.resample("d").sum()
        frame_daily[CONSUMPTION].plot(ax=axes[0], kind="bar", xlabel="Datetime", ylabel="kWh")
        frame_hourly[CONSUMPTION].plot(ax=axes[1], kind="bar", xlabel="Datetime", ylabel="kWh")
        result_filepath = os.path.join(tempfile.gettempdir(), "plot1.png")
        fig.tight_layout()
        fig.savefig(result_filepath)
        return FileResponse(result_filepath)
    return Message(message="Failure", filenames=[file.filename for file in files])


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger("main")
    logging.info("uvicorn is running")
    logging.debug("It's corn!")
    uvicorn.run(app, host="127.0.0.1", port=8005)
