import kaa

class Theme:
    def __init__(self, styles):
        self.styles = {}
        self.add_styles(styles)

    def get_style(self, name):
        return self.styles[name]

    def add_styles(self, styles):
        for style in styles:
            self.styles[style.name] = style

    def update(self, rhs):
        default = self.styles.get('default', None)
        self.add_styles(s.fill(default) for s in rhs.styles.values())

class Style:
    def __init__(self, name, fgcolor, bgcolor, underline=False,
                 bold=False, nowrap=False, rjust=False):
        self.name = name
        self.fgcolor = fgcolor
        self.bgcolor = bgcolor
        self.underline = underline
        self.bold = bold
        self.nowrap = nowrap
        self.rjust = rjust

    def fill(self, default):
        return Style(
            self.name,
            self.fgcolor if self.fgcolor is not None else default.fgcolor,
            self.bgcolor if self.bgcolor is not None else default.bgcolor,
            self.underline if self.underline is not None else default.underline,
            self.bold if self.bold is not None else default.bold,
            self.nowrap if self.nowrap is not None else default.nowrap,
            self.rjust if self.rjust is not None else default.rjust,
        )


