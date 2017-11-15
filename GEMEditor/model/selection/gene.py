from GEMEditor.model.selection.base import SelectionDialog


class GeneSelectionDialog(SelectionDialog):
    def __init__(self, model, *args, **kwargs):
        SelectionDialog.__init__(self, model.QtGeneTable, *args, **kwargs)
        self.setWindowTitle("Select gene..")
