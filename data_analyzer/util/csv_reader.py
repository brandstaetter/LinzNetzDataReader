import pandas as pd
from api.table_definition import CONSUMPTION, DATE, ENDDATE, FALLBACK, STARTDATE
from numpy import NaN
from util.database_helper import D_TABLE_NAME, QH_TABLE_NAME


def parse_float(value_string: str) -> float:
    return float(value_string.replace(",", ".")) if value_string != "" else NaN


def parse(destination_file_path: str, table_name: str) -> pd.DataFrame:
    if table_name == QH_TABLE_NAME:
        frame = pd.read_csv(
            destination_file_path,
            parse_dates=[STARTDATE, ENDDATE],
            dayfirst=True,
            sep=";",
            converters={CONSUMPTION: parse_float, FALLBACK: parse_float},
            index_col=STARTDATE,
        )
    elif table_name == D_TABLE_NAME:
        frame = pd.read_csv(
            destination_file_path,
            parse_dates=[DATE],
            dayfirst=True,
            sep=";",
            converters={CONSUMPTION: parse_float, FALLBACK: parse_float},
            index_col=DATE,
        )
    return frame
