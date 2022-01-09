from datetime import datetime
from pathlib import Path
from typing import List
from reflectionist import DB_READ_ERROR, SUCCESS
from uuid import uuid4

from reflectionist.database import CurrentReflection, DatabaseHandler, Reflection


class ReadException(Exception):
    pass


class Service:
    def __init__(self, db_path: Path) -> None:
        self._db_handler = DatabaseHandler(db_path)

    def add(self, happened: str, felt: str, learned: str) -> CurrentReflection:
        reflection = Reflection(str(datetime.utcnow()), happened, felt, learned)
        read = self._db_handler.read()
        if read.return_code == DB_READ_ERROR:
            return CurrentReflection(reflection, read.return_code)
        read.reflections.insert(0, reflection)
        write = self._db_handler.write(read.reflections)
        return CurrentReflection(reflection, write.return_code)

    def get(self) -> List[Reflection]:
        read = self._db_handler.read()
        return read.reflections

    def describe(self, id: int) -> Reflection:
        response = self._db_handler.read()
        if response.return_code != SUCCESS:
            raise ReadException(
                f"Could not read reflections, error: {response.return_code}"
            )
        if id < 0 or id >= len(response.reflections):
            raise IndexError(f"Reflection with id {id} does not exist.")
        return response.reflections[id]
