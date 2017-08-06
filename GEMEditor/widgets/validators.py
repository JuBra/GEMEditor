from PyQt5 import QtGui


class IdValidator(QtGui.QValidator):
    def __init__(self, id_dict, initial_value=""):
        QtGui.QValidator.__init__(self)
        self.test_list = id_dict
        self.initial_value = initial_value

    def validate(self, p_str, p_int):
        p_str = str(p_str)
        if p_str == "":
            return QtGui.QValidator.Intermediate, p_str, p_int
        elif p_str in self.test_list and p_str != self.initial_value:
            return QtGui.QValidator.Intermediate, p_str, p_int
        else:
            return QtGui.QValidator.Acceptable, p_str, p_int


class PmidValidator(QtGui.QValidator):
    def __init__(self, initial_value=""):
        QtGui.QValidator.__init__(self)
        self.initial_value = str(initial_value)

    def validate(self, p_str, p_int):
        # No common string translate syntax for python 2.7 and 3.0
        p_stripped = "".join(x for x in p_str if x.isdigit())

        if p_stripped:
            if p_stripped != self.initial_value:
                return QtGui.QValidator.Acceptable, p_stripped, p_int
            else:
                return QtGui.QValidator.Intermediate, p_stripped, p_int
        else:
            return QtGui.QValidator.Intermediate, "", p_int
