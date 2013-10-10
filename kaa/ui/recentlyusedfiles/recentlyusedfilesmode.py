import os
import kaa
from kaa.ui.selectlist import filterlist


def show_recentlyused(callback, title, items):
    files = []
    for p in items:
        path = os.path.relpath(p)
        files.append(path if len(path) < len(p) else p)

    doc = filterlist.FilterListInputDlgMode.build(title, callback)
    dlg = kaa.app.show_dialog(doc)

    filterlistdoc = filterlist.FilterListMode.build()
    dlg.add_doc('dlg_filterlist', 0, filterlistdoc)

    filterlistdoc.mode.set_candidates(files)

    list = dlg.get_label('dlg_filterlist')
    filterlistdoc.mode.set_query(list, '')
    dlg.on_console_resized()

    return doc


def show_recentlyusedfiles(callback):
    return show_recentlyused(callback, 'Recently used files', kaa.app.config.hist_files)

def show_recentlyuseddirs(callback):
    return show_recentlyused(callback, 'Recently used directories', kaa.app.config.hist_dirs)

