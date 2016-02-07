import kaa
from kaa import document
from kaa.ui.filenameindex import filenameindexmode


def show(commandline, s):
    doc = document.Document()
    doc.set_title(' '.join(commandline.split()))
    mode = MakeoutputMode()
    doc.setmode(mode)

    doc.insert(0, s)

    mode = doc.mode
    style_filename = mode.get_styleid('filenameindex-filename')
    style_lineno = mode.get_styleid('filenameindex-lineno')

    for m in mode.RE_FILENAME.finditer(doc):
        f, t = m.span('FILENAME')
        doc.setstyles(f, t, style_filename, update=False)

        f, t = m.span('LINENO')
        doc.setstyles(f, t, style_lineno, update=False)

    kaa.app.show_doc(doc)


class MakeoutputMode(filenameindexmode.FilenameIndexMode):
    MODENAME = 'Make'
