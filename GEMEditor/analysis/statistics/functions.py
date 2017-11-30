import logging
from collections import OrderedDict
from GEMEditor.analysis.model_test import run_tests
from GEMEditor.model.classes import Reaction, Metabolite, Gene
from GEMEditor.model.display.proxymodels import metabolite_is_dead_end


LOGGER = logging.getLogger(__name__)


def reaction_statistics(model):
    """ Calculate the reaction stats

    Parameters
    ----------
    model: GEMEditor.model.classes.Model,
        Model for which to retrieve counts

    Returns
    -------
    OrderedDict,
        Dictionary containing the reaction stats

    """

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
    """ Calculate the metabolite stats

    Parameters
    ----------
    model: GEMEditor.model.classes.Model,
        Model for which to retrieve counts

    Returns
    -------
    OrderedDict,
        Dictionary containing the metabolite stats

    """

    num_total = len(model.metabolites)
    num_anotated = 0
    num_dead_ends = 0

    for metabolite in model.metabolites:
        if metabolite.annotation:
            num_anotated += 1
        if metabolite_is_dead_end(metabolite):
            num_dead_ends += 1

    return OrderedDict([("Total", num_total),
                        ("Annotated", num_anotated),
                        ("DeadEnd", num_dead_ends)])


def gene_statistics(model):
    """ Calculate the gene stats

    Parameters
    ----------
    model: GEMEditor.model.classes.Model,
        Model for which to retrieve counts

    Returns
    -------
    OrderedDict,
        Dictionary containing the gene stats

    """

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
    """ Calculate the reference stats

    Parameters
    ----------
    model: GEMEditor.model.classes.Model,
        Model for which to retrieve counts

    Returns
    -------
    OrderedDict,
        Dictionary containing the reference stats

    """

    return OrderedDict([("Total", len(model.references)),
                        ("Unassigned", sum(not r.linked_items for r in model.references.values()))])


def evidence_statistics(model):
    """ Calculate the evidence stats

    Parameters
    ----------
    model: GEMEditor.model.classes.Model,
        Model for which to retrieve counts

    Returns
    -------
    OrderedDict,
        Dictionary containing the evidence stats

    """

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
    """ Calculate the test stats

    Parameters
    ----------
    model: GEMEditor.model.classes.Model,
        Model for which to retrieve counts

    progress: QProgressDialog,
        Progress dialog informing user

    Returns
    -------
    result: OrderedDict,
        Dictionary containing the test stats

    """
    LOGGER.debug("Running test statistics..")

    num_total = len(model.tests)
    num_passing = 0
    num_failing = 0
    num_not_run = 0

    test_results = run_tests(model.tests, model, progress)

    for testcase in model.tests:
        try:
            status, _ = test_results[testcase]
        except KeyError:
            num_not_run += 1
        else:
            if status:
                num_passing += 1
            else:
                num_failing += 1

    result = OrderedDict([("Total", num_total),
                          ("Passing", num_passing),
                          ("Failing", num_failing)])
    if num_not_run:
        result["Not run"] = num_not_run

    return result


def run_all_statistics(model, progress):
    """ Calculate all statistics

    Parameters
    ----------
    model: GEMEditor.model.classes.Model,
        Model for which to retrieve counts

    progress: QProgressDialog,
        Progress dialog informing user

    Returns
    -------
    OrderedDict,
        Dictionary containing all stats grouped by item type

    """

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