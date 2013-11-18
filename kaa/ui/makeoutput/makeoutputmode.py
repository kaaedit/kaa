import kaa
from kaa import document
from kaa.ui.filenameindex import filenameindexmode
from gappedbuf import re as gre

def show(commandline, s):
    buf = document.Buffer()
    doc = document.Document(buf)
    doc.set_title(' '.join(commandline.split()))
    mode = MakeoutputMode()
    doc.setmode(mode)

    doc.insert(0, s)

    mode = doc.mode
    style_filename = mode.get_styleid('filenameindex-filename')
    style_lineno = mode.get_styleid('filenameindex-lineno')
    
    for m in mode.RE_FILENAME.finditer(doc.buf):
        f, t = m.span('FILENAME')
        doc.setstyle(f, t, style_filename)
        
        f, t = m.span('LINENO')
        doc.setstyle(f, t, style_lineno)

    kaa.app.show_doc(doc)
    
class MakeoutputMode(filenameindexmode.FilenameIndexMode):
    MODENAME = 'Make'

