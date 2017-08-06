

class MockSelectionDialog:

    def __init__(self, return_items=None, return_value=1):

        if return_items is None:
            self.return_items = []
        elif not isinstance(return_items, list):
            self.return_items = [return_items]
        else:
            self.return_items = return_items
        self.return_value = return_value

    def selected_items(self):
        return self.return_items

    def exec_(self):
        return self.return_value


class MockModelTestDialog:

    def __init__(self, parent=None, return_value=1,
                 example_item=None):
        self.return_value = return_value
        self.example_item = example_item

    def exec_(self):
        return self.return_value

    def set_test(self, test, model):
        self.test = test
        self.model = model
        self.set_return_values()

    def set_return_values(self):
        if self.example_item is not None:
            self.test.outcomes = self.example_item.outcomes
            self.test.settings = self.example_item.settings
            self.test.description = self.example_item.description

