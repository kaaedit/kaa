import kaa
from kaa.command import command, Commands, norec
from kaa.commands import editorcommand


class SearchCommands(editorcommand.EditCommands):

    @command('edit.backspace')
    def backspace(self, wnd):
        pos = wnd.cursor.pos
        if pos > wnd.document.marks['searchtext'][0]:
            super().backspace(wnd)

    @command('edit.delete')
    def delete(self, wnd):
        pos = wnd.cursor.pos
        if pos < wnd.document.marks['searchtext'][1]:
            super().delete(wnd)

    @command('searchdlg.search.next')
    def search_next(self, wnd):
        mode = wnd.document.mode
        mode.search_next(wnd)

    @command('searchdlg.search.prev')
    def search_prev(self, wnd):
        mode = wnd.document.mode
        mode.search_prev(wnd)

    @command('searchdlg.toggle.ignorecase')
    def toggle_ignorecase(self, wnd):
        mode = wnd.document.mode
        mode.toggle_option_ignorecase()

    @command('searchdlg.toggle.wordsearch')
    def toggle_wordsearch(self, wnd):
        mode = wnd.document.mode
        mode.toggle_option_wordsearch()

    @command('searchdlg.toggle.regex')
    def toggle_regex(self, wnd):
        mode = wnd.document.mode
        mode.toggle_option_regex()

class ReplaceCommands(Commands):
    @command('replacedlg.field.next')
    def field_next(self, wnd):
        searchfrom, searchto = wnd.document.marks['searchtext']
        replacefrom, replaceto = wnd.document.marks['replacetext']

        if searchfrom <= wnd.cursor.pos <= searchto:
            wnd.cursor.setpos(replacefrom)
        else:
            wnd.cursor.setpos(searchfrom)
