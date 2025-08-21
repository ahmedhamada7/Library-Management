{
    'name': "Library Management",
    'version': '18.0.1.0.0',
    'description': """ This Module Manages An Internal Library Of Books.""",
    'author': "Apps Square For Scientific Solutions",
    'website': "",
    'category': 'Education',
    'depends': ['base', 'mail'],
    'data': [
        'security/security_groups.xml',
        'security/ir.model.access.csv',
        'security/record_rules.xml',

        'views/library_book.xml',
        'views/library_author.xml',
        'views/library_rental.xml',
        'views/menus.xml',
    ],

    'license': 'LGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False,
}
