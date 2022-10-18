import logging
import os
import tempfile

import matplotlib.dates as mdates
import numpy as np
from api.table_definition import CONSUMPTION
from fastapi import APIRouter
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
from pandas import DataFrame
from service.data_services import get_frame
from service.util.database_helper import D_TABLE_NAME, QH_TABLE_NAME

templates = Jinja2Templates(directory=os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "templates")))
graph_router = APIRouter()


@graph_router.get("/api/graph")
async def get_graph(source: str, aggregate: str = "", step: int = 4, lower: str = "", upper: str = "") -> FileResponse:
    logging.debug("Rendering graph with source %s, step %d, lower '%s', upper '%s'")
    frame = None
    if source == "qh":
        frame = get_frame(QH_TABLE_NAME)
    elif source == "d":
        frame = get_frame(D_TABLE_NAME)
    else:
        raise ValueError("Unknown value for source")
    if frame is not None:
        result_filepath = os.path.join(tempfile.gettempdir(), "plot_" + source + ".png")
        if os.path.exists(result_filepath):
            os.remove(result_filepath)

        if lower != "" and upper != "":
            frame = frame.loc[lower:upper]  # type: ignore [misc]
        elif lower != "" and upper == "":
            frame = frame.loc[lower:]  # type: ignore [misc]
        elif lower == "" and upper != "":
            frame = frame.loc[:upper]  # type: ignore [misc]

        width = max(frame.size / 30 if source == "d" else frame.size / 100, 10)
        height = 5.0

        if aggregate in ["h", "d", "w", "m"]:
            frame = frame.resample(aggregate).sum(numeric_only=True)
        _persist_plot(step, frame, result_filepath, width, height)
        return FileResponse(result_filepath)
    raise FileNotFoundError("Data not found, please upload.")


def _persist_plot(step: int, frame: DataFrame, result_filepath: str, width: float, height: float) -> None:
    # Draw pandas plot: x_compat=True converts the pandas x-axis units to matplotlib
    # date units (not strictly necessary when using a daily frequency like here)
    axes = frame[CONSUMPTION].plot(x_compat=True, figsize=(width, height), legend=None, ylabel="kWh")
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
    axes.xaxis.set_major_formatter(mdates.DateFormatter("\n%b %y"))
    axes.xaxis.set_minor_formatter(mdates.DateFormatter("%d"))

    axes.grid(visible=True, axis="y", which="major")

    # Additional formatting
    axes.figure.autofmt_xdate(rotation=0, ha="center")
    title = "Verbrauch"
    axes.set_title(title, pad=20, fontsize=14)

    axes.figure.tight_layout()

    axes.figure.savefig(result_filepath)
    axes.clear()
    axes.figure.clear()
