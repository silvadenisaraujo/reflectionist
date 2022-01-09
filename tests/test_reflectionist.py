import pytest
import json

from reflectionist import SUCCESS, __version__
from typer.testing import CliRunner
from datetime import datetime
from reflectionist import __app_name__, __version__, cli
from reflectionist.service import Service

runner = CliRunner()

MOCKED_REFLECTIONS = [
    {
        "created_at": str(datetime.utcnow()),
        "happened": "I was a dog",
        "felt": "I was a cat",
        "learned": "I was a mouse",
    }
]


def test_version():
    result = runner.invoke(cli.app, ["--version"])
    assert result.exit_code == 0
    assert f"{__app_name__} v{__version__}\n" in result.stdout


@pytest.fixture
def mock_json_file(tmp_path):
    db_file = tmp_path / "reflection.json"
    with db_file.open("w") as db:
        json.dump(MOCKED_REFLECTIONS, db, indent=4)
    return db_file


def test_add(mock_json_file):
    service = Service(db_path=mock_json_file)
    added = service.add(
        happened="I was a dog", felt="I was a cat", learned="I was a mouse"
    )
    assert added.return_code == SUCCESS
    reflections = service.get()
    assert len(reflections) == 2


def test_list(mock_json_file):
    service = Service(db_path=mock_json_file)
    reflections = service.get()
    assert len(reflections) == 1


def test_successfull_describe(mock_json_file):
    service = Service(db_path=mock_json_file)
    reflection = service.describe(0)
    assert reflection["happened"] == MOCKED_REFLECTIONS[0]["happened"]


def test_error_describe(mock_json_file):
    service = Service(db_path=mock_json_file)
    with pytest.raises(IndexError):
        service.describe(1000)
