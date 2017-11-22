import logging
from collections import OrderedDict
from GEMEditor.analysis.model_test import get_original_settings, run_test
from GEMEditor.model.classes import Reaction, Metabolite, Gene
from GEMEditor.model.display.proxymodels import metabolite_is_dead_end
from PyQt5.QtWidgets import QApplication


LOGGER = logging.getLogger(__name__)


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
    return OrderedDict([("Total", len(model.references)),
                        ("Unassigned", sum(not r.linked_items for r in model.references.values()))])


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
            LOGGER.debug("Test simulation aborted by user")
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