import pandas as pd
from api.table_definition import CONSUMPTION, ENDDATE, FALLBACK, STARTDATE
from numpy import NaN


def parse_float(value_string: str) -> float:
    return float(value_string.replace(",", ".")) if value_string != "" else NaN


def parse(destination_file_path: str) -> pd.DataFrame:
    frame = pd.read_csv(
        destination_file_path,
        parse_dates=[STARTDATE, ENDDATE],
        dayfirst=True,
        sep=";",
        converters={CONSUMPTION: parse_float, FALLBACK: parse_float},
        index_col=STARTDATE,
    )
    return frame
