from kaa.theme import Theme, Style, Overlay

DefaultThemes = {
    'basic': [
        Style('default', 'default', 'default'),
        Style('lineno', 'White', 'Blue'),
        Style('parenthesis_cur', 'White', 'Blue'),
        Style('parenthesis_match', 'Red', 'Yellow'),

        Style('keyword', 'Magenta', None),
        Style('constant', 'Red', None),
        Style('directive', 'Orange', None),
        Style('comment', 'Cyan', None),
        Style('string', 'Blue', None),
        Style('number', 'Green', None),

        Overlay('cursor_row', None, 'Base02'),
        Overlay('breakpoint', None, 'Base02'),
        Overlay('current_row', None, 'Yellow'),
    ],
}
