import sip
sip.setapi('QVariant', 2)
sip.setapi('QString', 2)
from PyQt5.QtGui import QPixmap, QIcon, QStandardItem, QStandardItemModel
from PyQt5.QtCore import Qt, QSize
from GEMEditor.data_classes import ReactionSetting, Outcome, GeneSetting, Compartment


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

    def all_data_changed(self):
        self.dataChanged.emit(self.index(0, 0),
                              self.index(self.rowCount()+1,
                                         self.columnCount()+1))

        # Without sort, tables populated using blockSignals
        # don't show items on Linux
        self.sort(0)


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

    header = ("Abbreviation", "Name")

    def __init__(self, *args):
        ElementTable.__init__(self, *args)
        self.set_header()

    @staticmethod
    def row_from_item(input_tuple):
        id_item = QStandardItem(str(input_tuple[0]))
        id_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
        name_item = QStandardItem(str(input_tuple[1].name))
        return [id_item, name_item]

    def item_from_row(self, row_idx):
        """ Return the linked item of a table row"""
        abbreviation = self.item(row_idx).text()
        name = self.item(row_idx, 1).text()
        return abbreviation, Compartment(abbreviation, name)


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
        reaction : GEMEditor.cobraClasses.Reaction

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
        return ReactionSetting(reaction=self.item(row_idx, 0).link,
                               lower_bound=self.item(row_idx, 1).data(2),
                               upper_bound=self.item(row_idx, 2).data(2),
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


class EvidenceItemsTable(ElementTable):

    header = ("Type", "Part")

    def __init__(self, *args):
        ElementTable.__init__(self, *args)
        self.set_header()

    @staticmethod
    def row_from_item(item):
        type_item = LinkedItem(type(item).__name__, item)
        id_item = LinkedItem(item.id, item)

        return [type_item, id_item]

    def item_from_row(self, row_idx):
        """ Return the outcome object as represented in a table row """
        return self.item(row_idx, 0).link


class LinkedReferenceTable(ElementTable):

    header = ("Authors",)

    def __init__(self, *args):
        ElementTable.__init__(self, *args)
        self.set_header()

    @staticmethod
    def row_from_item(reference):
        return [LinkedItem(reference.reference_string(), reference)]

    def item_from_row(self, row_idx):
        """ Return the outcome object as represented in a table row """
        return self.item(row_idx, 0).link
