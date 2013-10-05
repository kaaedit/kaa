import kaa
from kaa.command import Commands, command, is_enable, norec, norerun
from kaa import document
from kaa.ui.mainmenu import mainmenumode
from kaa.ui.itemlist import itemlistmode
from kaa.ui.moveseparator import moveseparatormode

class ApplicationCommands(Commands):
    @command('app.mainmenu')
    @norec
    @norerun
    def show_mainmenu(self, wnd):
        doc = mainmenumode.MainMenuMode.build(wnd)
        kaa.app.show_menu(wnd, doc, root=True)

    @command('menu.file')
    @norec
    @norerun
    def show_filemenu(self, wnd):
        doc = mainmenumode.FileMenuMode.build(wnd)
        kaa.app.show_menu(wnd, doc, root=False)

    @command('menu.edit')
    @norec
    @norerun
    def show_editmenu(self, wnd):
        doc = mainmenumode.EditMenuMode.build(wnd)
        kaa.app.show_menu(wnd, doc, root=False)

    @command('menu.edit.convert')
    @norec
    @norerun
    def show_editmenuconvert(self, wnd):
        doc = mainmenumode.EditMenuConvertMode.build(wnd)
        kaa.app.show_menu(wnd, doc, root=False)

    @command('menu.macro')
    @norerun
    @norec
    def show_macromenu(self, wnd):
        doc = mainmenumode.MacroMenuMode.build(wnd)
        kaa.app.show_menu(wnd, doc, root=False)

    @command('menu.tools')
    @norec
    @norerun
    def show_toolsmenu(self, wnd):
        doc = mainmenumode.ToolsMenuMode.build(wnd)
        kaa.app.show_menu(wnd, doc, root=False)

    @command('menu.window')
    @norec
    @norerun
    def show_windowmenu(self, wnd):
        doc = mainmenumode.WindowMenuMode.build(wnd)
        kaa.app.show_menu(wnd, doc, root=False)

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
            wnd.splitter.split(vert=True)

    @command('editor.splithorz')
    @norec
    @norerun
    def editor_splithorz(self, wnd):
        if wnd.splitter:
            wnd.splitter.split(vert=False)

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


    @command('editor.joinwindow')
    @norec
    def editor_joinwindow(self, wnd):
        if wnd.splitter and wnd.splitter.parent:
            buddy = wnd.splitter.get_buddy()
            if not buddy:
                return   # not split

            wnds = set()
            docs = set()
            for splitter, w in buddy.walk():
                if w:
                    wnds.add(w)
                    docs.add(w.document)

            saves = [doc for doc in docs if wnds.issuperset(doc.wnds)]
            def saved():
                wnd.splitter.parent.join(wnd)

            wnd.document.mode.file_commands.save_documents(wnd, saves, saved)


        #if wnd.splitter and wnd.splitter.parent:
        #    if wnd.splitter.parent.wnd:
        #        # not splitted
        #        return
        #
        #    def saved():
        #        wnd.splitter.parent.join(wnd)
        #
        #    if len(wnd.document.wnds) == 1:
        #        wnd.document.mode.file_commands.ask_doc_close(
        #            wnd, wnd.document, saved)
        #    else:
        #        saved()

    @command('editor.switchfile')
    @norec
    @norerun
    def editor_switchfile(self, wnd):
        docs = []
        for frame in kaa.app.get_frames():
            for splitter, w in frame.splitter.walk():
                if w:
                    doc = w.document
                    if doc not in docs:
                        docs.append(doc)

        titles = [doc.get_title() for doc in docs]

        def callback(n):
            doc = docs[n]
            wnd.show_doc(doc)

        def saved():
            n = docs.index(wnd.document)
            doc = itemlistmode.ItemListMode.build('', titles, n, callback)
            kaa.app.show_dialog(doc)

        if len(wnd.document.wnds) == 1:
            wnd.document.mode.file_commands.ask_doc_close(
                wnd, wnd.document, saved)
        else:
            saved()


