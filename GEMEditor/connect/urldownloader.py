import logging
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QProgressDialog
from urllib.request import urlretrieve, ContentTooShortError, HTTPError, URLError
from time import time
from math import ceil


LOGGER = logging.getLogger(__name__)


class StopDownload(Exception):
    pass


class Downloader(QtCore.QObject):
    """ A Downloar worker that can be used in threads for downloading any file.

    The downloader emits the finished signal when finished. Error messages are
    saved in the error attribute if any error occured, otherwise the attribute is None.
    The filename to which the content has been downloaded is saved in the filename
    attribute.

    How to use:
    1) Set up a QThread
    2) Use QThread moveToThread in order to move the Downloader to the thread
    3) Connect the signals of the worker to the corresponding object.
       It is necessary to connect the Thread.started signal to the Downloader.process slot
       as well as the Downloader.finished signal to the Thread.quit slot
       If there should be a progress update connect the Downloader.download_status to the
       corresponding progess dialog method
    4) Start the thread using the Thread.start method

    If no filename is specified the content will be saved to a temp file."""

    download_status = QtCore.pyqtSignal(int, int, int)
    finished = QtCore.pyqtSignal()

    def __init__(self, url, filename=None):
        super(Downloader, self).__init__()
        self.url = url
        self.filename = filename
        self.error = None
        self.wasCanceled = False

    def process(self):
        # If no url has been in the constructor, exit with an error.
        if not self.url:
            LOGGER.error("Url not specified during __init__")
            self.finish_with_error("Url not specified for download!")
            return

        # Download the content of the url
        LOGGER.debug("Trying to download {0!s}, saving it to {1!s}..".format(self.url, self.filename))
        try:
            self.filename, _ = urlretrieve(url=self.url, filename=self.filename,
                                           reporthook=self.update_status)
        except (ContentTooShortError, HTTPError, URLError) as e:
            LOGGER.exception("An error occurred during the download:")
            self.finish_with_error("There has been an error while downloading the file!\n\n{}".format(str(e)))
            return
        except StopDownload:
            LOGGER.debug("User cancelled download")
            self.finish_with_error("Download cancelled!")
            return

        LOGGER.debug("Download successful!")
        self.finished.emit()

    def update_status(self, transferred_blocks, block_size, file_size):
        """ Update connected progress dialogs

        This function is used as reporthook in urlretrieve and thereby
        repetitively called. Updates the ProgressDialog by emitting
        self.download_status and by raising StopDownload terminates
        download if user cancelled the ProgressDialog.

        Parameters
        ----------
        transferred_blocks: int
        block_size: int
        file_size: int

        Raises
        ------
        StopDownload
            If user cancelled the download

        """

        if self.wasCanceled:
            raise StopDownload
        self.download_status.emit(transferred_blocks, block_size, file_size)
        LOGGER.debug("Download status: Blocks {0!s} Blocksize {1!s} Filesize {2!s}".format(transferred_blocks,
                                                                                           block_size,
                                                                                           file_size))

    @QtCore.pyqtSlot()
    def set_canceled(self):
        self.wasCanceled = True

    def finish_with_error(self, error):
        self.error = error
        self.finished.emit()


class DownloadProgressDialog(QProgressDialog):
    """ A ProgressDialog for using with a download worker.

    How to use:
    1) Connect the worker status signal to the DownloadDialog.set_progress method
    2) Connect the DownloadDialog.wasCanceled signal to the threads

    """

    def __init__(self, *args, minimum_duration=None, auto_close=None, window_title="Download"):
        super(DownloadProgressDialog, self).__init__(*args)

        self.chunks = 0
        self.time = 0
        self.setWindowTitle(window_title)

        if minimum_duration is not None:
            self.setMinimumDuration(minimum_duration)
        if auto_close is not None:
            self.setAutoClose(auto_close)

    @QtCore.pyqtSlot(int, int, int)
    def set_progress(self, num_blocks_transferred, block_size, file_size):
        if self.wasCanceled():
            raise StopDownload

        elif not self.time:
            self.setMaximum(ceil(file_size/block_size))
            self.time = time()
            self.setValue(0)

        # Keep track of the chunks
        self.chunks += block_size

        # Only update every 0.5 seconds
        self.setValue(num_blocks_transferred)
        QApplication.processEvents()




