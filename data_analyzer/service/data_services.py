import logging

import pandas as pd
from api.table_definition import CONSUMPTION, DATE, ENDDATE, FALLBACK
from db.session import engine, insp
from service.util.csv_reader import parse
from service.util.database_helper import D_TABLE_NAME, QH_TABLE_NAME, table_from_filename


def is_persist_csv(filename: str, csv_file_path: str) -> bool:
    with engine.connect() as con:
        success = False
        table_name = table_from_filename(filename)
        logging.debug("Resolved table name to save to as %s for file %s", table_name, filename)
        original_frame = get_frame(table_name)
        new_frame = parse(csv_file_path, table_name)
        if original_frame is None:
            logging.debug("No previous data found, creating new table")
            frame = new_frame
            success = True
        elif not pd.Series(new_frame.index.values).isin(original_frame.index.values).any():
            logging.debug("Adding new data to table")
            # using concat instead of just apending to keep data sorted
            frame = pd.concat([original_frame, new_frame], sort=True, join="inner")
            success = True
        else:
            logging.warning("Duplicate/overlapping dataset in %s uploaded! Will not be stored.", filename)
            frame = original_frame
        logging.debug("Writing table with the following columns: %s", frame.dtypes)
        frame.to_sql(table_name, con, if_exists="replace")
        return success


def get_frame(table_name: str) -> pd.DataFrame:
    original_frame: pd.DataFrame = None
    if insp.has_table(table_name):
        if table_name == QH_TABLE_NAME:
            original_frame = pd.read_sql_table(
                table_name,
                con=engine,
                index_col=DATE,
                parse_dates=[DATE, ENDDATE],
                columns=[DATE, ENDDATE, CONSUMPTION, FALLBACK],
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
