from GEMEditor.base.tables import LinkedItem, ElementTable
from GEMEditor.model.classes.modeltest import ReactionSetting, GeneSetting, Outcome
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap, QIcon, QStandardItem, QFont, QBrush


class ReactionBaseTable(ElementTable):

    header = ("ID", "Name", "Formula", "Subsystem", "Lower Bound",
              "Upper Bound", "Objective Coefficient")

    def __init__(self, *args):
        ElementTable.__init__(self, *args)
        self.set_header()

    @staticmethod
    def row_from_item(reaction):
        """ Return a table row from the input reaction """
        id = LinkedItem(reaction.id, reaction)
        name = LinkedItem(reaction.name, reaction)
        reaction_str = LinkedItem(reaction.reaction, reaction)
        subsystem = LinkedItem(reaction.subsystem, reaction)
        lower_bound = LinkedItem(link=reaction)
        lower_bound.setData(reaction.lower_bound, 2)
        upper_bound = LinkedItem(link=reaction)
        upper_bound.setData(reaction.upper_bound, 2)
        obj_coeff = LinkedItem(link=reaction)
        obj_coeff.setData(reaction.objective_coefficient, 2)
        return [id, name, reaction_str, subsystem, lower_bound, upper_bound, obj_coeff]


class ReactionTable(ReactionBaseTable):

    header = ReactionBaseTable.header + ("",)

    def __init__(self, *args):
        ReactionBaseTable.__init__(self, *args)
        scaling_settings = (QSize(15, 15), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
        self.ok_icon = QIcon(QPixmap(":/status_okay").scaled(*scaling_settings))
        self.error_icon = QIcon(QPixmap(":/status_error").scaled(*scaling_settings))
        self.unknown_icon = QIcon(QPixmap(":/status_unknown").scaled(*scaling_settings))
        self.undefined_icon = QIcon(QPixmap(":/status_undefined").scaled(*scaling_settings))

    def row_from_item(self, reaction):
        status = LinkedItem(link=reaction)
        if reaction.balanced is True:
            status.setIcon(self.ok_icon)
        elif reaction.balanced is False:
            status.setIcon(self.error_icon)
        elif reaction.balanced == "Unknown":
            status.setIcon(self.unknown_icon)
        elif reaction.balanced is None:
            status.setIcon(self.undefined_icon)

        return ReactionBaseTable.row_from_item(reaction) + [status]


class MetaboliteTable(ElementTable):

    header = ("ID", "Name", "Formula", "Charge", "Compartment")

    def __init__(self, *args):
        ElementTable.__init__(self, *args)
        self.set_header()

    @staticmethod
    def row_from_item(metabolite):
        """ Return a table row from the input metabolite """
        return [LinkedItem(metabolite.id, metabolite),
                LinkedItem(metabolite.name, metabolite),
                LinkedItem(metabolite.formula, metabolite),
                LinkedItem(str(metabolite.charge), metabolite),
                LinkedItem(metabolite.compartment, metabolite)]


class GeneTable(ElementTable):

    header = ("ID", "Name", "Genome")

    def __init__(self, *args):
        ElementTable.__init__(self, *args)
        self.set_header()

    @staticmethod
    def row_from_item(gene):
        """ Get the table row from the gene item """
        return [LinkedItem(gene.id, gene),
                LinkedItem(gene.name, gene),
                LinkedItem(gene.genome, gene)]


class ReferenceTable(ElementTable):

    header = ("Authors", "Title", "Journal", "Year", "PMID", "PMC", "DOI", "Link")

    def __init__(self, *args):
        ElementTable.__init__(self, *args)
        self.set_header()

    @staticmethod
    def row_from_item(reference):
        return [LinkedItem(reference.reference_string(), reference),
                LinkedItem(reference.title, reference),
                LinkedItem(reference.journal, reference),
                LinkedItem(reference.year, reference),
                LinkedItem(reference.pmid, reference),
                LinkedItem(reference.pmc, reference),
                LinkedItem(reference.doi, reference),
                LinkedItem(reference.url, reference)]


class ModelTestTable(ElementTable):

    header = ("Name", "Status")

    def __init__(self, *args):
        ElementTable.__init__(self, *args)
        self.set_header()

    @staticmethod
    def row_from_item(testcase):
        return [LinkedItem(testcase.description, testcase),
                LinkedItem()]

    def set_status(self, row, solution, passed):
        """ Update the solution display in a given row

        Parameters
        ----------
        row: int
        solution: cobra.core.solution.solution
        passed: bool

        Returns
        -------

        """
        status_item = self.item(row, 1)
        font = QFont()
        font.setBold(True)
        status_item.setFont(font)
        status_item.setData(Qt.AlignCenter | Qt.AlignHCenter, 7)

        if solution is None:
            # No solution passed
            status_item.setText("")
            status_item.link = None
        elif solution.status != "optimal":
            # Erroneous solution
            status_item.setText(solution.status)
            status_item.setForeground(QBrush(Qt.darkMagenta, Qt.SolidPattern))
            status_item.link = None
        elif passed:
            # Solution is optimal and passes test requirements
            status_item.setText("Passed")
            status_item.setForeground(QBrush(Qt.darkGreen, Qt.SolidPattern))
            status_item.link = solution
        else:
            # Solution is optimal, but does not pass test requirements
            status_item.setText("Failed")
            status_item.setForeground(QBrush(Qt.red, Qt.SolidPattern))
            status_item.link = solution


class AnnotationTable(ElementTable):

    header = ("Resource", "ID")

    def __init__(self, *args):
        ElementTable.__init__(self, *args)
        self.set_header()

    @staticmethod
    def row_from_item(item):
        """ Return a row from an annotation item """
        display = LinkedItem(item.collection, item)
        identifier = LinkedItem(item.identifier, item)
        return [display, identifier]


class AuthorTable(ElementTable):

    header = ("Lastname", "Firstname", "Initials")

    def __init__(self, *args):
        ElementTable.__init__(self, *args)
        self.set_header()

    @staticmethod
    def row_from_item(item):
        """ Return a row from an annotation item """
        return [LinkedItem(item.lastname, item),
                LinkedItem(item.firstname, item),
                LinkedItem(item.initials, item)]


class StoichiometryTable(ElementTable):

    header = ("Metabolite", "Stoichiometry")

    def __init__(self, *args):
        ElementTable.__init__(self, *args)
        self.set_header()

    @staticmethod
    def row_from_item(input_tuple):
        """ Return the table row from an input item """
        metabolite, stoichiometry = input_tuple
        id_item = LinkedItem(metabolite.id, metabolite)
        id_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
        id_item.setToolTip("Formula: {}\nCharge: {}".format(metabolite.formula, metabolite.charge))
        value_item = LinkedItem(link=metabolite)
        value_item.setData(stoichiometry, 2)
        return [id_item, value_item]

    def get_items(self):
        return dict(zip(ElementTable.get_items(self), [self.item(r, 1).data(2) for r in range(self.rowCount())]))


class EvidenceTable(ElementTable):

    header = ("Entity", "Assertion", "ECO", "Link", "Comment", "References")

    def __init__(self, *args):
        ElementTable.__init__(self, *args)
        self.set_header()

    @staticmethod
    def row_from_item(item):
        """ Get row from evidence item

        Parameters
        ----------
        item : GEMEditor.evidence_class.Evidence

        Returns
        -------
        list
        """
        return [LinkedItem(item.entity.id, item), LinkedItem(item.assertion, item), LinkedItem(item.eco, item),
                LinkedItem(str(item.link), item), LinkedItem(item.comment, item),
                LinkedItem("; ".join([x.reference_string() for x in item.references]))]

    def get_items(self):
        return [self.item(r).link for r in range(self.rowCount())]


class CompartmentTable(ElementTable):

    header = ("ID", "Name")

    def __init__(self, *args):
        ElementTable.__init__(self, *args)
        self.set_header()

    @staticmethod
    def row_from_item(compartment):
        id_item = LinkedItem(str(compartment.id), compartment)
        name_item = QStandardItem(str(compartment.name))
        return [id_item, name_item]


class ReactionSettingsTable(ElementTable):

    header = ("Reaction", "Lower bound", "Upper bound", "Objective coefficient")

    def __init__(self, *args):
        ElementTable.__init__(self, *args)
        self.set_header()

    @staticmethod
    def row_from_item(setting):
        """ Get a row to be displayed in the table

        Parameters
        ----------
        setting : GEMEditor.data_classes.ReactionSetting

        Returns
        -------
        list
        """
        reaction_item = LinkedItem(setting.reaction.id, setting.reaction)
        reaction_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)

        upper_bound_item = QStandardItem()
        upper_bound_item.setData(setting.upper_bound, 2)

        lower_bound_item = QStandardItem()
        lower_bound_item.setData(setting.lower_bound, 2)

        objective_item = QStandardItem()
        objective_item.setData(setting.objective_coefficient, 2)

        return [reaction_item, lower_bound_item, upper_bound_item, objective_item]

    def item_from_row(self, row_idx):
        """ Return the setting object as represented in a table row """
        # Make sure the lower boundary is smaller than the upper
        bounds = (self.item(row_idx, 1).data(2),
                  self.item(row_idx, 2).data(2))

        return ReactionSetting(reaction=self.item(row_idx, 0).link,
                               lower_bound=min(bounds),
                               upper_bound=max(bounds),
                               objective_coefficient=self.item(row_idx, 3).data(2))


