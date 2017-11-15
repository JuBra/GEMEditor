from GEMEditor.model.selection.base import SelectionDialog


class CompartmentSelectionDialog(SelectionDialog):
    def __init__(self, model, *args, **kwargs):
        SelectionDialog.__init__(self, model.QtCompartmentTable, *args, **kwargs)
        self.setWindowTitle("Select compartment..")
