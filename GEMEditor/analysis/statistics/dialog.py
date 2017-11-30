import logging
from collections import OrderedDict
from math import floor
from GEMEditor.analysis.statistics.ui import Ui_StatisticsDialog
from PyQt5 import QtCore
from PyQt5.QtWidgets import QDialog, QGridLayout, QGroupBox, QLabel, QFileDialog, QDialogButtonBox, \
    QPushButton

logger = logging.getLogger(__name__)


class DisplayStatisticsDialog(QDialog, Ui_StatisticsDialog):
    """ Display model statistics

    Show model statistics one groupboxes per item type
    containing all computed numbers. The user has the
    choice to save the displayed statistics to a file.

    Parameters
    ----------
    statistics: OrderedDict,
        Dictionary containing the statistics grouped in categories

    """

    def __init__(self, statistics):
        super(DisplayStatisticsDialog, self).__init__()
        self.setupUi(self)
        self.statistics = statistics
        self.setWindowTitle("Statistics")
        self.save_button = QPushButton("Save")
        self.buttonBox.addButton(self.save_button, QDialogButtonBox.ActionRole)
        self.save_button.clicked.connect(self.save_statistics)
        self.update_statistics()

    def update_statistics(self):
        """ Populate the dialogs with numbers from
        the statistics dictionary. """

        # Delete existing child widgets
        for i in reversed(range(self.mainLayout.count())):
            current_widget = self.mainLayout.itemAt(i).widget()
            self.mainLayout.removeWidget(current_widget)
            current_widget.setParent(None)

        # Populate layout with new widgets
        for i, item in enumerate(self.statistics.items()):
            key, value = item
            # Generate group box per item
            group_widget = QGroupBox()
            group_widget.setTitle(key)

            # Set group layout
            group_layout = QGridLayout()
            group_widget.setLayout(group_layout)

            # Add groupbox to main layout (3 columns)
            self.mainLayout.addWidget(group_widget, floor(i/3), i % 3)

            # Add items to groupbox
            for n, item in enumerate(value.items()):
                # Add description
                group_layout.addWidget(QLabel(item[0]), n, 0, QtCore.Qt.AlignTop)
                # Add count
                group_layout.addWidget(QLabel(str(item[1])), n, 1, QtCore.Qt.AlignTop | QtCore.Qt.AlignRight)

            # Stretch last row to make rows align at top
            group_layout.setRowStretch(n, 1)

    @QtCore.pyqtSlot()
    def save_statistics(self):
        """ Write stats to file """
        filename, filter = QFileDialog.getSaveFileName(self, self.tr("Save statistics"), None,
                                                       self.tr("Text file (*.txt)"))
        if filename:
            write_stats_to_file(filename, self.statistics)


def write_stats_to_file(path, model_stats):
    """ Write the statistics to file

    Parameters
    ----------
    path: str
        File path to save statistics to
    model_stats: OrderedDict
        Dictionary containing the statistics grouped in categories

    """
    with open(path, "w") as open_file:
        for category, statistics in model_stats.items():
            for description, count in statistics.items():
                open_file.write("\t".join((category, description, str(count)))+"\n")
