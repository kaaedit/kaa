from kaa.theme import Theme, Style

DefaultThemes = {
    'default':
        Theme([
            Style('default', 'default', 'default'),
            Style('lineno', 'White', 'Blue'),
            Style('parenthesis_cur', 'White', 'Blue'),
            Style('parenthesis_match', 'Red', 'Yellow'),

            Style('keyword', 'Red', 'default'),
            Style('comment', 'Cyan', 'default'),
            Style('string', 'Green', 'default'),
            Style('number', 'Yellow', 'default'),
        ])
}
