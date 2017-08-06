from GEMEditor.cobra.classes import Reaction, CleaningDict

class TestCleanupDict:

    @pytest.fixture(autouse=True)
    def setup_dict(self):
        self.cleandict = CleaningDict()

    def test_empty_dit(self):
        assert len(self.cleandict) == 0
        assert isinstance(self.cleandict["test"], set)

    def test_addition_deletion(self):
        reaction = Reaction("test")
        subsystem = "subsystem"
        assert len(self.cleandict) == 0

        # Add reaction
        self.cleandict[subsystem].add(reaction)

        # Test addition
        assert len(self.cleandict) == 1
        assert reaction in self.cleandict[subsystem]

        # Remove reaction
        self.cleandict.remove_reaction(subsystem, reaction)
        assert len(self.cleandict) == 0

    def test_removal_with_mutliple_entries(self):
        reaction1 = Reaction("test1")
        reaction2 = Reaction("test2")
        subsystem = "test subsystem"
        self.cleandict[subsystem].add(reaction1)
        self.cleandict[subsystem].add(reaction2)

        # Test addition
        assert len(self.cleandict) == 1
        assert len(self.cleandict[subsystem]) == 2
        assert reaction1 in self.cleandict[subsystem]
        assert reaction2 in self.cleandict[subsystem]

        # Remove reaction1
        self.cleandict.remove_reaction(subsystem, reaction1)
        assert len(self.cleandict) == 1
        assert len(self.cleandict[subsystem]) == 1
        assert reaction2 in self.cleandict[subsystem]

        # Remove reaction2
        self.cleandict.remove_reaction(subsystem, reaction2)
        assert len(self.cleandict) == 0
