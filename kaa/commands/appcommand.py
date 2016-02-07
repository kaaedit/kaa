import kaa
from kaa.command import Commands
from kaa.command import commandid
from kaa.command import norec
from kaa.command import norerun


class ApplicationCommands(Commands):

    def show_menu(self, wnd, name):
        from kaa.ui.mainmenu import menumode
        menumode.MenuMode.show_menu(wnd, name)

    @commandid('app.mainmenu')
    @norec
    @norerun
    def show_mainmenu(self, wnd):
        self.show_menu(wnd, 'MAIN')

    @commandid('menu.window')
    @norec
    @norerun
    def show_windowmenu(self, wnd):
        self.show_menu(wnd, 'CHANGE-WINDOW')

    @commandid('menu.edit.convert')
    @norec
    @norerun
    def show_editmenuconvert(self, wnd):
        self.show_menu(wnd, 'EDIT-CONVERT')

    @commandid('menu.code')
    @norec
    @norerun
    def show_codemenu(self, wnd):
        self.show_menu(wnd, 'CODE')

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

    @commandid('app.global.prev')
    @norec
    @norerun
    def global_prev(self, wnd):
        for w in self._walk_all_wnds(wnd):
            if w.document.mode.on_global_prev(w):
                return

    @commandid('app.global.next')
    @norec
    @norerun
    def global_next(self, wnd):
        for w in self._walk_all_wnds(wnd):
            if w.document.mode.on_global_next(w):
                return

    # todo: move following methods somewhere else

    @commandid('app.show-framelist')
    @norec
    @norerun
    def show_framelist(self, wnd):
        frames = list(kaa.app.get_frames())
        titles = list(frame.get_title().replace('&', '&&') for frame in frames)

        last_sel = None

        def callback(n):
            # bring the frame a top of frame list.
            if last_sel:
                wnd.mainframe.register_childframe(last_sel)

        def selchanged(n):
            frames[n].bring_top()
            dlg.get_label('popup').bring_top()

            nonlocal last_sel
            if n is not None:
                last_sel = frames[n]

        from kaa.ui.itemlist import itemlistmode
        doc = itemlistmode.ItemListMode.build(
            '', titles, 0, callback, selchanged)
        dlg = kaa.app.show_dialog(doc)

    @commandid('editor.splitvert')
    @norec
    @norerun
    def editor_splitvert(self, wnd):
        if wnd.splitter:
            s = wnd.splitter.split(vert=True)
            s.wnd.activate()

    @commandid('editor.splithorz')
    @norec
    @norerun
    def editor_splithorz(self, wnd):
        if wnd.splitter:
            s = wnd.splitter.split(vert=False)
            s.wnd.activate()

    @commandid('editor.moveseparator')
    @norec
    @norerun
    def editor_moveseparator(self, wnd):
        from kaa.ui.moveseparator import moveseparatormode
        moveseparatormode.move_separator(wnd)

    @commandid('editor.nextwindow')
    @norec
    def editor_nextwindow(self, wnd):
        splitter = wnd.parent.splitter
        if splitter:
            wnds = [w for s, w in splitter.walk() if w]
            try:
                n = wnds.index(wnd) + 1
            except ValueError:
                return

            if n >= len(wnds):
                n = 0
            wnds[n].activate()

    @commandid('editor.prevwindow')
    @norec
    def editor_prevwindow(self, wnd):
        splitter = wnd.parent.splitter
        if splitter:
            wnds = [w for s, w in splitter.walk() if w]
            try:
                n = wnds.index(wnd) - 1
            except ValueError:
                return

            if n < 0:
                n = len(wnds) - 1
            wnds[n].activate()

    def save_splitterdocs(self, wnd, splitter, callback):
        wnds = set()
        docs = set()
        for child, w in splitter.walk():
            if w:
                wnds.add(w)
                docs.add(w.document)

        saves = [doc for doc in docs if wnds.issuperset(doc.wnds)]

        kaa.app.file_commands.save_documents(wnd, saves, callback)

    @commandid('editor.joinwindow')
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

    @commandid('editor.switchfile')
    @norec
    @norerun
    def editor_switchfile(self, wnd):
        docs = []
        for frame in kaa.app.get_frames():
            docs.extend(frame.get_documents())

        titles = [doc.get_title().replace('&', '&&') for doc in docs]

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

            from kaa.ui.itemlist import itemlistmode
            doc = itemlistmode.ItemListMode.build(
                '', titles, n, callback, selchanged)
            kaa.app.show_dialog(doc)

        kaa.app.file_commands.can_close_wnd(wnd, saved)


class MacroCommands(Commands):

    @commandid('macro.start-record')
    @norec
    @norerun
    def start_record(self, wnd):
        kaa.app.macro.start_record()
        kaa.app.messagebar.update()

    @commandid('macro.end-record')
    @norec
    @norerun
    def end_record(self, wnd):
        kaa.app.macro.end_record()
        kaa.app.messagebar.update()

    @commandid('macro.toggle-record')
    @norec
    @norerun
    def toggle_record(self, wnd):
        kaa.app.macro.toggle_record()
        kaa.app.messagebar.update()

    @commandid('macro.run')
    @norec
    def run_macro(self, wnd):
        if kaa.app.macro.is_recording():
            return
        if not kaa.app.macro.get_commands():
            return

        kaa.app.macro.run(wnd)
