import os
import kaa
import kaa.log
import kaa.utils
from kaa.command import Commands
from kaa.command import commandid
from kaa.command import norec
from kaa.command import norerun


class FileCommands(Commands):

    def _show_msgbox(self, caption, options, callback,
                     keys=None, border=False):

        from kaa.ui.msgbox import msgboxmode
        return msgboxmode.MsgBoxMode.show_msgbox(
            caption, options, callback, keys, border)

    @commandid('file.new')
    @norec
    @norerun
    def file_new(self, wnd):
        doc = kaa.app.storage.newfile()
        kaa.app.show_doc(doc)

    def _find_file_doc(self, filename):
        for frame in kaa.app.get_frames():
            for doc in frame.get_documents():
                if doc.get_filename() == filename:
                    MAX_FILENAMEMSG_LEN = 50
                    if len(filename) > MAX_FILENAMEMSG_LEN:
                        filename = '...{}'.format(
                            filename[MAX_FILENAMEMSG_LEN * -1:])

                    kaa.app.messagebar.set_message(
                        "`{}` is already opened.".format(filename))
                    return doc

    def _activate_file(self, filename):
        doc = self._find_file_doc(filename)
        if doc:
            if doc.wnds:
                wnd = doc.wnds[0]
                wnd.get_label('frame').bring_top()
                wnd.activate()
            return True

    def restore_file_loc(self, wnd):
        if wnd.document.fileinfo:
            disp = kaa.app.config.hist('filedisp').find(
                wnd.document.fileinfo.fullpathname)
            if disp:
                loc = disp.get('pos', 0)
                loc = min(loc, wnd.document.endpos())
                if wnd.document.geteol(loc) != wnd.document.endpos():
                    wnd.cursor.setpos(loc, top=True)
                else:
                    wnd.cursor.setpos(loc, middle=True)

    @commandid('file.open')
    @norec
    @norerun
    def file_open(self, wnd, filename=''):
        def cb(filename, encoding, newline):
            if not filename:
                return

            if self._activate_file(filename):
                return

            doc = kaa.app.storage.openfile(filename, encoding, newline)
            editor = kaa.app.show_doc(doc)
            self.restore_file_loc(editor)

        if not filename:
            if wnd and wnd.document.fileinfo:
                filename = wnd.document.fileinfo.dirname

        from kaa.ui.selectfile import selectfile
        selectfile.show_fileopen(filename, cb)

    @commandid('file.info')
    @norec
    @norerun
    def file_info(self, wnd):
        from kaa.ui.fileinfo import fileinfomode
        fileinfomode.show_fileinfo(wnd)

    @commandid('file.viewdiff')
    @norec
    @norerun
    def file_viewdiff(self, wnd, callback=None):
        if wnd.document.fileinfo and wnd.document.fileinfo.fullpathname:
            from kaa.ui.viewdiff import viewdiffmode
            viewdiffmode.view_doc_diff(wnd.document, callback=None)

    @commandid('file.save')
    @norec
    @norerun
    def file_save(self, wnd, filename=None, saved=None, document=None,
                  encoding=None, newline=None):
        "Save document"
        try:
            if not document:
                document = wnd.document
            if not filename:
                filename = document.get_filename()

            if filename:
                kaa.app.storage.save_document(
                    document, filename, encoding, newline)
                # notify file saved
                if saved:
                    saved(canceled=False)
            else:
                # no file name. Show save_as dialog.
                self.file_saveas(wnd, saved=saved, document=document)

        except Exception as e:
            kaa.log.exception('File write error:')
            self._show_msgbox(
                'File write error: ' + str(e), ['&Ok'],
                lambda c: saved(canceled=True) if saved else None,
                keys=['\r', '\n'])

    @commandid('file.saveas')
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

        if document.fileinfo:
            newline = document.fileinfo.newline
            encoding = document.fileinfo.encoding
        else:
            newline = encoding = None

        selectfile.show_filesaveas(
            document.get_filename(), newline, encoding, cb)

    def ask_doc_close(self, wnd, document, callback, msg):
        def choice(c):
            if c == 'y':
                self.file_save(wnd, saved=callback, document=document)
            elif c == 'n':
                callback(canceled=False)
            elif c == 'd':
                def cb():
                    return self.ask_doc_close(
                        wnd, document, callback, msg)

                if document.fileinfo and document.fileinfo.fullpathname:
                    from kaa.ui.viewdiff import viewdiffmode
                    viewdiffmode.view_doc_diff(document, callback=cb)
                else:
                    cb()

        if (document.mode.DOCUMENT_MODE
                and document.undo
                and document.undo.is_dirty()):

            items = ['&Yes', '&No', '&Cancel']
            if document.fileinfo and document.fileinfo.fullpathname:
                items.append('View &Diff')

            self._show_msgbox(
                '{} [{}]: '.format(
                    msg, document.get_title()),
                items, choice)
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

    @commandid('file.close')
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
                doc = kaa.app.storage.newfile(temporary=True)
                kaa.app.show_doc(doc)

        self.close_frame(frame, saved)

    def get_current_documents(self, wnd):
        docs = set()
        for frame in wnd.mainframe.childframes:
            editors = {e for e in frame.get_editors()}
            docs |= {
                e.document for e in editors if e.document.mode.DOCUMENT_MODE}
        return docs

    @commandid('file.save.all')
    @norec
    @norerun
    def file_saveall(self, wnd):

        def saved(canceled):
            pass

        docs = self.get_current_documents(wnd)
        docs = [doc for doc in docs if doc.undo and doc.undo.is_dirty()]
        if docs:
            self.save_documents(wnd, docs, saved, force=True)

    @commandid('file.close.all')
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
                doc = kaa.app.storage.newfile(temporary=True)
                kaa.app.show_doc(doc)

        frames = wnd.mainframe.childframes[:]
        callback(False)

    def _select_recentry_used_files(self, callback):
        files = []
        for p, info in kaa.app.config.hist('filename').get():
            path = kaa.utils.shorten_filename(p)
            files.append(path if len(path) < len(p) else p)

        from kaa.ui.selectlist import filterlist
        filterlist.show_listdlg('Recently used files:',
                                files, callback)

    @commandid('file.recently-used-files')
    @norec
    @norerun
    def file_recently_used_files(self, wnd):
        def cb(filename):
            if filename:
                filename = os.path.abspath(filename)
                if self._activate_file(filename):
                    return

                self.file_open(wnd, filename)

        self._select_recentry_used_files(cb)

    def _select_recentry_used_dirs(self, callback):
        files = []
        for p, info in kaa.app.config.hist('dirname').get():
            path = kaa.utils.shorten_filename(p)
            files.append(path if len(path) < len(p) else p)

        from kaa.ui.selectlist import filterlist
        filterlist.show_listdlg('Recently used directories:',
                                files, callback)

    @commandid('file.recently-used-directories')
    @norec
    @norerun
    def file_recently_used_dirs(self, wnd):
        def cb(filename):
            if filename:
                self.file_open(wnd, filename)

        self._select_recentry_used_dirs(cb)

    @commandid('file.quit')
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

    def reload_file(self, document):
        fileinfo = document.fileinfo
        newdoc = kaa.app.storage.openfile(
            fileinfo.fullpathname, fileinfo.encoding, fileinfo.newline,
            filemustexists=True)

        for w in document.wnds[:]:
            w.show_doc(newdoc)

        if not document.closed:
            document.close()

    def notify_fileupdated(self, document):
        def choice(c):
            if c == 'y':
                self.reload_file(document)
            elif c == 'n':
                return
            elif c == 'd':
                def cb():
                    return self.notify_fileupdated(document)

                if document.fileinfo and document.fileinfo.fullpathname:
                    from kaa.ui.viewdiff import viewdiffmode
                    viewdiffmode.view_doc_diff(
                        document, callback=cb)
                else:
                    cb()
            else:
                self.notify_fileupdated(document)

        items = ['&Yes', '&No', 'View &Diff']
        msg = 'File [{}] has been updated by other process. Reload file?: '
        self._show_msgbox(msg.format(document.get_title()),
                          items, choice)

    def can_close_wnd(self, wnd, cb):
        if len(wnd.document.wnds) == 1:
            self.ask_doc_close(
                wnd, wnd.document, cb, 'Save file before close?')
        else:
            cb(False)

    def _open_file_to_wnd(self, wnd, func):
        def cb(filename, encoding, newline):
            if not filename:
                return

            doc = self._find_file_doc(filename)
            if not doc:
                doc = kaa.app.storage.openfile(filename, encoding, newline)

            wnd.show_doc(doc)
            self.restore_file_loc(wnd)

        def saved(canceled):
            if canceled:
                return
            func(cb)

        self.can_close_wnd(wnd, saved)

    @commandid('file.new-to')
    @norec
    @norerun
    def file_new_to(self, wnd):
        def openfile(cb):
            doc = kaa.app.storage.newfile()
            wnd.show_doc(doc)

        self._open_file_to_wnd(wnd, openfile)

    @commandid('file.open-to')
    @norec
    @norerun
    def file_open_to(self, wnd):
        def openfile(cb):
            if wnd.document.fileinfo:
                filename = wnd.document.fileinfo.dirname
            else:
                filename = ''
            from kaa.ui.selectfile import selectfile
            selectfile.show_fileopen(filename, cb)

        self._open_file_to_wnd(wnd, openfile)

    def _show_selected_recentlyfile(self, cb, filename):
        if filename:
            filename = os.path.abspath(filename)

            from kaa.ui.selectfile import selectfile
            selectfile.show_fileopen(filename, cb)

    @commandid('file.recently-used-files-to')
    @norec
    @norerun
    def file_recently_used_files_to(self, wnd):
        def selectfile(cb):
            self._select_recentry_used_files(
                lambda filename: self._show_selected_recentlyfile(cb, filename))

        self._open_file_to_wnd(wnd, selectfile)

    @commandid('file.recently-used-directories-to')
    @norec
    @norerun
    def file_recently_used_dirs_to(self, wnd):
        def selectdir(cb):
            self._select_recentry_used_dirs(
                lambda filename: self._show_selected_recentlyfile(cb, filename))

        self._open_file_to_wnd(wnd, selectdir)
