import pandas as pd
from numpy import NaN

from data_analyzer.api.table_definition import CONSUMPTION, DATE, ENDDATE, FALLBACK
from data_analyzer.service.util.database_helper import D_TABLE_NAME, QH_TABLE_NAME

CONSUMPTION_ALT = "Energiemenge in kWh"
STARTDATE = "Datum von"


def parse_float(value_string: str) -> float:
    return float(value_string.replace(",", ".")) if len(value_string.strip()) > 0 else NaN


def parse(destination_file_path: str, table_name: str) -> pd.DataFrame:
    if table_name == QH_TABLE_NAME:
        frame = pd.read_csv(
            destination_file_path,
            parse_dates=[STARTDATE, ENDDATE],
            dayfirst=True,
            sep=";",
            converters={CONSUMPTION: parse_float, FALLBACK: parse_float, CONSUMPTION_ALT: parse_float},
        )
        frame.rename(columns={STARTDATE: DATE}, inplace=True)
        frame.set_index(DATE, inplace=True)
    elif table_name == D_TABLE_NAME:
        frame = pd.read_csv(
            destination_file_path,
            parse_dates=[DATE],
            dayfirst=True,
            sep=";",
            converters={CONSUMPTION: parse_float, FALLBACK: parse_float, CONSUMPTION_ALT: parse_float},
            index_col=DATE,
        )
    if CONSUMPTION_ALT in frame.columns:
        frame.rename(columns={CONSUMPTION_ALT: CONSUMPTION}, inplace=True)
    return frame
