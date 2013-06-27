# class KeyDispatcher:
#     def __init__(self):
#         self.keys = []
#
#     def get_command_keys(self):
#         return self.keys
#
#     def on_key(self, key, keybind):
#         self.keys.append(key)
#         cur_keys = self.get_command_keys()
#         candidates = [(keys, command) for keys, command
#                         in keybind.get_candidates(cur_keys)]
#         match = [command for keys, command in candidates
#                     if len(keys) == len(cur_keys)]
#
#         s = None
#         if not candidates:
#             if len(self.keys) == 1:
#                 if isinstance(key, str):
#                     s = key
#
#         return s, (match[0] if match else None), candidates
#
#     def reset_keys(self):
#         self.keys = []
