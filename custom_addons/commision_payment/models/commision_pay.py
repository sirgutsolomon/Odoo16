from odoo import models, fields, api
from odoo.exceptions import UserError

class Driver(models.Model):
    _name = 'ride.driver'
    _description = 'Driver'

    name = fields.Char(string='Driver Name', required=True)
    balance = fields.Float(string='Balance', default=0.0)
    partner_id = fields.Many2one('res.partner', string='Related Partner', required=True)

class Trip(models.Model):
    _name = 'ride.trip'
    _description = 'Trip'

    driver_id = fields.Many2one('ride.driver', string='Driver', required=True)
    partner_id = fields.Many2one('res.partner', string='Driver', required=True)

    trip_amount = fields.Float(string='Trip Amount', required=True)
    commission_rate = fields.Float(string='Commission Rate (%)', default=10.0)
    commission_amount = fields.Float(string='Commission Amount', compute='_compute_commission', store=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('commission_deducted', 'Commission Deducted'),
    ], default='draft', string='Status')

    @api.depends('trip_amount', 'commission_rate')
    def _compute_commission(self):
        for trip in self:
            trip.commission_amount = (trip.trip_amount * trip.commission_rate) / 100

    def action_deduct_commission(self):
        for trip in self:
            if trip.state != 'draft':
                raise UserError("Commission already deducted for this trip.")

            # Deduct commission from driver balance
            trip.driver_id.balance -= trip.commission_amount

            # Create accounting entry for commission deduction
            self._create_commission_journal_entry()

            # Mark the trip as commission deducted
            trip.state = 'commission_deducted'

    def _create_commission_journal_entry(self):
        """Create a journal entry for the commission deduction."""
        journal = self.env['account.journal'].search([('type', '=', 'sales')], limit=1)
        if not journal:
            raise UserError("Please configure a general journal.")

        move_vals = {
            'journal_id': journal.id,
            'date': fields.Date.today(),
            'ref': f'Commission for Trip {self.id}',
            'line_ids': [
                # Debit: Commission expense
                (0, 0, {
                    'account_id': self.env.ref('account.data_account_expense_misc').id,
                    'name': f'Commission for Trip {self.id}',
                    'debit': self.commission_amount,
                    'credit': 0.0,
                }),
                # Credit: Driver's payable account
                (0, 0, {
                    'account_id': self.driver_id.partner_id.property_account_payable_id.id,
                    'name': f'Commission for Trip {self.id}',
                    'debit': 0.0,
                    'credit': self.commission_amount,
                }),
            ],
        }

        move = self.env['account.move'].create(move_vals)
        move.action_post()
