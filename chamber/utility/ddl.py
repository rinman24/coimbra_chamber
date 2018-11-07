"""DDL utility module."""

build_instructions = {
    ('experiments', 'table_order'): (
        'Tube', 'Setting'
        ),
    ('experiments', 'ddl'): dict(
        Tube=(
            'ddl a'
            ),
        Setting=(
            'ddl b'
            )
        )
    }

table_order = (
    'Tube'
)

ddl = dict()