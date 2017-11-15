from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItem, QStandardItemModel


class LinkedItem(QStandardItem):

    def __init__(self, text=None, link=None):
        if text is None:
            QStandardItem.__init__(self)
        else:
            QStandardItem.__init__(self, text)
        self.link = link


class ElementTable(QStandardItemModel):

    def __init__(self, *args):
        QStandardItemModel.__init__(self, *args)

    def set_header(self):
        self.setHorizontalHeaderLabels(self.header)

    @staticmethod
    def row_from_item(item):
        raise NotImplementedError

    def item_from_row(self, row_idx):
        """ Return the linked item of a table row"""
        return self.item(row_idx).link

    def update_row_from_item(self, item, row_index=None):
        """ Add an item to a table """
        row_data = self.row_from_item(item)
        if row_index is None or row_index >= self.rowCount():
            self.appendRow(row_data)
        else:
            self.update_row_from_rowdata(row_data, row_index)

    def update_row_from_rowdata(self, row_data, row_index):
        """ Updates the the table row at row_index
        using the given item """
        for i, element in enumerate(row_data):
            self.setItem(row_index, i, element)

    def clear_information(self):
        """ Clear the content of the data table """
        self.setRowCount(0)

    def delete_rows(self, row_indices):
        """ Delete all rows specified in the row indices to be removed
        from the data_table """

        for row in sorted(row_indices, reverse=True):
            self.removeRow(row)

    def get_id(self, row):
        """ Get the id from the row - per default the first column """
        return self.item(row, 0).text()

    def get_row_display_name(self, row):
        return self.get_id(row)

    def update_row_from_link(self, row):
        self.update_row_from_item(self.item_from_row(row), row)

    def update_row_from_id(self, item_id, col=0):
        items = self.findItems(item_id, Qt.MatchExactly, col)
        for x in items:
            row = self.indexFromItem(x).row()
            self.update_row_from_link(row)

    def populate_table(self, items):
        """ Populate the table with the items from item """
        self.blockSignals(True)
        self.setRowCount(0)
        for i, item in enumerate(items):
            self.update_row_from_item(item, i)
        self.blockSignals(False)
        self.all_data_changed()

    def get_items(self):
        return [self.item_from_row(r) for r in range(self.rowCount())]

    def get_item_to_row_mapping(self):
        return dict((self.item_from_row(r), r) for r in range(self.rowCount()))

    def all_data_changed(self):
        self.dataChanged.emit(self.index(0, 0),
                              self.index(self.rowCount()+1,
                                         self.columnCount()+1))

        # Without sort, tables populated using blockSignals
        # don't show items on Linux
        self.sort(0)