import logging
import os
import os.path
import tempfile
from typing import List, Union

import aiofiles
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
import uvicorn
from api.general_pages.route_frontend import general_pages_router
from api.table_definition import CONSUMPTION, DATE, ENDDATE, FALLBACK, STARTDATE
from db.session import engine, insp
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from util import csv_reader
from util.database_helper import D_TABLE_NAME, QH_TABLE_NAME, table_from_filename

# general setup and base configuration

# FastAPI
app = FastAPI()
app.include_router(general_pages_router)
app.mount("/static", StaticFiles(directory="data_analyzer/static"), name="static")


class Message(BaseModel):
    message: str = ""
    filenames: List[str] = []
    success: bool


def _persist_csv(filename: str, csv_file_path: str) -> None:
    with engine.connect() as con:
        table_name = table_from_filename(filename)
        logging.debug("Resolved table name to save to as %s for file %s", table_name, filename)
        original_frame = _get_frame(table_name)
        new_frame = csv_reader.parse(csv_file_path, table_name)
        if original_frame is None:
            logging.debug("No previous data found, creating new table")
            frame = new_frame
        elif (table_name == QH_TABLE_NAME and not new_frame[ENDDATE].isin(original_frame[ENDDATE].values).any()) or (
            table_name == D_TABLE_NAME and not pd.Series(new_frame.index.values).isin(original_frame.index.values).any()
        ):
            logging.debug("Adding new data to table")
            # using concat instead of just apending to keep data sorted
            frame = pd.concat([original_frame, new_frame], sort=True, join="inner")
        else:
            logging.warning("Duplicate/overlapping dataset in %s uploaded! Will not be stored.", filename)
            frame = original_frame
        logging.debug("Writing table with the following columns: %s", frame.dtypes)
        frame.to_sql(table_name, con, if_exists="replace")


def _get_frame(table_name: str) -> pd.DataFrame:
    original_frame: pd.DataFrame = None
    if insp.has_table(table_name):
        if table_name == QH_TABLE_NAME:
            original_frame = pd.read_sql_table(
                table_name,
                con=engine,
                index_col=STARTDATE,
                parse_dates=[STARTDATE, ENDDATE],
                columns=[STARTDATE, ENDDATE, CONSUMPTION, FALLBACK],
            )
        elif table_name == D_TABLE_NAME:
            original_frame = pd.read_sql_table(
                table_name,
                con=engine,
                index_col=DATE,
                parse_dates=[DATE],
                columns=[DATE, CONSUMPTION, FALLBACK],
            )
        logging.debug("Loaded the following data: %s", original_frame.dtypes)
        logging.debug("Data head: \n%s", original_frame.head())
    return original_frame


@app.post("/api/upload-file")
async def create_upload_file(file: UploadFile = File(...)) -> Message:
    logging.debug("processing file: %s", file.filename)  # getting filename
    destination_file_path = os.path.join(tempfile.gettempdir(), file.filename)  # location to store file
    async with aiofiles.open(destination_file_path, "wb") as out_file:
        while content := await file.read(1024):  # async read file chunk
            if isinstance(content, str):
                await out_file.write(content.encode("utf-8"))
            else:
                await out_file.write(content)  # async write file chunk

    _persist_csv(file.filename, destination_file_path)
    return Message(success=True, filenames=[file.filename], message="File processed successfully.")


@app.post("/api/upload-files")
async def create_upload_files(files: List[UploadFile] = File(...)) -> Message:
    filtered_list = list(set(files))
    logging.debug("Processing files: %s", filtered_list)
    for file in filtered_list:
        destination_file_path = os.path.join(tempfile.gettempdir(), file.filename)  # output file path
        async with aiofiles.open(destination_file_path, "wb") as out_file:
            while content := await file.read(1024):  # async read file chunk
                if isinstance(content, str):
                    await out_file.write(content.encode("utf-8"))
                else:
                    await out_file.write(content)  # async write file chunk
        _persist_csv(file.filename, destination_file_path)

    return Message(success=True, filenames=[file.filename for file in files], message="Files processed successfully.")


@app.get("/api/graph")
async def qh_graph(source: str, aggregate: str = "", step: int = 4) -> Union[FileResponse, Message]:
    frame = None
    if source == "qh":
        frame = _get_frame(QH_TABLE_NAME)
    elif source == "d":
        frame = _get_frame(D_TABLE_NAME)
    else:
        raise ValueError("Unknown value for source")
    if frame is not None:
        if aggregate == "h":
            frame = frame.resample("h").sum()
        if aggregate == "d":
            frame = frame.resample("d").sum()
        if aggregate == "m":
            frame = frame.resample("m").sum()
        result_filepath = os.path.join(tempfile.gettempdir(), "plot1.png")
        if os.path.exists(result_filepath):
            os.remove(result_filepath)
        # fig = frame[CONSUMPTION].plot(kind="bar", xlabel="Datetime", ylabel="kWh").get_figure()
        # fig.tight_layout()
        # fig.savefig(result_filepath)

        # Draw pandas plot: x_compat=True converts the pandas x-axis units to matplotlib
        # date units (not strictly necessary when using a daily frequency like here)
        # ax = frame[CONSUMPTION].plot(kind="bar", figsize=(10, 5), legend=None, ylabel="kWh")
        axes = frame[CONSUMPTION].plot(x_compat=True, figsize=(10, 5), legend=None, ylabel="kWh")

        axes.set_ylim(*axes.get_ylim())  # reset y limits to display highlights without gaps
        # Highlight weekends based on the x-axis units
        xmin, xmax = axes.get_xlim()
        days = np.arange(np.floor(xmin), np.ceil(xmax) + 2)
        weekends = [((dt.weekday() >= 5) | (dt.weekday() == 0)) for dt in mdates.num2date(days)]
        axes.fill_between(days, *axes.get_ylim(), where=weekends, facecolor="k", alpha=0.1)
        axes.set_xlim(xmin, xmax)  # set limits back to default values

        # Create appropriate ticks using matplotlib date tick locators and formatters
        axes.xaxis.set_major_locator(mdates.MonthLocator())
        axes.xaxis.set_minor_locator(mdates.MonthLocator(bymonthday=np.arange(0, 31, step=step)))
        axes.xaxis.set_major_formatter(mdates.DateFormatter("%d\n%b"))
        axes.xaxis.set_minor_formatter(mdates.DateFormatter("%d"))

        # Additional formatting
        axes.figure.autofmt_xdate(rotation=0, ha="center")
        title = "Verbrauch"
        axes.set_title(title, pad=20, fontsize=14)

        axes.figure.savefig(result_filepath)
        axes.clear()
        return FileResponse(result_filepath)
    return Message(success=False, message="No data found!")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, filename="data_analyzer.log")
    uvicorn.run(app, host="127.0.0.1", port=8005)
