from GEMEditor.model.classes.modeltest import ModelTest, ReactionSetting, GeneSetting, Outcome
from GEMEditor.rw import *
from PyQt5.QtWidgets import QApplication
from cobra.io.sbml3 import strnum, clip
from lxml.etree import SubElement


def add_tests_to_xml(model_node, model):

    if model.QtTestsTable.rowCount() > 0:
        list_of_tests = SubElement(model_node, ge_listOfTests)

        for element in model.QtTestsTable.get_items():
            test_node = SubElement(list_of_tests, ge_testCase)
            if element.description:
                test_node.set("description", element.description)
            if element.comment:
                test_node.set("comment", element.comment)

            # Add list of settings
            list_of_settings_node = SubElement(test_node, ge_listOfSettings)

            for setting in element.get_reaction_settings():
                SubElement(list_of_settings_node, ge_reactionSetting,
                           attrib={"reactionId": "R_"+setting.reaction.id,
                                   "upperBound": strnum(setting.upper_bound),
                                   "lowerBound": strnum(setting.lower_bound),
                                   "objectiveCoefficient": strnum(setting.objective_coefficient)})

            for setting in element.get_gene_settings():
                SubElement(list_of_settings_node, ge_geneSetting,
                           attrib={"geneId": "G_"+setting.gene.id,
                                   "active": str(setting.activity)})

            list_of_outcomes_node = SubElement(test_node, ge_listOfOutcomes)

            for outcome in element.outcomes:
                SubElement(list_of_outcomes_node, ge_outcome,
                           attrib={"reactionId": "R_"+outcome.reaction.id,
                                   "operator": outcome.operator,
                                   "value": strnum(outcome.value)})

            if element.references:

                list_of_reference_links_node = SubElement(test_node, ge_listOfReferenceLinks)
                for reference in element.references:
                    SubElement(list_of_reference_links_node, ge_referenceLink, attrib={"id": reference.id})


def parse_test_from_xml(model_node, model, progress=None):

    list_of_tests_node = model_node.find(ge_listOfTests)

    if list_of_tests_node is None:
        return
    elif progress is None:
        pass
    elif not progress.wasCanceled():
        progress.setLabelText("Reading test cases...")
        progress.setRange(0, len(list_of_tests_node))
    else:
        return

    for i, test_node in enumerate(list_of_tests_node.iterfind(ge_testCase)):

        if progress is None:
            pass
        elif not progress.wasCanceled():
            progress.setValue(i)
            QApplication.processEvents()
        else:
            return

        new_test = ModelTest(description=test_node.get("description"), comment=test_node.get("comment"))

        settings_list_node = test_node.find(ge_listOfSettings)
        outcomes_list_node = test_node.find(ge_listOfOutcomes)
        reference_list_node = test_node.find(ge_listOfReferenceLinks)

        # Add settings
        if settings_list_node is not None:
            for setting_node in settings_list_node.iterfind(ge_reactionSetting):
                reaction = model.reactions.get_by_id(clip(setting_node.get("reactionId"), "R_"))
                new_setting = ReactionSetting(reaction=reaction,
                                              upper_bound=float(setting_node.get("upperBound")),
                                              lower_bound=float(setting_node.get("lowerBound")),
                                              objective_coefficient=float(setting_node.get("objectiveCoefficient")))
                new_test.add_setting(new_setting)
            for gene_setting_node in settings_list_node.iterfind(ge_geneSetting):
                gene = model.genes.get_by_id(clip(gene_setting_node.get("geneId"), "G_"))
                new_setting = GeneSetting(gene)
                if gene_setting_node.get("active") == "True":
                    new_setting.activity = True
                elif gene_setting_node.get("active") == "False":
                    new_setting.activity = False
                else:
                    raise ValueError("Unexpected value for activity in gene setting.")
                new_test.add_setting(new_setting)

        # Add outcomes
        if outcomes_list_node is not None:
            for outcome_node in outcomes_list_node.iterfind(ge_outcome):
                reaction = model.reactions.get_by_id(clip(outcome_node.get("reactionId"), "R_"))
                new_outcome = Outcome(reaction=reaction,
                                      value=float(outcome_node.get("value")),
                                      operator=outcome_node.get("operator"))
                new_test.add_outcome(new_outcome)

        # Add references
        if reference_list_node is not None:
            for refLink_node in reference_list_node.iterfind(ge_referenceLink):
                new_test.add_reference(model.references[refLink_node.get("id")])

        model.tests.append(new_test)
