QH_TABLE_NAME = "data_qh"
D_TABLE_NAME = "data_d"


def table_from_filename(filename: str) -> str:
    if filename.find("_QH_") > 0:
        return QH_TABLE_NAME
    if filename.find("_D_") > 0:
        return D_TABLE_NAME
    return "trash"