class GeneSettingsTable(ElementTable):

    header = ("Gene", "Status")

    def __init__(self, *args):
        ElementTable.__init__(self, *args)
        self.set_header()

    @staticmethod
    def row_from_item(setting):
        """ Get a row to be displayed in the table

        Parameters
        ----------
        setting : GEMEditor.data_classes.GeneSetting

        Returns
        -------
        list
        """
        gene_item = LinkedItem(setting.gene.id, setting.gene)
        gene_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)

        if setting.activity is True:
            state = "active"
        elif setting.activity is False:
            state = "inactive"
        else:
            raise ValueError("Unknown state '{}' for gene activity.".format(str(setting.gene.functional)))

        activity_item = QStandardItem(state)

        return [gene_item, activity_item]

    def item_from_row(self, row_idx):
        """ Return the setting object as represented in a table row """
        choice = self.item(row_idx, 1).text()
        if choice == "active":
            functional = True
        elif choice == "inactive":
            functional = False
        else:
            raise ValueError("Unknown state '{}' for gene activity.".format(choice))
        return GeneSetting(gene=self.item(row_idx, 0).link, activity=functional)


class OutcomesTable(ElementTable):

    header = ("Reaction", "Operator", "Flux value")

    def __init__(self, *args):
        ElementTable.__init__(self, *args)
        self.set_header()

    @staticmethod
    def row_from_item(outcome):
        reaction_item = LinkedItem(outcome.reaction.id, outcome.reaction)
        reaction_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)

        operator_item = QStandardItem(outcome.operator)

        flux_value_item = QStandardItem()
        flux_value_item.setData(outcome.value, 2)

        return [reaction_item, operator_item, flux_value_item]

    def item_from_row(self, row_idx):
        """ Return the outcome object as represented in a table row """
        return Outcome(reaction=self.item(row_idx, 0).link,
                       operator=self.item(row_idx, 1).text(),
                       value=self.item(row_idx, 2).data(2))
