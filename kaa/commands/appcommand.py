import kaa
from kaa.command import Commands, command, is_enable, norec
from kaa import document
from kaa.ui.mainmenu import mainmenumode
from kaa.ui.itemlist import itemlistmode
from kaa.ui.moveseparator import moveseparatormode

class ApplicationCommands(Commands):
    @command('app.mainmenu')
    @norec
    def show_mainmenu(self, wnd):
        doc = mainmenumode.MainMenuMode.build(wnd)
        kaa.app.show_menu(wnd, doc, root=True)

    @command('menu.file')
    @norec
    def show_filemenu(self, wnd):
        doc = mainmenumode.FileMenuMode.build(wnd)
        kaa.app.show_menu(wnd, doc, root=False)

    @command('menu.edit')
    @norec
    def show_editmenu(self, wnd):
        doc = mainmenumode.EditMenuMode.build(wnd)
        kaa.app.show_menu(wnd, doc, root=False)

    @command('menu.macro')
    @norec
    def show_macromenu(self, wnd):
        doc = mainmenumode.MacroMenuMode.build(wnd)
        kaa.app.show_menu(wnd, doc, root=False)

    @command('menu.window')
    @norec
    def show_windowmenu(self, wnd):
        doc = mainmenumode.WindowMenuMode.build(wnd)
        kaa.app.show_menu(wnd, doc, root=False)

    @command('app.show-framelist')
    @norec
    def show_framelist(self, wnd):
        from kaa.ui.framelist import framelistmode
        doc = framelistmode.FrameListMode.build()
        kaa.app.show_dialog(doc)

    @command('editor.splitvert')
    @norec
    def editor_splitvert(self, wnd):
        if wnd.splitter:
            wnd.splitter.split(vert=True)

    @command('editor.splithorz')
    @norec
    def editor_splithorz(self, wnd):
        if wnd.splitter:
            wnd.splitter.split(vert=False)

    @command('editor.moveseparator')
    @norec
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


    @command('editor.joinwindow')
    @norec
    def editor_joinwindow(self, wnd):
        if wnd.splitter and wnd.splitter.parent:
            if wnd.splitter.parent.wnd:
                # not splitted
                return

            def saved():
                wnd.splitter.parent.join(wnd)

            if len(wnd.document.wnds) == 1:
                wnd.document.mode.file_commands.ask_doc_close(
                    wnd, wnd.document, saved)
            else:
                saved()

    @command('editor.switchfile')
    @norec
    def editor_switchfile(self, wnd):
        docs = []
        for frame in wnd.mainframe.childframes:
            docs.extend(
                set(w.document for splitter, w in frame.splitter.walk() if w))
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


