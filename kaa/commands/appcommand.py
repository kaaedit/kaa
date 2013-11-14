import kaa
from kaa.command import Commands, command, is_enable, norec, norerun
from kaa import document

#todo: following imports should be defered
from kaa.ui.mainmenu import menumode
from kaa.ui.itemlist import itemlistmode
from kaa.ui.moveseparator import moveseparatormode

class ApplicationCommands(Commands):
    @command('app.mainmenu')
    @norec
    @norerun
    def show_mainmenu(self, wnd):
        menumode.MenuMode.show_menu(wnd, 'MAIN')

    @command('menu.window')
    @norec
    @norerun
    def show_windowmenu(self, wnd):
        menumode.MenuMode.show_menu(wnd, 'CHANGE-WINDOW')

    @command('menu.edit.convert')
    @norec
    @norerun
    def show_editmenuconvert(self, wnd):
        menumode.MenuMode.show_menu(wnd, 'EDIT-CONVERT')

    @command('menu.code')
    @norec
    @norerun
    def show_codemenu(self, wnd):
        menumode.MenuMode.show_menu(wnd, 'CODE')

    def _walk_all_wnds(self, wnd):
        yield wnd
        curframe = wnd.get_label('frame')
        if curframe:
            for w in curframe.get_editors():
                if w is not wnd:
                    yield w
        
        for frame in kaa.app.get_frames():
            if frame is not curframe:
                for w in frame.get_editors():
                    yield w

    @command('app.global.prev')
    @norec
    @norerun
    def global_prev(self, wnd):
        for w in self._walk_all_wnds(wnd):
            if w.document.mode.on_global_prev(w):
                return

    @command('app.global.next')
    @norec
    @norerun
    def global_next(self, wnd):
        for w in self._walk_all_wnds(wnd):
            if w.document.mode.on_global_next(w):
                return
        
    # todo: move following methods somewhere else

    @command('app.show-framelist')
    @norec
    @norerun
    def show_framelist(self, wnd):
        from kaa.ui.framelist import framelistmode
        doc = framelistmode.FrameListMode.build()
        kaa.app.show_dialog(doc)

    @command('editor.splitvert')
    @norec
    @norerun
    def editor_splitvert(self, wnd):
        if wnd.splitter:
            s = wnd.splitter.split(vert=True)
            s.wnd.activate()

    @command('editor.splithorz')
    @norec
    @norerun
    def editor_splithorz(self, wnd):
        if wnd.splitter:
            s = wnd.splitter.split(vert=False)
            s.wnd.activate()

    @command('editor.moveseparator')
    @norec
    @norerun
    def editor_moveseparator(self, wnd):
        moveseparatormode.move_separator(wnd)

    @command('editor.nextwindow')
    @norec
    def editor_nextwindow(self, wnd):
        splitter = wnd.parent.splitter
        if splitter:
            wnds = [wnd for s, wnd in splitter.walk() if wnd]
            try:
                n = wnds.index(wnd)+1
            except ValueError:
                return

            if n >= len(wnds):
                n = 0
            wnds[n].activate()

    @command('editor.prevwindow')
    @norec
    def editor_prevwindow(self, wnd):
        splitter = wnd.parent.splitter
        if splitter:
            wnds = [wnd for s, wnd in splitter.walk() if wnd]
            try:
                n = wnds.index(wnd)-1
            except ValueError:
                return

            if n < 0:
                n = len(wnds)-1
            wnds[n].activate()

    def save_splitterdocs(self, wnd, splitter, callback):
        wnds = set()
        docs = set()
        for child, w in splitter.walk():
            if w:
                wnds.add(w)
                docs.add(w.document)

        saves = [doc for doc in docs if wnds.issuperset(doc.wnds)]

        wnd.document.mode.file_commands.save_documents(wnd, saves, callback)

    @command('editor.joinwindow')
    @norec
    def editor_joinwindow(self, wnd):
        if wnd.splitter and wnd.splitter.parent:
            buddy = wnd.splitter.get_buddy()
            if not buddy:
                return   # not split

            def saved(canceled):
                if not canceled:
                    wnd.splitter.parent.join(wnd)

            self.save_splitterdocs(wnd, buddy, saved)

    @command('editor.switchfile')
    @norec
    @norerun
    def editor_switchfile(self, wnd):
        docs = []
        for frame in kaa.app.get_frames():
            docs.extend(frame.get_documents())

        titles = [doc.get_title() for doc in docs]

        curdoc = wnd.document
        curdoc_close = curdoc.mode.CLOSE_ON_DEL_WINDOW

        def callback(n):
            curdoc.mode.CLOSE_ON_DEL_WINDOW = curdoc_close
            if n is not None:
                doc = docs[n]
                wnd.show_doc(doc)
            else:
                wnd.show_doc(curdoc)

        def selchanged(n):
            doc = docs[n]
            wnd.show_doc(doc)

        def saved(canceled):
            if canceled:
                return
                
            curdoc.mode.CLOSE_ON_DEL_WINDOW = False
            n = docs.index(wnd.document)
            doc = itemlistmode.ItemListMode.build('', titles, n, callback, selchanged)
            kaa.app.show_dialog(doc)

        wnd.document.mode.file_commands.can_close_wnd(wnd, saved)
