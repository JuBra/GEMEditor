from GEMEditor.model.selection.base import SelectionDialog


class ReferenceSelectionDialog(SelectionDialog):
    def __init__(self, model, *args, **kwargs):
        SelectionDialog.__init__(self, model.QtReferenceTable, *args, **kwargs)
        self.setWindowTitle("Select reference..")
