import logging

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from data_analyzer.api.general_pages.route_frontend import general_pages_router
from data_analyzer.api.operations.route_graph import graph_router
from data_analyzer.api.operations.route_operations import operations_router

# general setup and base configuration

# FastAPI
app = FastAPI()
app.include_router(general_pages_router)
app.include_router(operations_router)
app.include_router(graph_router)
app.mount("/static", StaticFiles(directory="data_analyzer/static"), name="static")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, filename="data_analyzer.log")
    uvicorn.run(app, host="127.0.0.1", port=8005)
