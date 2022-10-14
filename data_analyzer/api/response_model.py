from typing import List

from pydantic import BaseModel


class Message(BaseModel):
    message: str = ""
    filenames: List[str] = []
    problems: List[str] = []
    success: bool
