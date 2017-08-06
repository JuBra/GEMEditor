from PyQt5 import QtCore, QtGui
from PyQt5.QtWebEngineWidgets import QWebEnginePage
from PyQt5.QtWidgets import QErrorMessage, QDialogButtonBox, QMessageBox, QDialog, QInputDialog, QLineEdit, QFileDialog
from PyQt5.QtCore import QStandardPaths
import os.path
from GEMEditor.base.dialogs import CustomStandardDialog
from GEMEditor.ui.ReferenceEditDialog import Ui_ReferenceEditDialog
from GEMEditor.ui.AddAuthorName import Ui_AddAuthorName

from GEMEditor.connect.pubmed import RetrievePubmedData
from GEMEditor.connect.pmc import IdConverter
from GEMEditor.widgets.tables import AuthorTable
from six.moves.urllib.parse import quote
from six.moves.urllib.request import urlopen
from six.moves.urllib.error import URLError
from GEMEditor.ui.PubmedWebBrowser import Ui_PubmedBrowser
from GEMEditor.data_classes import Reference, Author
import lxml.etree as ET


class ReferenceEditDialog(CustomStandardDialog, Ui_ReferenceEditDialog):

    def __init__(self, reference_item):
        CustomStandardDialog.__init__(self)
        self.setupUi(self)

        # Save the input reference item to detect changes
        self.reference_item = reference_item

        # Initialize a error dialog that is fed by the workers
        self.error_dialog = QErrorMessage(self)

        # Setup threads and worker objects for retrieval of data
        # from NCBI. Use one thread for the pubmed lookup.
        self.pmid_thread = QtCore.QThread(self)
        self.pmid_worker = RetrievePubmedData()
        self.pmid_worker.moveToThread(self.pmid_thread)

        # Use a second thread for the querying of non pubmed ids
        # like DOIs or Pubmed central Ids. Those Ids are translated
        # to pubmed ids in order to not implement a second parser
        # for the pubmed central xml format
        self.id_thread = QtCore.QThread(self)
        self.id_worker = IdConverter()
        self.id_worker.moveToThread(self.id_thread)
        self.connect_workers()

        # Setup the author table data model
        self.authorTable = AuthorTable(self)
        self.authorTableView.setModel(self.authorTable)

        # Setup items, disable Ok button and restore state
        self.populate_inputs()
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
        self.setup_connections()
        self.restore_dialog_geometry()

    def setup_connections(self):
        self.authorTable.rowsInserted.connect(self.activateButton)
        self.authorTable.rowsRemoved.connect(self.activateButton)

    @QtCore.pyqtSlot()
    def getPmidInfo(self):
        self.retrieveData("pubmed", self.pmidInput.text().strip())

    @QtCore.pyqtSlot()
    def getPmcInfo(self):
        self.retrieveData("pmc", self.pmcInput.text().strip())

    @QtCore.pyqtSlot()
    def getDOIInfo(self):
        self.retrieveData("doi", quote(self.doiInput.text().strip()))

    @QtCore.pyqtSlot()
    def get_data_from_pmid(self):
        mapping = self.sender().get_information()
        if mapping is not None and mapping["pmid"] is not None:
            self.retrieveData("pubmed", mapping["pmid"])

    def retrieveData(self, database, id):
        # Set the ID on the corresponding worker and start the thread
        # for the lookup of the reference information from NCBI
        if not self.pmid_thread.isRunning() and database == "pubmed":
            self.pmid_worker.set_id(id)
            self.pmid_thread.start()
        elif not self.id_thread.isRunning() and database == "pmc":
            self.id_worker.set_identifier(id)
            self.id_thread.start()
        elif not self.id_thread.isRunning() and database == "doi":
            self.id_worker.set_identifier(id, database)
            self.id_thread.start()

    @QtCore.pyqtSlot()
    def addAuthor(self):
        # Show a dialog to add authors to the table
        dialog = AddAuthorDialog(self)
        status = dialog.exec_()

        if status and dialog.author != ("", "", ""):
            self.authorTable.update_row_from_item(dialog.author)

    @QtCore.pyqtSlot()
    def deleteAuthor(self):
        self.authorTableView.delete_selected_rows()
        self.activateButton()

    @QtCore.pyqtSlot()
    def activateButton(self):
        if self.authorTable.rowCount() != 0 and self.check_modification() and any([self.pmidInput.text(),
                                                     self.pmcInput.text(),
                                                     self.doiInput.text(),
                                                     self.linkInput.text()]):
            self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(True)
        else:
            self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)

    @QtCore.pyqtSlot()
    def checkPMID(self):
        self.searchPubmedButton.setEnabled(self.pmidInput.hasAcceptableInput())

    @QtCore.pyqtSlot()
    def checkPMC(self):
        self.searchPMCButton.setEnabled(self.pmcInput.hasAcceptableInput())

    def check_modification(self):
        # Check that there has been a modification to the reference
        # in order to activate the Ok button
        if any([self.reference_item.pmid != self.pmidInput.text(),
                self.reference_item.pmc != self.pmcInput.text(),
                self.reference_item.doi != self.doiInput.text(),
                self.reference_item.url != self.linkInput.text(),
                self.reference_item.authors != self.get_authors(),
                self.reference_item.year != self.yearInput.text(),
                self.reference_item.title != self.titleInput.text(),
                self.reference_item.journal != self.journalInput.text()]):
            return True
        else:
            return False

    def get_authors(self):
        """ Get a list of all authors in the author table
        The list contains tuples with three elements: (firstname, lastname, initials)
        """
        return self.authorTable.get_items()

    @QtCore.pyqtSlot()
    def update_info_from_online(self):
        sender = self.sender()
        self.populate_inputs(sender.get_reference())

    def populate_inputs(self, reference=None):
        """ Populate the inputs with existing information """
        if reference is None:
            reference = self.reference_item

        # Clear all exising informatino
        self.clear_information()

        if reference is not None:
            for author in reference.authors:
                self.authorTable.update_row_from_item(author)

            self.titleInput.setText(reference.title)
            self.titleInput.setCursorPosition(0)
            self.yearInput.setText(reference.year)
            self.yearInput.setCursorPosition(0)
            self.pmcInput.setText(reference.pmc)
            self.pmcInput.setCursorPosition(0)
            self.pmidInput.setText(reference.pmid)
            self.pmidInput.setCursorPosition(0)
            self.doiInput.setText(reference.doi)
            self.doiInput.setCursorPosition(0)
            self.linkInput.setText(reference.url)
            self.linkInput.setCursorPosition(0)
            self.journalInput.setText(reference.journal)
            self.journalInput.setCursorPosition(0)
            self.activateButton()

    def clear_information(self):
        """ Clear exising information from the dialog """

        self.authorTable.setRowCount(0)
        self.titleInput.clear()
        self.yearInput.clear()
        self.journalInput.clear()
        self.pmidInput.clear()
        self.pmcInput.clear()
        self.doiInput.clear()
        self.linkInput.clear()

    @QtCore.pyqtSlot()
    def save_state(self):
        """ Save the input to the input reference instance """

        self.reference_item.pmid = self.pmidInput.text()
        self.reference_item.pmc = self.pmcInput.text()
        self.reference_item.doi = self.doiInput.text()
        self.reference_item.url = self.linkInput.text()
        self.reference_item.authors = self.get_authors()
        self.reference_item.year = self.yearInput.text()
        self.reference_item.title = self.titleInput.text()
        self.reference_item.journal = self.journalInput.text()

    def connect_workers(self):
        self.id_thread.started.connect(self.id_worker.retrieve_data)
        self.id_worker.error.connect(self.error_dialog.showMessage)
        self.id_worker.finished.connect(self.id_thread.quit)
        self.id_worker.finished.connect(self.get_data_from_pmid)

        self.pmid_thread.started.connect(self.pmid_worker.retrieve_data)
        self.pmid_worker.error.connect(self.error_dialog.showMessage)
        self.pmid_worker.finished.connect(self.pmid_thread.quit)
        self.pmid_worker.finished.connect(self.update_info_from_online)


