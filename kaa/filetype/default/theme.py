from kaa.theme import Theme, Style

DefaultThemes = {
    'default':
        Theme([
            Style('default', 'default', 'default'),
            Style('lineno', 'White', 'Blue'),
            Style('parenthesis_cur', 'White', 'Blue'),
            Style('parenthesis_match', 'Red', 'Yellow'),

            Style('keyword', 'Magenta', 'default'),
            Style('comment', 'blue', 'default'),
            Style('string', 'Green', 'default'),
        ])
}
