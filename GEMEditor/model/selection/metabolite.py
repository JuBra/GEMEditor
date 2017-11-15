from GEMEditor.model.selection.base import SelectionDialog


class MetaboliteSelectionDialog(SelectionDialog):
    def __init__(self, model, *args, **kwargs):
        SelectionDialog.__init__(self, model.QtMetaboliteTable, *args, **kwargs)
        self.setWindowTitle("Select metabolite..")
