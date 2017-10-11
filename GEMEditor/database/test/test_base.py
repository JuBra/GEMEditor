import pytest
from GEMEditor.database.base import DatabaseWrapper, valid_database
from GEMEditor.database.tables import setup_empty_database
from GEMEditor.database import miriam_databases


@pytest.fixture()
def database(tmpdir_factory):
    temp_path = str(tmpdir_factory.mktemp('db').join("database.db"))
    setup_empty_database(database_path=temp_path)
    return temp_path


@pytest.fixture()
def empty_file(tmpdir_factory):
    temp_path = str(tmpdir_factory.mktemp('db').join("database.db"))
    open(temp_path, "a").close()
    return temp_path


class TestDatabaseWrapper:

    def test_setup_no_database_file(self):
        with pytest.raises(FileNotFoundError):
            DatabaseWrapper("")

    def test_setup_empty_datase(self, database):
        wrapper = DatabaseWrapper(database)




