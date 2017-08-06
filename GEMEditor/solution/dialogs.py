from PyQt5.QtWidgets import QDialog
from .ui.SolutionDialog import Ui_SolutionDialog
from cobra.core import Solution


class SolutionDialog(QDialog, Ui_SolutionDialog):
    """ Display the model solution in a dialog

    Tables are populated depending on the method used."""

    _valid_methods = ("fba", "pfba")

    def __init__(self, solution, method):
        super(SolutionDialog, self).__init__()
        self.setupUi(self)
        self.solution = None
        self.method = None

        self.set_solution(solution, method)

    def _populate_infobox(self):
        """ Set the information of the solution object to the widgets

        self.solution should be a cobra.Solution object or None"""

        if self.solution is not None:
            self.label_status_value.setText(str(self.solution.status))
            self.label_objective_value.setText(str(self.solution.objective_value))
        else:
            self.label_status_value.clear()
            self.label_objective_value.clear()

    def _populate_tables(self):
        """ Set the solution to tabs """

        for i in range(self.tabWidget.count()):
            self.tabWidget.widget(i).set_solution(self.solution, self.method)

    def set_solution(self, solution, method):
        """ Set solution to dialog

        Parameters
        ----------
        solution
        method

        Returns
        -------

        """

        # Check arguments
        if method not in self._valid_methods:
            raise ValueError("Unexpected method '{0!s}' passed to set_solution".format(method))
        elif not isinstance(solution, Solution):
            raise TypeError("Unexpected type '{0!s}' passed to set_solution".format(type(solution)))

        # Set attributes
        self.solution = solution
        self.method = method
        self.update_display()

    def update_display(self):
        """ Update the display widgets

        At this point solution should be a cobra.Solution object or None and
        method should be valid method or None.

        Returns
        -------

        """
        self._populate_infobox()
        self._populate_tables()
