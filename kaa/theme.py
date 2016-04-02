

class Theme:

    def __init__(self, styles):
        self.styles = {}
        self.overlays = {}
        self.add_styles(styles)

    def get_style(self, name):
        return self.styles[name]

    def add_styles(self, styles):
        for style in styles:
            if not isinstance(style, Overlay):
                # Style instance
                self.styles[style.name] = style
            else:
                self.overlays[style.name] = style

    def update(self, rhs):
        default = self.styles.get('default', None)
        styles = []
        for s in rhs:
            s = s.copy()
            if s.name == 'default':
                s.set_default_attr(default)
            styles.append(s)
        self.add_styles(styles)

    def finish_update(self):
        default = self.styles.get('default', None)
        for style in self.styles.values():
            style.set_default_attr(default)


class Style:

    def __init__(self, name, fgcolor, bgcolor, underline=False,
                 bold=False, nowrap=False, rjust=False, fillrow=False):
        self.name = name
        self.fgcolor = fgcolor
        self.bgcolor = bgcolor
        self.underline = underline
        self.bold = bold
        self.nowrap = nowrap
        self.rjust = rjust
        self.fillrow = fillrow

    def copy(self):
        # ???
        return self.__class__(
            self.name,
            self.fgcolor,
            self.bgcolor,
            self.underline,
            self.bold,
            self.nowrap,
            self.rjust,
            self.fillrow,
        )

    def set_default_attr(self, default):
        # ???
        if self.fgcolor is None:
            self.fgcolor = default.fgcolor
        if self.bgcolor is None:
            self.bgcolor = default.bgcolor
        if self.underline is None:
            self.underline = default.underline
        if self.bold is None:
            self.bold = default.bold
        if self.nowrap is None:
            self.nowrap = default.nowrap
        if self.rjust is None:
            self.rjust = default.rjust
        if self.fillrow is None:
            self.fillrow = default.fillrow


class Overlay(Style):

    def __init__(self, name, fgcolor=None, bgcolor=None,
                 underline=None, bold=None):
        super().__init__(name, fgcolor, bgcolor, underline, bold)

    def copy(self):
        return self.__class__(
            self.name,
            self.fgcolor,
            self.bgcolor,
            self.underline,
            self.bold
        )

    def set_default_attr(self, default):
        pass