class AddAuthorDialog(QDialog, Ui_AddAuthorName):
    def __init__(self, *args):
        QDialog.__init__(self, *args)
        self.setupUi(self)

    @property
    def author(self):
        return Author(self.lastnameLineEdit.text(), self.firstnameLineEdit.text(), self.initialsLineEdit.text())


class PubmedBrowser(QDialog, Ui_PubmedBrowser):

    def __init__(self, mainwindow):
        QDialog.__init__(self, mainwindow)
        self.setupUi(self)

        self.error_dialog = QErrorMessage(self)
        self.found_ids = []
        self.known_ids = {}
        self.known_id_path = None
        self.current_index = 0
        self.count = 0

        self.pmid_thread = QtCore.QThread(self)
        self.pmid_worker = RetrievePubmedData()
        self.pmid_worker.moveToThread(self.pmid_thread)

        self.pmid_thread.started.connect(self.pmid_worker.retrieve_data)
        self.pmid_worker.error.connect(self.error_dialog.showMessage)
        self.pmid_worker.finished.connect(self.pmid_thread.quit)
        self.pmid_worker.finished.connect(self.update_info_from_online)

        # Search parameters
        settings = QtCore.QSettings()
        self.email = settings.value("Email")
        self.tool = quote(settings.applicationName())

        # Connect slots
        self.webView.loadProgress.connect(self.progressBar.setValue)

        # Adjust window settings
        self.setWindowFlags(QtCore.Qt.Window)
        #self.webView.page().setLinkDelegationPolicy(QWebEnginePage.DelegateExternalLinks)
        self.webView.setContentsMargins(0,0,0,0)
        self.buttonPrevious.setVisible(False)
        self.buttonNext.setVisible(False)
        self.resultsBox.layout().setContentsMargins(9, 0, 9, 9)
        self.resultsBox.hide()
        self.adjustSize()

        self.load_knowns()

    @QtCore.pyqtSlot()
    def hide_progressbar(self):
        self.progressBar.setVisible(False)

    @QtCore.pyqtSlot()
    def show_progressbar(self):
        self.progressBar.setValue(0)
        self.progressBar.setVisible(True)

    @QtCore.pyqtSlot()
    def search_pubmed(self):
        search_term = "+".join(self.searchInput.text().split(" "))
        search_url = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={term}&retmax=100000&usehistory=y&email={email}&tool={tool}"
        if self.email is not None:
            try:
                url_data = urlopen(search_url.format(tool=self.tool,
                                                     term=search_term,
                                                     email=self.email))
                #record_data = url_data.read().decode('utf-8')
            except URLError:
                return
            else:
                xml_tree = ET.fromstring(url_data.read())
                self.found_ids = [id_obj.text for id_obj in xml_tree.find("IdList")]
                self.count = len(self.found_ids)
                self.current_index = 0
                if not self.count:
                    QMessageBox().information(self, "No result found!",
                                                    "The search term did not find any results!")
                    return
                self.update_stats()
                self.update_display(0, "right")
                self.showMaximized()

    @QtCore.pyqtSlot()
    def add_publication(self):
        pmid = self.found_ids[self.current_index]
        if not self.parent().referenceTab.dataTable.findItems(pmid, QtCore.Qt.MatchExactly, 4):
            self.pmid_worker.set_id(pmid)
            self.pmid_thread.start()
        else:
            QMessageBox().information(self, "Reference found!",
                                            "This reference is already in the reference table!")

    @QtCore.pyqtSlot()
    def push_publication_to_nonread(self):
        current_id = self.found_ids[self.current_index]
        result, ok_clicked = QInputDialog(self).getText(self, self.tr("Enter comment.."), self.tr("Comment:"), QLineEdit.Normal, "")
        if ok_clicked:
            self.known_ids[current_id] = result
            self.next_entry()

    def update_display(self, index, direction):
        if index < 0:
            QMessageBox().information(self, "No more entry found!",
                                            "There is no more entry - index {}!".format(str(index)))
            return

        try:
            current_id = self.found_ids[index]
        except IndexError:
            QMessageBox().information(self, "No more entry found!",
                                            "There is no more entry with index {}!".format(str(index)))
            return
        else:
            if current_id in self.known_ids and self.skipKnowns.isChecked():
                if direction == "right":
                    self.update_display(index+1, direction)
                    return
                elif direction == "left":
                    self.update_display(index-1, direction)
                    return
                else:
                    raise ValueError("Unknown direction {}".format(str(direction)))
            self.buttonPrevious.setEnabled(index > 0)
            self.buttonNext.setEnabled(index < self.count - 1)
            self.current_index = index
            self.numCurrent.setText(str(index+1))
            self.webView.load(QtCore.QUrl("http://www.ncbi.nlm.nih.gov/pubmed/"+current_id))
            self.setFocus()
            self.resultsBox.setVisible(True)
            self.buttonNext.setVisible(True)
            self.buttonPrevious.setVisible(True)

    @QtCore.pyqtSlot()
    def update_info_from_online(self):
        sender = self.sender()
        new_reference = sender.get_reference()
        if new_reference:
            self.parent().referenceTab.dataTable.update_row_from_item(new_reference)
            self.parent().referenceTab.model.add_reference(new_reference)

    def update_stats(self):
        self.numTotal.setText(str(len(self.found_ids))+" new "+"("+str(self.new_entries)+" total"+")")

    @QtCore.pyqtSlot()
    def next_entry(self):
        self.update_display(self.current_index + 1, "right")

    @QtCore.pyqtSlot()
    def previous_entry(self):
        self.update_display(self.current_index - 1, "left")

    @QtCore.pyqtSlot(QtCore.QUrl)
    def open_external_url(self, input_url):
        QtGui.QDesktopServices.openUrl(input_url)

    @QtCore.pyqtSlot(str)
    def toggle_search_button(self, input):
        self.buttonSearch.setEnabled(input != "")

    @QtCore.pyqtSlot()
    def load_knowns(self):
        settings = QtCore.QSettings()
        last_path = settings.value("LastPath") or QStandardPaths.DesktopLocation or None
        filename, filters = QFileDialog.getOpenFileName(self, self.tr("Open known publications"),
                                                        last_path, self.tr("Text file (*.txt)"))
        if filename:
            with open(filename, "r") as open_file:
                try:
                    self.known_ids = dict((line.strip("\n").split("\t")) for line in open_file)
                    self.known_id_path = filename
                    if self.found_ids:
                        self.update_display(self.current_index, "right")
                except ValueError:
                    self.error_dialog.showMessage("Wrong file format!")
                    return

            for reference in self.parent().model.references.values():
                if reference.pmid:
                    self.known_ids[reference.pmid] = "Already in model!"

    @QtCore.pyqtSlot()
    def save_knowns(self):

        # Show error message if known_ids is empty
        if not self.known_ids:
            self.error_dialog.showMessage("There are no visited ids!")
            return

        filename = str(QFileDialog.getSaveFileName(self,
                                                         self.tr("Save Model"),
                                                         self.known_id_path,
                                                         self.tr("Text file (*.txt)")))
        if filename:
            with open(filename, "w") as open_file:
                for x in self.known_ids.items():
                    open_file.write("\t".join(x)+"\n")

    @property
    def new_entries(self):
        return len(set(self.found_ids)-set(self.known_ids.keys()))

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Left:
            self.previous_entry()
            event.ignore()
        elif event.key() == QtCore.Qt.Key_Right:
            self.next_entry()
            event.ignore()
        elif event.key() == QtCore.Qt.Key_Delete:
            self.push_publication_to_nonread()
            event.ignore()
        elif event.key() == QtCore.Qt.Key_Enter:
            # Enter is passed on from the QLineEdit -> ignore event
            event.ignore()



