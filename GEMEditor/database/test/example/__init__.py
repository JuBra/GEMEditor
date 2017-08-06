from os.path import join, dirname, abspath, isfile
from GEMEditor.database import metanetx_files

files = {}
for key, value in metanetx_files.items():
    path = abspath(join(dirname(abspath(__file__)), value))
    files[key] = path
    assert isfile(path)


