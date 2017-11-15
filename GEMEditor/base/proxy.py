from PyQt5 import QtCore
from PyQt5.QtCore import QSortFilterProxyModel


class CustomSortFilterProxyModel(QSortFilterProxyModel):

    def __init__(self, *args, **kwargs):
        super(CustomSortFilterProxyModel, self).__init__(*args, **kwargs)
        self.custom_filter = 0

    def filterAcceptsRow(self, p_int, QModelIndex):
        item = self.sourceModel().item(p_int, 0).link
        if self.filterRegExp():
            return (self.passes_custom_filter(item) and
                    super(CustomSortFilterProxyModel, self).filterAcceptsRow(p_int, QModelIndex))
        else:
            return self.passes_custom_filter(item)

    def passes_custom_filter(self, item):
        raise NotImplementedError

    @QtCore.pyqtSlot(int)
    def set_custom_filter(self, n):
        self.custom_filter = n
        self.invalidateFilter()

    def setSourceModel(self, QAbstractItemModel):
        super(CustomSortFilterProxyModel, self).setSourceModel(QAbstractItemModel)
        QAbstractItemModel.dataChanged.connect(self.invalidate)


class RecursiveProxyFilter(QSortFilterProxyModel):

    def __init__(self, *args, **kwargs):
        super(RecursiveProxyFilter, self).__init__(*args, **kwargs)

    def filterAcceptsRow(self, p_int, QModelIndex):
        if super(RecursiveProxyFilter, self).filterAcceptsRow(p_int, QModelIndex) is True:
            return True

        elif self.filterRegExp():
            index = self.sourceModel().index(p_int, 0, QModelIndex)

            if index.isValid():
                # Search children
                for child_row in range(self.sourceModel().rowCount(index)):
                    if self.filterAcceptsRow(child_row, index):
                        return True
        return False