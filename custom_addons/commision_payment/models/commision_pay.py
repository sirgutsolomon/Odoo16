from odoo import models, fields, api
from odoo.exceptions import UserError

class Trip(models.Model):
    _name = 'ride.trip'
    _description = 'Trip'

    customer_id = fields.Many2one('res.partner', string='Customer', required=True)
    commission_rate = fields.Float(string='Commission Amount Deducted', default=10.0)
    trip_amount = fields.Float(string='Trip Amount', required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('invoice_created', 'Invoice Created'),
        ('paid', 'Paid'),
    ], default='draft', string='Status')

    def action_deduct_commission(self):
        """Create an invoice and deduct the trip amount from advance payment."""
        for trip in self:
            if trip.state != 'draft':
                raise UserError("Trip has already been processed.")

            # Step 1: Create the invoice
            invoice = trip.create_commission_invoice()

            # Step 3: Update the trip state to 'paid'
            trip.state = 'paid'


    def _create_invoice(self):
        """Create a customer invoice for the trip amount."""
        journal = self.env['account.journal'].search([('type', '=', 'sale')], limit=1)
        income_account = self.env['account.account'].search([('account_type', '=', 'income')], limit=1)
        if not self.customer_id.property_account_advance_id:
            raise UserError(_("Please specify an advance payment account for the customer."))

        # Use the advance payment account specified in the customer record
        advance_account = self.customer_id.property_account_advance_id
        if not income_account:
            raise UserError("No income account configured.")

        invoice_vals = {
            'move_type': 'out_invoice',
            'partner_id': self.customer_id.id,
            'invoice_date': fields.Date.today(),
            'journal_id': journal.id,
            'currency_id': self.env.company.currency_id.id,
            'invoice_line_ids': [
                (0, 0, {
                    'name': f'Trip Charge for {self.customer_id.name}',
                    'quantity': 1,
                    'price_unit': self.commission_rate,
                    'account_id': advance_account.id,
                }),
                # (0, 0, {
                #     'name': f'Trip Charge for {self.customer_id.name}',
                #     'quantity': 1,
                #     'price_unit': self.commission_rate,
                #     'account_id': advance_account.id,
                # }),

            ],
        }

        invoice = self.env['account.move'].create(invoice_vals)
        invoice.action_post()

        return invoice

    def _deduct_from_advance_payment(self, invoice):
        """Create a payment to deduct from the advance payment account and reconcile it with the invoice."""
        advance_account = self.customer_id.property_account_advance_id
        bank_journal = self.env['account.journal'].search([('type', '=', 'bank')], limit=1)

        if not advance_account:
            raise UserError(f"No advance payment account configured for {self.customer_id.name}.")

        if not bank_journal:
            raise UserError("Please configure a bank journal for advance payments.")

        # Create the payment entry
        payment_vals = {
            'payment_type': 'inbound',
            'partner_type': 'customer',
            'partner_id': self.customer_id.id,
            'amount': self.commission_rate,
            'currency_id': self.env.company.currency_id.id,
            'date': fields.Date.today(),
            'journal_id': bank_journal.id,
            'payment_method_line_id': bank_journal.inbound_payment_method_line_ids and
                                      bank_journal.inbound_payment_method_line_ids[0].id or False,
            'destination_account_id': advance_account.id,
        }

        payment = self.env['account.payment'].create(payment_vals)
        payment.action_post()

        # Reconcile the payment with the invoice
        receivable_lines = invoice.line_ids.filtered(lambda l: l.account_type == 'receivable' and not l.reconciled)
        payment_lines = payment.move_id.line_ids.filtered(lambda l: l.account_type == 'receivable' and not l.reconciled)

        (receivable_lines + payment_lines).reconcile()

        return payment


    def create_commission_invoice(self):
        """Create an invoice for the commission deduction."""
        # Ensure the customer has sufficient advance balance
        advance_account =  self.env['account.account'].search([('name', '=', 'Advance Payment')], limit=1)
        if not advance_account:
            raise UserError("Please configure an advance payment account for the customer.")

        customer_balance = self._get_customer_advance_balance(advance_account)
        print(f'this is the customer balance {customer_balance}')

        if customer_balance + self.commission_rate < self.commission_rate:
            raise UserError("Insufficient advance balance for this trip.")

        # Find the income account (commission income)
        income_account = self.env['account.account'].search([('account_type', '=', 'income')], limit=1)
        if not income_account:
            raise UserError("No income account configured.")
        # Step 1: Create the Invoice ask here
        unit_price = 0

        invoice_vals = {
            'move_type': 'out_invoice',
            'partner_id': self.customer_id.id,
            'invoice_date': fields.Date.today(),
            'journal_id': self.env['account.journal'].search([('type', '=', 'sale')], limit=1).id,
            'currency_id': self.env.company.currency_id.id,
            'invoice_line_ids': [
                (0, 0, {
                    'name': f'Trip Charge for {self.customer_id.name}',
                    'quantity': 1,
                    'price_unit': 0,
                    'account_id': self.env['account.account'].search([('account_type', '=', 'income')], limit=1).id,
                }),
            ],
        }
        invoice = self.env['account.move'].create(invoice_vals)
        invoice.action_post()

        # Step 2: Check for Unreconciled Receivable Balances
        receivable_lines = self.env['account.move.line'].search([
            ('partner_id', '=', self.customer_id.id),
            ('account_id', '=', self.customer_id.property_account_receivable_id.id),  # Receivable account
            ('reconciled', '=', False),
            ('balance', '>', 0),
        ])

        # Check if there are sufficient funds
        total_available = sum(receivable_lines.mapped('balance'))
        print(self.customer_id.property_account_receivable_id.id)

        if total_available <= 0:
            raise UserError("No available balance in the receivable account to deduct from.")

        # Step 3: Deduct the Advance Payment
        deduction_amount = min(self.commission_rate, total_available)

        # Create a journal entry to deduct the advance payment
        deduction_move = self.env['account.move'].create({
            'journal_id': self.env['account.journal'].search([('type', '=', 'general')], limit=1).id,
            'line_ids': [
                (0, 0, {
                    'account_id': advance_account.id,  # Advance payment account
                    'partner_id': self.customer_id.id,
                    'credit': deduction_amount,
                    'name': 'Advance Payment Deduction for Trip',
                }),
                (0, 0, {
                    'account_id': self.env['account.account'].search([('account_type', '=', 'income')], limit=1).id,  # Income account
                    'partner_id': self.customer_id.id,
                    'debit': deduction_amount,
                    'name': 'Advance Payment Deduction for Trip',
                }),
            ],
        })

        deduction_move.action_post()

    def _get_customer_advance_balance(self, advance_account):
        """Calculate the advance balance for the customer."""
        account_moves = self.env['account.move.line'].search([
            ('account_id', '=', advance_account.id),
            ('partner_id', '=', self.customer_id.id),
        ])
        return sum(move.debit - move.credit for move in account_moves)

    def _reconcile_with_advance(self, invoice, advance_account):
        """Automatically reconcile the invoice with the customer's advance payment."""
        advance_lines = self.env['account.move.line'].search([
            ('account_id', '=', advance_account.id),
            ('partner_id', '=', self.customer_id.id),
            ('reconciled', '=', False),
        ])
        print(len(advance_lines))

        invoice_lines = invoice.line_ids.filtered(lambda line: line.account_id.account_type == 'asset_receivable')
        print(invoice_lines)

        # (advance_lines + invoice_lines).reconcile()