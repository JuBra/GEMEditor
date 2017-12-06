import pandas as pd
from GEMEditor.base.dialogs import DataFrameDialog
from PyQt5.QtWidgets import QApplication


# Make sure to only start an application
# if there is no active one. Opening multiple
# applications will lead to a crash.
app = QApplication.instance()
if app is None:
    app = QApplication([])


class TestDataFrameDialog:

    def test_display_of_dataframe(self):
        df = pd.DataFrame({"A": 1, "B": 2}, index=["Value"])
        df.sort_index(axis=1, inplace=True)
        dialog = DataFrameDialog(df)

        assert dialog.datatable.rowCount() == 1
        assert dialog.datatable.columnCount() == 3
        assert dialog.datatable.horizontalHeaderItem(0).text() == "Index"
        assert dialog.datatable.horizontalHeaderItem(1).text() == "A"
        assert dialog.datatable.horizontalHeaderItem(2).text() == "B"
