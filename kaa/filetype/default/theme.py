from kaa.theme import Theme, Style

DefaultThemes = {
    'default':
        Theme([
            Style('default', 'default', 'default', False, False),
            Style('lineno', 'White', 'Blue', False, False),
            Style('parenthesis_cur', 'White', 'Blue', False, False),
            Style('parenthesis_match', 'Red', 'Yellow', False, False),

            Style('keyword', 'magenta', 'default'),
            Style('comment', 'green', 'default'),
            Style('string', 'red', 'default'),
        ])
}
