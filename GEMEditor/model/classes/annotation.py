

class Annotation:
    def __init__(self, collection=None, identifier=None, type="is"):
        self._collection = collection
        self._identifier = identifier
        self._type = type

    @property
    def collection(self):
        return self._collection

    @property
    def identifier(self):
        return self._identifier

    @property
    def type(self):
        return self._type

    def __eq__(self, other):
        if isinstance(other, Annotation) and (self.collection == other.collection and
                                                self.identifier == other.identifier and
                                                      self.type == other.type):
            return True
        else:
            return False

    def __hash__(self):
        return hash((self._collection, self._identifier, self._type))

    def __str__(self):
        return "Annotation({0!s}, {1!s})".format(self._collection, self._identifier)