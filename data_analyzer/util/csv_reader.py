import pandas as pd
from numpy import NaN


def parse_float(value_string: str) -> float:
    return float(value_string.replace(",", ".")) if value_string != "" else NaN


def parse(destination_file_path: str) -> pd.DataFrame:
    frame = pd.read_csv(
        destination_file_path,
        parse_dates=["Datum von", "Datum bis"],
        dayfirst=True,
        sep=";",
        converters={"Verbrauch in kWh": parse_float, "Ersatzwert": parse_float},
        index_col="Datum von",
    )
    return frame
