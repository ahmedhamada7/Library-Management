from odoo import models, fields


class LibraryAuthor(models.Model):
    _name = 'library.author'
    _description = 'Library Author'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    name = fields.Char(string='Author Full Name', required=True, tracking=True)
    biography = fields.Text(string='Biography', tracking=True)
    user_id = fields.Many2one(
        'res.users',
        string='Responsible User',
        default=lambda self: self.env.user,
        required=True,
        ondelete='restrict',
        tracking=True
    )
    book_ids = fields.Many2many(
        'library.book',
        'author_book_rel',
        'author_id',
        'book_id',
        string='Authored Books',
        tracking=True
    )
