from kaa.theme import Theme, Style

DefaultTheme = Theme('default', [
    Style('default', 'default', 'default', False, False),
    Style('lineno', 'White', 'Blue', False, False),
    Style('parenthesis_cur', 'White', 'Blue', False, False),
    Style('parenthesis_match', 'Red', 'Yellow', False, False),
])
