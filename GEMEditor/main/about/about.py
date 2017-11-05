from PyQt5.QtWidgets import QDialog, QApplication
from GEMEditor import __projectpage__, __version__
from GEMEditor.main.about.ui import Ui_AboutDialog


class AboutDialog(QDialog, Ui_AboutDialog):
    def __init__(self, parent):
        QDialog.__init__(self, parent)
        self.setupUi(self)
        appname = QApplication.applicationName()
        self.setWindowTitle(self.tr("About {}".format(appname)))
        self.textDisplay.setHtml("""<h1>About {appName}</h1>
        <p><b>Version {version}</b></p>
        <p>{appName} is an editor for genome-scale metabolic models in order to facilitate selection, modification and
        annotation of genome-scale models.<br>
        This program has been developed at the Technical University of Denmark (DTU).</p>

        {appName} is built on top of excellent free software packages:
        <ul>
        <li>Cobrapy for model solving</li>
        <li>Escher for visualization</li>
        <li>Networkx for network layout</li>
        <li>MetaNetX for annotation</li>
        </ul>

        <p>If you need help or want to report a bug, please visit the <a href="{projectPage}">project page</a>.</p>

        <p>If you use {appName} in a scientific publication please cite:<br>
        <b>Brandl J, Andersen MR, unpublished</b></p>

        <p>{appName} is distributed under the following license:</b></p>

        <p>The MIT License (MIT)<br>
        Copyright (c) 2016 Technical University of Denmark (DTU)</p>

        <p>Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:</p>

        <p>The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.</p>

        <p>THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.</p>

        """.format(appName=appname, projectPage=__projectpage__, version=__version__))
