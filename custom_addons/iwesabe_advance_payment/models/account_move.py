from odoo import models, fields, api, _
from odoo.exceptions import UserError

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    is_advance_payment = fields.Boolean(copy=False)

    def post_advance_payment(self):
        """Post the advance payment to the customer's advance payment account."""
        if not self.partner_id.property_account_advance_id:
            raise UserError(_("Please specify an advance payment account for the customer."))

        # Use the advance payment account specified in the customer record
        advance_account = self.partner_id.property_account_advance_id
        if not self.journal_id.default_account_id:
            raise UserError(_("The selected journal does not have a default credit account configured."))

        # Create a move (journal entry) for the advance payment
        move_vals = {
            'partner_id': self.partner_id.id,
            'move_type': 'entry',
            'date': fields.Date.today(),
            'line_ids': [
                (0, 0, {
                    'name': _('Advance Payment'),
                    'account_id': advance_account.id,  # Debit to the advance account
                    'debit': self.amount,
                    'credit': 0.0,
                }),
                (0, 0, {
                    'name': _('Advance Payment'),
                    'account_id': self.journal_id.default_account_id.id,  # Credit to the bank/cash account
                    'debit': 0.0,
                    'credit': self.amount,
                }),
            ],
        }

        # Create and post the journal entry
        move = self.env['account.move'].create(move_vals)
        move.action_post()

        # Mark the payment as posted
        self.action_post()
