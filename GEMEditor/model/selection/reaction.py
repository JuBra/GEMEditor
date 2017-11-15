from GEMEditor.model.selection.base import SelectionDialog


class ReactionSelectionDialog(SelectionDialog):
    def __init__(self, model, *args, **kwargs):
        SelectionDialog.__init__(self, model.QtReactionTable, *args, **kwargs)
        self.setWindowTitle("Select reaction..")
