from PyQt5.QtWidgets import QApplication


# Make sure to only start an application
# if there is no active one. Opening multiple
# applications will lead to a crash.
app = QApplication.instance()
if app is None:
    app = QApplication([])


class TestPubmedBrowser:

    def test_pubmed_browser(self):
        # Todo: Implement test
        assert True