from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QTableView, QTreeView


class ElementTableView(QTableView):
    """ QTableView that maps the indexes to the original model """

    def __init__(self, *args, **kwargs):
        QTableView.__init__(self, *args, **kwargs)

    def get_selected_indexes(self, get_first_only=False):
        """ Get currently selected items """
        if get_first_only:
            return self.selectedIndexes()[:1]
        else:
            return self.selectedIndexes()

    def get_selected_columns(self, get_first_only=False):
        """ Get a list of unique columns that are currently selected """

        return list({x.column() for x in self.get_selected_indexes(get_first_only)})

    def get_selected_rows(self, get_first_only=False):
        """ Get a list of unique rows that are currently selected """

        return list({x.row() for x in self.get_selected_indexes(get_first_only)})

    @QtCore.pyqtSlot()
    def delete_selected_rows(self):
        """ Delete all selected rows from data table """

        self.model().delete_rows(self.get_selected_rows())


class ProxyElementTableView(ElementTableView):
    """ QTableView that maps the indexes to the original model """

    def __init__(self, *args, **kwargs):
        ElementTableView.__init__(self, *args, **kwargs)

    def get_selected_indexes(self, get_first_only=False):
        """ Get currently selected items """
        if get_first_only:
            return [self.model().mapToSource(element) for element in self.selectedIndexes()][:1]
        else:
            return [self.model().mapToSource(element) for element in self.selectedIndexes()]

    def get_selected_items(self):
        source_model = self.model().sourceModel()
        return [source_model.item_from_row(row) for row in self.get_selected_rows()]

    @QtCore.pyqtSlot()
    def delete_selected_rows(self):
        """ Delete all selected rows from data table """
        self.model().sourceModel().delete_rows(self.get_selected_rows())


class GeneTreeView(QTreeView):
    def __init__(self, *args, **kwargs):
        QTreeView.__init__(self, *args, **kwargs)

    def mousePressEvent(self, event):
        # Inspired by http://stackoverflow.com/questions/2761284/is-it-possible-to-deselect-in-a-qtreeview-by-clicking-off-an-item

        # Get the index of item at click position
        index = self.indexAt(event.pos())

        # If no item is clicked clear selection and reset index
        if not index.isValid():
            self.clearSelection()
            self.setCurrentIndex(index)
        QTreeView.mousePressEvent(self, event)
