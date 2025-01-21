from odoo import models, fields, api, _
from odoo.exceptions import UserError

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    is_advance_payment = fields.Boolean(copy=False)


    def action_validate(self):
        """Post the advance payment to the customer's advance payment account."""
        advance_account =  self.env['account.account'].search([('name', '=', 'Advance Payment')], limit=1)
        self.reconcile_invoice(self.amount)
        return
        if not advance_account:
            raise UserError(_("Please specify an advance payment account for the customer."))

        # Use the advance payment account specified in the customer record
        if not self.journal_id.default_account_id:
            raise UserError(_("The selected journal does not have a default credit account configured."))
        payment_journal = self.journal_id

        credit_account = payment_journal.default_account_id or payment_journal.payment_credit_account_id
        # Create a move (journal entry) for the advance payment
        print(credit_account.id)
        owed_credit = self._get_customer_advance_balance(advance_account)
        amount = self.amount
        if owed_credit < 0:
           amount = self.reconcile_invoice(amount)


        move_vals = {
            'partner_id': self.partner_id.id,
            'move_type': 'entry',
            'date': fields.Date.today(),
            'line_ids': [
                (0, 0, {
                    'name': _('Advance Payment'),
                    'account_id': advance_account.id,  # Debit to the advance account
                    'debit': amount,
                    'credit': 0.0,
                }),
                (0, 0, {
                    'name': _('Advance Payment'),
                    'account_id': credit_account.id,
                    'debit': 0.0,
                    'credit': amount,
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

    def reconcile_invoice(self, amount):
        """
        Reconcile an invoice with a payment.

        :param env: Odoo Environment
        :param invoice_id: ID of the invoice (account.move)
        :param payment_data: Dictionary with payment details
        :return: None
        """
        # Fetch the invoice
        invoice = self.env['account.move'].search([
            ('partner_id', '=', self.partner_id.id),
            ('move_type', '=', 'out_invoice'),  # Filter for sales invoices (customer invoices)
            ('state', '=', 'posted')  # Optionally filter for only posted invoices
        ], limit=1)
        if amount < invoice.amount_total:
            raise ValueError("Payment must be greater than what is owed.")


        if invoice.state != 'posted' or invoice.payment_state == 'paid':
            raise ValueError("Invoice must be posted and unpaid to reconcile.")

        # Create a payment
        print(invoice.amount_total)
        payment = self.env['account.payment'].create({
            'payment_type': 'inbound',
            'partner_type': 'customer',
            'partner_id': invoice.partner_id.id,
            'amount': invoice.amount_total,
            'date': fields.Date.today(),
            'journal_id': self.journal_id.id,  # Bank or cash journal ID
            'payment_method_id': self.env.ref('account.account_payment_method_manual_in').id,
        })
        print(self.journal_id.id)

        # Post the payment
        payment.action_post()

        # Reconcile the payment with the invoice
        receivable_lines = invoice.line_ids.filtered(
            lambda l: l.account_id.account_type == 'asset_receivable' and not l.reconciled)
        print(len(receivable_lines))
        payment_lines = payment.move_id.line_ids.filtered(lambda l: l.account_id.account_type == 'asset_receivable')
        print(len(payment_lines))

        (receivable_lines + payment_lines).reconcile()
        return amount - invoice.amount_total
    def _get_customer_advance_balance(self, advance_account):
        """Calculate the advance balance for the customer."""
        account_moves = self.env['account.move.line'].search([
            ('account_id', '=', advance_account.id),
            ('partner_id', '=', self.partner_id.id),
        ])
        return sum(move.debit - move.credit for move in account_moves)