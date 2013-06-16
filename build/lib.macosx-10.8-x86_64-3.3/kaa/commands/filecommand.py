import kaa
from kaa import LOG
from kaa.command import Commands, command, is_enable, norec
from kaa.ui.msgbox import msgboxmode
from kaa.ui.fileopendlg import fileopendlgmode
from kaa import document

class FileCommands(Commands):
    @command('file.open')
    @norec
    def file_open(self, wnd):
        def cb(filename):
            doc = kaa.app.storage.openfile(filename)
            kaa.app.show_doc(doc)

        fileopendlgmode.show_fileopen('.', cb)


    @command('file.save')
    @norec
    def file_save(self, wnd, filename=None, saved=None, document=None):
        "Save document"
        try:
            if not document:
                document=wnd.document
            if not filename and document.fileinfo:
                filename = document.fileinfo.fullpathname

            if filename:
                kaa.app.storage.save_document(filename, document)
                # notify file saved
                if saved:
                    saved()
            else:
                # no file name. Show save_as dialog.
                self.file_saveas(wnd, saved=saved, document=document)
        except Exception as e:
            LOG.exception('File write error:')
            msgboxmode.MsgBoxMode.show_msgbox(
                'File write error: '+str(e), ['&Ok'], lambda c:self.file_saveas(wnd), keys=['\n'])

    @command('file.saveas')
    @norec
    def file_saveas(self, wnd, saved=None, document=None):
        "Show save_as dialog and save to the specified file."
        def cb(filename):
            self.file_save(wnd, filename, saved=saved, document=document)

        if not document:
            document = wnd.document
        filename = ''
        fileinfo = document.fileinfo
        if fileinfo:
            filename = fileinfo.fullpathname
        fileopendlgmode.show_filesaveas(filename, cb)

    def ask_doc_close(self, wnd, document, callback):
        def saved():
           callback()

        def choice(c):
            if c == 'y':
                self.file_save(wnd, saved=saved)
            elif c == 'n':
                callback()

        if document.undo and document.undo.is_dirty():
            msgboxmode.MsgBoxMode.show_msgbox(
                'Save file before close? [{}]: '.format(
                    document.get_filename()),
                ['&Yes', '&No', '&Cancel'], choice)
        else:
            callback()

    def save_documents(self, wnd, docs, callback):
        def save_documents():
            if not docs:
                if callback:
                    callback()
            else:
                doc = docs.pop()
                self.ask_doc_close(wnd, doc, save_documents)

        save_documents()

    @command('file.close')
    @norec
    def file_close(self, wnd):
        "Close file"

        frame = wnd.get_label('frame')
        editors = {e for e in frame.get_editors()}
        alldocs = {e.document for e in editors}

        docs = []
        for doc in alldocs:
            doc_editors = set(doc.wnds) - editors
            if not doc_editors:
                docs.append(doc)

        def saved():
            frame.destroy()
            if frame.mainframe.childframes:
                kaa.app.set_focus(frame.mainframe.childframes[-1])
            else:
                from kaa.filetype.default import defaultmode
                doc = document.Document(document.Buffer())
                doc.setmode(defaultmode.DefaultMode())
                kaa.app.show_doc(doc)

        self.save_documents(wnd, docs, saved)

    @command('file.quit')
    @norec
    def file_quit(self, wnd):

        docs = set()
        for frame in wnd.mainframe.childframes:
            editors = {e for e in frame.get_editors()}
            docs |= {e.document for e in editors}

        def saved():
            kaa.app.quit()

        self.save_documents(wnd, docs, saved)
