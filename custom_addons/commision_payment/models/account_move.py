from odoo import models, fields, api, _
from odoo.exceptions import UserError

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    is_advance_payment = fields.Boolean(copy=False)


    def action_validate(self):
        """Post the advance payment to the customer's advance payment account."""
        advance_account =  self.env['account.account'].search([('name', '=', 'Advance Payment')], limit=1)
        if not advance_account:
            raise UserError(_("Please specify an advance payment account for the customer."))

        # Use the advance payment account specified in the customer record
        if not self.journal_id.default_account_id:
            raise UserError(_("The selected journal does not have a default credit account configured."))
        payment_journal = self.journal_id

        credit_account = payment_journal.default_account_id or payment_journal.payment_credit_account_id
        # Create a move (journal entry) for the advance payment
        print(credit_account.id)
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
                    'account_id': credit_account.id,
                    'debit': 0.0,
                    'credit': self.amount,
                }),
            ],
        }
        print(self.env.company.default_cash_difference_income_account_id.id)
        print(self.amount)

        # Create and post the journal entry
        move = self.env['account.move'].create(move_vals)
        move.action_post()

        # Mark the payment as posted
        self.action_post()
        self.state = 'paid'
