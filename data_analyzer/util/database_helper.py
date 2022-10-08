def table_from_filename(filename: str) -> str:
    if filename.find("_QH_") > 0:
        return "data_qh"
    if filename.find("_D_") > 0:
        return "data_d"
    return "trash"
