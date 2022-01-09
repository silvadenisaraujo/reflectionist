import configparser
from dataclasses import dataclass, is_dataclass, asdict
from datetime import datetime
import json

from pathlib import Path
from typing import List, NamedTuple

from reflectionist import DB_READ_ERROR, DB_WRITE_ERROR, JSON_ERROR, SUCCESS

DEFAULT_DB_FILE_PATH = Path.home().joinpath(
    "." + Path.home().stem + "_reflections.json"
)


@dataclass
class Reflection:
    created_at: str
    happened: str
    feeling: str
    learned: str


class CurrentReflection(NamedTuple):
    reflection: Reflection
    return_code: int


def get_database_path(config_file: Path) -> Path:
    """Return the current path to the reflections database."""
    config_parser = configparser.ConfigParser()
    config_parser.read(config_file)
    return Path(config_parser["General"]["database"])


def init_database(db_path: Path) -> int:
    """Create the reflections database."""
    try:
        db_path.write_text("[]")  # Empty reflections list
        return SUCCESS
    except OSError:
        return DB_WRITE_ERROR


@dataclass
class DBResponse:
    reflections: List[Reflection]
    return_code: int


class DataclassJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if is_dataclass(o):
            return asdict(o)
        return super().default(o)


class DatabaseHandler:
    def __init__(self, db_path: Path) -> None:
        self._db_path = db_path

    def read(self) -> DBResponse:
        try:
            with self._db_path.open("r") as db:
                try:
                    return DBResponse(json.load(db), SUCCESS)
                except json.JSONDecodeError:
                    return DBResponse([], JSON_ERROR)
        except OSError:
            return DBResponse([], DB_READ_ERROR)

    def write(self, reflections: List[Reflection]) -> DBResponse:
        try:
            with self._db_path.open("w") as db:
                json.dump(reflections, db, indent=4, cls=DataclassJSONEncoder)
            return DBResponse(reflections, SUCCESS)
        except OSError:
            return DBResponse(reflections, DB_WRITE_ERROR)
