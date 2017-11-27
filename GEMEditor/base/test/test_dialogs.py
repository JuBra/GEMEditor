import pandas as pd
from GEMEditor.base.dialogs import DataFrameDialog


class TestDataFrameDialog:

    def test_display_of_dataframe(self):
        df = pd.DataFrame({"A": 1, "B": 2}, index=["Value"])
        df.sort_index(axis=1, inplace=True)
        dialog = DataFrameDialog(df)

        assert dialog.datatable.rowCount() == 1
        assert dialog.datatable.columnCount() == 2
        assert dialog.datatable.horizontalHeaderItem(0).text() == "A"
        assert dialog.datatable.horizontalHeaderItem(1).text() == "B"
        assert dialog.datatable.verticalHeaderItem(0).text() == "Value"
