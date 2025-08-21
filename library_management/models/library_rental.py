from odoo import models, fields, api
from odoo.exceptions import ValidationError


class LibraryRental(models.Model):
    _name = 'library.rental'
    _description = 'Book Rental'
    _order = 'rental_date desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'book_id'

    book_id = fields.Many2one(
        'library.book',
        string='Book',
        required=True,
        tracking=True
    )
    borrower_id = fields.Many2one(
        'res.partner',
        string='Borrower',
        required=True,
        tracking=True
    )
    rental_date = fields.Datetime(
        string='Rental Date',
        default=lambda self: fields.Datetime.now(),
        tracking=True
    )
    return_date = fields.Datetime(
        string='Return Date',
        tracking=True
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('rented', 'Rented'),
        ('returned', 'Returned'),
        ('lost', 'Lost')
    ], string='Status', default='draft', required=True, tracking=True)
    hide_confirm = fields.Boolean(default=False)
    user_id = fields.Many2one(
        'res.users',
        string='Responsible User',
        default=lambda self: self.env.user,
        required=True,
        ondelete='restrict',
        tracking=True
    )

    def action_confirm_rental(self):
        """
        Confirm the rental: change state from draft to rented
        and set rental_date to current time if not already set
        """
        for rental in self:
            rental.hide_confirm = True
            if rental.state == 'draft':
                values = {
                    'state': 'rented'
                }
                if not rental.rental_date:
                    values['rental_date'] = fields.Datetime.now()

                rental.write(values)

    def action_return_book(self):
        for rental in self:
            if rental.state == 'rented':
                rental.write({
                    'return_date': fields.Datetime.now(),
                    'state': 'returned'
                })

    @api.constrains('book_id', 'state')
    def _check_book_availability(self):
        """
        Constraint to prevent renting a book that is already rented.
        A book cannot be rented if another rental exists with state 'rented'
        and no return_date set.
        """
        for rental in self:
            if rental.state == 'rented':
                active_rentals = self.search([
                    ('book_id', '=', rental.book_id.id),
                    ('state', '=', 'rented'),
                    ('id', '!=', rental.id),
                    ('return_date', '=', False),
                ])

                if active_rentals:
                    raise ValidationError(
                        f"The book '{rental.book_id.name}' is already rented out. "
                        f"Please wait until it is returned before renting it again."
                    )

    @api.constrains('state', 'return_date')
    def _check_return_date_consistency(self):
        """
        Additional constraint:
        - Returned books must have a return_date
        - Rented books should not have a return_date
        """
        for rental in self:
            if rental.state == 'returned' and not rental.return_date:
                raise ValidationError(
                    "Returned books must have a return date set. "
                    "Please set the return date or use the 'Return Book' button."
                )

            if rental.state == 'rented' and rental.return_date:
                raise ValidationError(
                    "Rented books should not have a return date set. "
                    "The return date will be automatically set when the book is returned."
                )

    @api.model
    def create(self, vals):
        if vals.get('state') in ['draft', 'rented']:
            book_id = vals.get('book_id')
            if book_id:
                unavailable_books = self.search([
                    ('book_id', '=', book_id),
                    ('state', 'in', ['rented', 'lost']),
                    ('return_date', '=', False),
                ])
                if unavailable_books:
                    book_name = self.env['library.book'].browse(book_id).name
                    raise ValidationError(
                        f"Cannot create rental - the book '{book_name}' is already unavailable (Rented or Lost)."
                    )
        return super(LibraryRental, self).create(vals)

    def write(self, vals):
        if 'state' in vals and vals['state'] == 'rented':
            for rental in self:
                if rental.state != 'rented':
                    unavailable_books = self.search([
                        ('book_id', '=', rental.book_id.id),
                        ('state', 'in', ['rented', 'lost']),
                        ('id', '!=', rental.id),
                        ('return_date', '=', False),
                    ])
                    if unavailable_books:
                        raise ValidationError(
                            f"Cannot rent book '{rental.book_id.name}' - it is already unavailable (rented or lost)."
                        )
        return super(LibraryRental, self).write(vals)

    def action_mark_lost(self):
        for rental in self:
            if rental.state in ['draft', 'rented']:
                rental.write({
                    'state': 'lost'
                })
