import kaa
class Macro:
    recording = False
    commands = ()

    def start_record(self):
        self.recording = True
        self.commands = []

    def end_record(self):
        self.recording = False

    def toggle_record(self):
        self.recording = not self.recording
        if self.recording:
            self.commands = []

    def is_recording(self):
        return self.recording

    def get_commands(self):
        return self.commands

    def record(self, f, *args, **kwargs):
        if not hasattr(f, 'NOREC'):
            commandid = f.COMMAND_ID
            self.commands.append((commandid, args, kwargs))

    def record_string(self, s):
        if not self.commands or not isinstance(self.commands[-1], str):
            self.commands.append(s)
        else:
            self.commands[-1] += s

    def record_repeatcount(self, n):
        if not self.commands or not isinstance(self.commands[-1], (int, type(None))):
            self.commands.append(n)
        else:
            self.commands[-1] = n

    def run(self, wnd):
        if self.recording:
            return

        mode = wnd.document.mode
        for cmd in self.commands:
            if isinstance(cmd, str):
                wnd.document.mode.edit_commands.put_string(wnd, cmd)
                wnd.screen.selection.clear()
            elif isinstance(cmd, (int, type(None))):
                wnd.editmode.set_repeat(cmd)
            else:
                commandid, args, kwargs = cmd
                if callable(commandid):
                    commandid(wnd)
                else:
                    is_available, cmd = mode.get_command(commandid)
                    cmd(wnd, *args, **kwargs)
