import functools
import kaa
from kaa.command import Commands
from kaa.command import commandid
from kaa.command import norec
from kaa.command import norerun


class ViCommands(Commands):

    @commandid('edit.replace-next-char')
    @norec
    @norerun
    def replace_next_char(self, wnd):
        wnd.editmode.install_keyhook(self._hook_replacechar)

    def _hook_replacechar(self, wnd, keyevent):
        s = keyevent.key[0]
        if isinstance(s, str) and s >= ' ':
            wnd.document.mode.put_string(wnd, s, overwrite=True)
            return None
        return keyevent

    @commandid('edit.delete-next-move')
    @norec
    @norerun
    def delete_next_move(self, wnd):
        wnd.editmode.install_keyhook(self._hook_key_delete_next_move)

    def _hook_key_delete_next_move(self, wnd, keyevent):
        s = keyevent.key
        if isinstance(s, str) and s == 'd':
            wnd.document.mode.on_commands(wnd, ['edit.delete.currentline'])
        else:
            f = functools.partial(self._hook_delete_next_move,
                                  wnd.cursor.pos)
            wnd.editmode.install_post_key_hook(f)
            return keyevent

    def _hook_delete_next_move(self, posfrom, wnd, s, commands):
        if kaa.app.focus is wnd:
            if commands:
                f, t = sorted((posfrom, wnd.cursor.pos))
                if f != t and t <= wnd.document.endpos():
                    wnd.document.mode.delete_string(wnd, f, t)
