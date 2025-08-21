from odoo import models, fields, api


class LibraryBook(models.Model):
    _name = 'library.book'
    _description = 'Library Book'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Title', required=True, tracking=True)
    isbn = fields.Char(string='ISBN', tracking=True)
    author_ids = fields.Many2many(
        'library.author',
        'author_book_rel',
        'book_id',
        'author_id',
        string='Authors',
        tracking=True
    )
    published_date = fields.Date(string='Published Date', tracking=True)
    cover_image = fields.Binary(string='Cover Image', tracking=True)
    summary = fields.Text(string='Summary', tracking=True)

    rental_ids = fields.One2many(
        'library.rental',
        'book_id',
        string='Rental History'
    )

    is_available = fields.Boolean(
        string='Is Available',
        compute='_compute_is_available',
        store=True,
        help='True if the book is currently available for rental (no active rentals in rented  or lost)',
        tracking=True
    )

    active_rental_count = fields.Integer(
        string='Active Rentals',
        compute='_compute_active_rental_count',
        store=False,
        help='Number of currently active rentals for this book'
    )

    user_id = fields.Many2one(
        'res.users',
        string='Responsible User',
        default=lambda self: self.env.user,
        required=True,
        ondelete='restrict',
        tracking=True
    )

    def _compute_active_rental_count(self):
        """Compute the number of active rentals for this book"""
        for book in self:
            active_rentals = book.rental_ids.filtered(
                lambda r: r.state == 'rented'
            )
            book.active_rental_count = len(active_rentals)

    def action_view_active_rentals(self):
        """Action to view active rentals for this book"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Active Rentals Of {self.name}',
            'res_model': 'library.rental',
            'view_mode': 'list,form',
            'domain': [('book_id', '=', self.id), ('state', '=', 'rented')],
            'context': {
                'default_book_id': self.id,
                'search_default_book_id': self.id,
            },
        }

    @api.depends('rental_ids.state')
    def _compute_is_available(self):
        """
        Compute the availability of the book.
        A book is available if there are no rentals in 'rented' or 'lost' state.
        """
        for book in self:
            active_rentals = book.rental_ids.filtered(
                lambda r: r.state in ['rented', 'lost']
            )
            book.is_available = not bool(active_rentals)
