import logging
from PyQt5.QtWidgets import QDialog, QGridLayout, QGroupBox, QLabel, QApplication, QFileDialog, QDialogButtonBox
from PyQt5 import QtCore
from math import floor
from collections import OrderedDict
from GEMEditor.widgets.proxymodels import metabolite_is_dead_end
from GEMEditor.cobraClasses import Reaction, Metabolite, Gene
from GEMEditor.analysis.model_test import run_test, get_original_settings
from GEMEditor.analysis.ui.BaseStatisticsDialog import Ui_Dialog


logger = logging.getLogger(__name__)


class DisplayStatisticsDialog(QDialog, Ui_Dialog):

    def __init__(self, statistics):
        super(DisplayStatisticsDialog, self).__init__()
        self.setupUi(self)
        self.statistics = statistics
        self.setWindowTitle("Statistics")
        self.buttonBox.accepted.connect(self.save_statistics)
        self.update_statistics()

    def update_statistics(self):

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
        filename, filter = QFileDialog.getSaveFileName(self, self.tr("Save statistics"), None,
                                                       self.tr("Text file (*.txt)"))
        if filename:
            write_stats_to_file(filename, self.statistics)


def reaction_statistics(model):
    num_reactions = len(model.reactions)
    num_transport = 0
    num_boundary = 0
    num_unbalanced = 0
    num_annotated = 0
    num_no_genes = 0
    num_has_presence_evidence = 0
    num_known_gene = 0

    for reaction in model.reactions:
        if len(reaction.metabolites) == 1:
            num_boundary += 1
        elif not reaction.genes:
            num_no_genes += 1

        if len(reaction.get_compartments()) > 1:
            num_transport += 1
        if reaction.balanced is False:
            num_unbalanced += 1
        if reaction.annotation:
            num_annotated += 1
        if any(x.assertion in ("Present", "Catalyzing reaction") for x in reaction.evidences):
            num_has_presence_evidence += 1
        if any(x.assertion == "Catalyzing reaction" for x in reaction.evidences):
            num_known_gene += 1

    return OrderedDict([("Total", num_reactions),
                        ("Transport", num_transport),
                        ("Boundary", num_boundary),
                        ("Unbalanced", num_unbalanced),
                        ("Annotated", num_annotated),
                        ("No genes", num_no_genes),
                        ("Evidence for presence", num_has_presence_evidence),
                        ("Known gene", num_known_gene)])


def metabolite_statistics(model):
    num_anotated = 0
    num_dead_ends = 0

    for metabolite in model.metabolites:
        if metabolite.annotation:
            num_anotated += 1
        if metabolite_is_dead_end(metabolite):
            num_dead_ends += 1

    return OrderedDict([("Total", len(model.metabolites)),
                        ("Annotated", num_anotated),
                        ("DeadEnd", num_dead_ends)])


def gene_statistics(model):
    num_genes = len(model.genes)
    num_unassigned = 0
    num_exp_verified_localization = 0
    num_predicted_localization = 0
    num_known_function = 0

    for gene in model.genes:
        if not gene.reactions:
            num_unassigned += 1
        if any(x.assertion == "Catalyzing reaction" for x in gene.evidences):
            num_known_function += 1
        if any(x.assertion == "Localization" for x in gene.evidences):
            if any(x.eco != "ECO:0000081" for x in gene.evidences):
                num_exp_verified_localization += 1
            else:
                num_predicted_localization += 1

    return OrderedDict([("Total", num_genes),
                        ("Unassigned", num_unassigned),
                        ("Verified location", num_exp_verified_localization),
                        ("Predicted location", num_predicted_localization),
                        ("Known function", num_known_function)])


def reference_statistics(model):
    return {"Total": len(model.references)}


def evidence_statistics(model):

    num_gene_reaction_links = 0
    num_presence_absence = 0
    num_localization = 0
    num_metabolite_presence = 0
    num_valid = 0

    for evidence in model.all_evidences.values():

        if evidence.assertion == "Localization":
            num_localization += 1
        if isinstance(evidence.entity, Reaction):
            if evidence.assertion in ("Present", "Absent"):
                num_presence_absence += 1

        if isinstance(evidence.entity, Metabolite) and \
            evidence.assertion == "Present":
            num_metabolite_presence += 1

        if isinstance(evidence.entity, Gene) and \
                        evidence.assertion in ("Catalyzing reaction", "Not catalyzing reaction"):
            num_gene_reaction_links += 1

        if evidence.is_valid():
            num_valid += 1

    return OrderedDict([("Total", len(model.all_evidences)),
                        ("Gene-Reaction links", num_gene_reaction_links),
                        ("Presence or Absence", num_presence_absence),
                        ("Localization", num_localization),
                        ("Metabolite presence", num_metabolite_presence),
                        ("Valid", num_valid)])


def modeltest_statistics(model, progress):

    num_passing_tests = 0

    original_state = get_original_settings(model)

    # Prepare model for tests
    for x in original_state:
        x.do()

    # Run tests
    progress.setLabelText("Running model tests..")
    progress.setRange(0, len(model.tests))
    QApplication.processEvents()
    logging.info("Running model test statistics..")
    for i, case in enumerate(model.tests):
        # Return if user cancelled
        if progress.wasCanceled():
            logger.info("Test simulation aborted by user")
            break
        else:
            progress.setValue(i)
            QApplication.processEvents()

        # Run test
        passed, _ = run_test(case, model, None)
        if passed:
            num_passing_tests += 1

    # Restore state
    for x in original_state:
        x.undo()

    return OrderedDict([("Total", len(model.tests)),
                        ("Passing", num_passing_tests),
                        ("Failing", len(model.tests)-num_passing_tests)])


def run_all_statistics(model, progress):

    reaction_stats = reaction_statistics(model)
    metabolite_stats = metabolite_statistics(model)
    gene_stats = gene_statistics(model)
    reference_stats = reference_statistics(model)
    evidence_stats = evidence_statistics(model)
    test_stats = modeltest_statistics(model, progress)

    return OrderedDict([("Reactions", reaction_stats),
                        ("Metabolites", metabolite_stats),
                        ("Genes", gene_stats),
                        ("Evidences", evidence_stats),
                        ("Tests", test_stats),
                        ("References", reference_stats)])


def write_stats_to_file(path, model_stats):
    """ Write the statistics of the model to file

    Parameters
    ----------
    path: str
    model_stats: OrderedDict

    Returns
    -------

    """
    with open(path, "w") as open_file:
        for category, statistics in model_stats.items():
            for description, count in statistics.items():
                open_file.write("\t".join((category, description, str(count)))+"\n")