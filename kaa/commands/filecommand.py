import os
import kaa
import kaa.log
from kaa.command import Commands, command, is_enable, norec, norerun
from kaa.ui.msgbox import msgboxmode

class FileCommands(Commands):
    @command('file.new')
    @norec
    @norerun
    def file_new(self, wnd):
        from kaa import fileio
        doc = fileio.newfile()
        kaa.app.show_doc(doc)

    @command('file.open')
    @norec
    @norerun
    def file_open(self, wnd, filename=''):
        def cb(filename, encoding, newline):
            if not filename:
                return

            for frame in kaa.app.get_frames():
                for doc in frame.get_documents():
                    if doc.get_filename() == filename:
                        if doc.wnds:
                            wnd = doc.wnds[0]
                            wnd.get_label('frame').bring_top()
                            wnd.activate()

                        MAX_FILENAMEMSG_LEN = 50
                        if len(filename) > MAX_FILENAMEMSG_LEN:
                            filename = '...{}'.format(
                                filename[MAX_FILENAMEMSG_LEN*-1:])

                        kaa.app.messagebar.set_message(
                            "`{}` is already opened.".format(filename))
                        return

            doc = kaa.app.storage.openfile(filename, encoding, newline)
            editor = kaa.app.show_doc(doc)
            if doc.fileinfo:
                disp = kaa.app.config.hist_filedisp.find(
                        doc.fileinfo.fullpathname)
                if disp:
                    loc = disp.get('pos', 0)
                    loc = min(loc, doc.endpos())
                    editor.cursor.setpos(loc, top=True)

        from kaa.ui.selectfile import selectfile
        selectfile.show_fileopen(filename, cb)

    @command('file.info')
    @norec
    @norerun
    def file_info(self, wnd):
        from kaa.ui.fileinfo import fileinfomode
        fileinfomode.show_fileinfo(wnd)

    @command('file.save')
    @norec
    @norerun
    def file_save(self, wnd, filename=None, saved=None, document=None,
                  encoding=None, newline=None):
        "Save document"
        try:
            if not document:
                document=wnd.document
            if not filename:
                filename = document.get_filename()

            if filename:
                kaa.app.storage.save_document(document, filename, encoding, newline)
                # notify file saved
                if saved:
                    saved(canceled=False)
            else:
                # no file name. Show save_as dialog.
                self.file_saveas(wnd, saved=saved, document=document)

        except Exception as e:
            kaa.log.exception('File write error:')
            msgboxmode.MsgBoxMode.show_msgbox(
                'File write error: '+str(e), ['&Ok'],
                lambda c:saved(canceled=True) if saved else None,
                keys=['\r', '\n'])

    @command('file.saveas')
    @norec
    @norerun
    def file_saveas(self, wnd, saved=None, document=None):
        "Show save_as dialog and save to the specified file."
        def cb(filename, enc, newline):
            if filename:
                self.file_save(wnd, filename, saved=saved, document=document,
                               encoding=enc, newline=newline)
            else:
                if saved:
                    saved(canceled=True)
                
        if not document:
            document = wnd.document

        from kaa.ui.selectfile import selectfile

        filename = document.get_filename()
        if document.fileinfo:
            newline = document.fileinfo.newline
            encoding = document.fileinfo.encoding
        else:
            newline = encoding = None
            
        selectfile.show_filesaveas(document.get_filename(), newline, encoding, cb)

    def ask_doc_close(self, wnd, document, callback, msg):
        def choice(c):
            if c == 'y':
                self.file_save(wnd, saved=callback, document=document)
            elif c == 'n':
                callback(canceled=False)

        if (document.mode.DOCUMENT_MODE 
            and document.undo
            and document.undo.is_dirty()):
                
            msgboxmode.MsgBoxMode.show_msgbox(
                '{} [{}]: '.format(
                    msg, document.get_title()),
                ['&Yes', '&No', '&Cancel'], choice)
        else:
            callback(canceled=False)

    def save_documents(self, wnd, docs, callback, 
                       msg='Save file before close?', force=False):

        docs = list(docs)
        activeframe = kaa.app.get_activeframe()
    
        def _save_documents(canceled):
            if canceled:
                if activeframe and not activeframe.closed:
                    kaa.app.set_focus(activeframe)
                callback(canceled=True)
                return
                
            if not docs:
                if activeframe and not activeframe.closed:
                    kaa.app.set_focus(activeframe)
                    
                if callback:
                    callback(canceled=False)
            else:
                doc = docs.pop()
                if doc.wnds:
                    w = doc.wnds[0]
                    if w and not w.closed:
                        w.activate()
                        
                if force:
                    self.file_save(wnd, saved=_save_documents, document=doc)
                else:
                    self.ask_doc_close(wnd, doc, _save_documents, msg)

        _save_documents(canceled=False)


    def get_closed_docs(self, editors):
        alldocs = {e.document for e in editors}
        docs = []

        for doc in alldocs:
            doc_editors = set(doc.wnds) - editors
            if not doc_editors:
                docs.append(doc)
        return docs
        
    def close_frame(self, frame, callback):

        editors = {e for e in frame.get_editors()}
        docs = self.get_closed_docs(editors)

        def cb(canceled):
            if not canceled:
                frame.destroy()
                callback(canceled=False)
    
        self.save_documents(frame, docs, cb, 'Save file before close?')

    @command('file.close')
    @norec
    @norerun
    def file_close(self, wnd, callback=None):
        "Close active frame"

        import kaa.fileio

        frame = wnd.get_label('frame')
        def saved(canceled):
            if canceled:
                return 
                
            if frame.mainframe.childframes:
                f = frame.mainframe.childframes[0]
                f.bring_top()
                kaa.app.set_focus(f)
            else:
                doc = kaa.fileio.newfile(provisional=True)
                kaa.app.show_doc(doc)

        self.close_frame(frame, saved)
        
    def get_current_documents(self, wnd):
        docs = set()
        for frame in wnd.mainframe.childframes:
            editors = {e for e in frame.get_editors()}
            docs |= {e.document for e in editors if e.document.mode.DOCUMENT_MODE}
        return docs
        
    @command('file.save.all')
    @norec
    @norerun
    def file_saveall(self, wnd):

        def saved(canceled):
            pass
        
        docs = self.get_current_documents(wnd)
        docs = [doc for doc in docs if doc.undo and doc.undo.is_dirty()]
        if docs:
            self.save_documents(wnd, docs, saved, force=True)

    @command('file.close.all')
    @norec
    @norerun
    def file_closeall(self, wnd):

        def callback(canceled):
            if canceled:
                return
                
            import kaa.fileio
            if frames:
                f = frames.pop()
                self.close_frame(f, callback)
            else:
                doc = kaa.fileio.newfile(provisional=True)
                kaa.app.show_doc(doc)
                
        frames = wnd.mainframe.childframes[:]
        callback(False)

    @command('file.recently-used-files')
    @norec
    @norerun
    def file_recently_used_files(self, wnd):

        def cb(filename):
            if filename:
                self.file_open(wnd, filename)

        files = []
        for p, info in kaa.app.config.hist_files.get():
            path = os.path.relpath(p)
            files.append(path if len(path) < len(p) else p)

        from kaa.ui.selectlist import filterlist
        filterlist.show_listdlg('Recently used files:', 
            files, cb)

    @command('file.recently-used-directories')
    @norec
    @norerun
    def file_recently_used_dirs(self, wnd):

        def cb(filename):
            if filename:
                self.file_open(wnd, filename)

        files = []
        for p, info in kaa.app.config.hist_dirs.get():
            path = os.path.relpath(p)
            files.append(path if len(path) < len(p) else p)

        from kaa.ui.selectlist import filterlist
        filterlist.show_listdlg('Recently used directories:', 
            files, cb)

    @command('file.quit')
    @norec
    @norerun
    def file_quit(self, wnd):

        def saved(canceled):
            if not canceled:
                try:
                    for frame in wnd.mainframe.childframes:
                        frame.destroy()
                except Exception:
                    kaa.log.exception('Error in file.quit:')
                kaa.app.quit()
        
        docs = self.get_current_documents(wnd)
        self.save_documents(wnd, docs, saved, 'Save file before close?')
