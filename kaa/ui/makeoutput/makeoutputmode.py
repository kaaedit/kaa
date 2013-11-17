import kaa
from kaa import document
from kaa.ui.filenameindex import filenameindexmode

def show(s):
    buf = document.Buffer()
    doc = document.Document(buf)
    mode = MakeoutputMode()
    doc.setmode(mode)
    doc.insert(0, s)
    kaa.app.show_doc(doc)
    
class MakeoutputMode(filenameindexmode.FilenameIndexMode):
    MODENAME = 'Make'

