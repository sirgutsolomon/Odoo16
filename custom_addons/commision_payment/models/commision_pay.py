from odoo import models, fields, api
from odoo.exceptions import UserError

class Trip(models.Model):
    _name = 'ride.trip'
    _description = 'Trip'

    customer_id = fields.Many2one('res.partner', string='Customer', required=True)
    trip_amount = fields.Float(string='Trip Amount', required=True)
    commission_rate = fields.Float(string='Commission Amount Deducted', default=10.0)
    # commission_amount = fields.Float(string='Commission Amount', compute='_compute_commission', store=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('invoice_created', 'Invoice Created'),
        ('commission_deducted', 'Commission Deducted'),
    ], default='draft', string='Status')

    # @api.depends('trip_amount', 'commission_rate')
    # def _compute_commission(self):
    #     for trip in self:
    #         trip.commission_amount = (trip.trip_amount * trip.commission_rate) / 100

    def action_deduct_commission(self):
        for trip in self:
            if trip.state != 'draft':
                raise UserError("Commission already deducted or invoice created for this trip.")

            # Step 1: Create an Invoice
            invoice = self._create_invoice()

            # Step 2: Create the Journal Entry for Commission Deduction
            self._deduct_from_advance_account(invoice)

            # Mark the trip as commission deducted
            trip.state = 'commission_deducted'

            return invoice

    def _create_invoice(self):
        """Create a customer invoice for the trip."""
        invoice_vals = {
            'move_type': 'out_invoice',  # Customer Invoice
            'partner_id': self.customer_id.id,  # The customer is set as the invoice partner
            'invoice_date': fields.Date.today(),
            'invoice_line_ids': [
                (0, 0, {
                    'name': f'Trip Charge for Customer {self.customer_id.name}',
                    'quantity': 1,
                    'price_unit': self.commission_rate,
                    'account_id': self.customer_id.property_account_advance_id.id,
                }),
                (0, 0, {
                    'name': f'Trip Charge for Customer {self.customer_id.name}',
                    'quantity': 1,
                    'price_unit': self.commission_rate,
                    'account_id': self.customer_id.property_account_advance_id.id,
                }),
            ],
        }

        invoice = self.env['account.move'].create(invoice_vals)
        invoice.action_post()  # Post the invoice

        return invoice

    def _create_commission_journal_entry(self):
        """Create a journal entry for the commission deduction."""
        journal = self.env['account.journal'].search([('type', '=', 'general')], limit=1)
        if not journal:
            raise UserError("Please configure a general journal.")

        move_vals = {
            'journal_id': journal.id,
            'date': fields.Date.today(),
            'ref': f'Commission Deduction for Trip {self.id}',
            'line_ids': [
                # Debit: Commission Expense Account
                (0, 0, {
                    'account_id': self.env['account.account'].search([('account_type', '=', 'income')], limit=1).id,
                    'name': f'Commission for Trip {self.id}',
                    'debit': self.commission_rate,
                    'credit': 0.0,
                }),
                # Credit: Customer's Payable Account
                (0, 0, {
                    'account_id': self.customer_id.property_account_advance_id.id,
                    'name': f'Commission for Trip {self.id}',
                    'debit': 0.0,
                    'credit': self.commission_rate,
                }),
            ],
        }

        move = self.env['account.move'].create(move_vals)
        move.action_post()

    def _deduct_from_advance_account(self, invoice):
        """Deduct the trip amount from the customer's advance payment account and reconcile it with the invoice."""
        advance_account = self.customer_id.property_account_advance_id
        if not advance_account:
            raise UserError(f"No advance payment account configured for {self.customer_id.name}.")

        # Create a payment entry to deduct from the advance payment account
        journal = self.env['account.journal'].search([('type', '=', 'bank')], limit=1)
        if not journal:
            raise UserError("Please configure a bank journal for advance payments.")

        payment_vals = {
            'payment_type': 'inbound',
            'partner_type': 'customer',
            'partner_id': self.customer_id.id,
            'amount': self.trip_amount,
            'currency_id': self.env.company.currency_id.id,
            'date': fields.Date.today(),
            'journal_id': journal.id,
            'payment_method_line_id': journal.inbound_payment_method_line_ids and
                                      journal.inbound_payment_method_line_ids[0].id or False,
            'is_advance_payment': True,
            'partner_bank_id': False,
            'destination_account_id': advance_account.id,  # Deduct from the advance payment account
        }

        payment = self.env['account.payment'].create(payment_vals)


        # Reconcile the payment with the invoice
        receivable_lines = invoice.line_ids.filtered(
            lambda line: line.account_id == advance_account and not line.reconciled)
        payment_lines = payment.move_id.line_ids.filtered(
            lambda line: line.account_id == advance_account and not line.reconciled)

        # Log the account info for debugging
        print("Receivable lines: ", receivable_lines)
        print("Payment lines: ", payment_lines)

        # Reconcile the lines between invoice and payment
        (receivable_lines + payment_lines).reconcile()

        # Optionally update the invoice state manually
        payment.action_post()  # Ensure it's posted after reconciliation

        return payment
