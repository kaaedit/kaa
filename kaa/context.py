class Context:

    def iter_roots(self):
        c = self
        while c:
            if isinstance(c, ContextRoot):
                yield c
            c = c.get_context_parent()

    def get_context_parent(self):
        raise NotImplementedError

    def get_context(self):
        for r in self.iter_roots():
            return r

    def set_label(self, name, obj):
        self.get_context().context[name] = obj

    def get_label(self, name):
        for r in self.iter_roots():
            ret = r.context.get(name)
            if ret:
                return ret

    def del_label(self, name):
        if name in self.get_context().context:
            del self.context[name]
            return True


class ContextRoot(Context):

    def __init__(self):
        super().__init__()
        self.context = {}

    def destroy_context(self):
        self.context.clear()
