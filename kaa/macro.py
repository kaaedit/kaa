

rec_command = object()
rec_string = object()


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

    def record(self, n_repeat, commandid, *args, **kwargs):
        if not isinstance(commandid, str):
            if hasattr(commandid, 'NOREC'):
                return

            commandid = commandid.COMMAND_ID

        self.commands.append((rec_command, n_repeat, commandid, args, kwargs))

    def record_string(self, s, overwrite):
        self.commands.append([rec_string, overwrite, s])

    def run(self, wnd):
        if self.recording:
            return

        mode = wnd.document.mode
        for rec in self.commands:
            if rec[0] is rec_string:
                wnd.document.mode.put_string(wnd, rec[2], overwrite=rec[1])
                wnd.screen.selection.clear()
            else:
                n_repeat, commandid, args, kwargs = rec[1:]
                wnd.set_command_repeat(n_repeat)
                try:
                    if callable(commandid):
                        commandid(wnd)
                    else:
                        is_available, cmd = mode.get_command(commandid)
                        cmd(wnd, *args, **kwargs)
                finally:
                    wnd.set_command_repeat(1)
