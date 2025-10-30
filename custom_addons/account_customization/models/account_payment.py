from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    custom_account_id = fields.Many2one(
        'account.account',
        string='Account',
        help="Select the account for dual posting"
    )

    def action_validate(self):
        """Override to add custom journal entries after validation"""
        print("=== ACTION VALIDATE CALLED ===")
        _logger.info("Payment action_validate called for ID %s", self.id)
        
        result = super().action_validate()
        
        # Add custom journal entries after validation
        for payment in self:
            print("--------------------------------this is the payment -----------------------------------------------")
            print(payment)
            print(payment.custom_account_id)
            if payment.custom_account_id:
                payment._create_custom_journal_entries()
        
        return result
    
    def _create_custom_journal_entries(self):
        """Create additional journal entries for custom account"""
        print(f"=== CREATING CUSTOM ENTRIES FOR PAYMENT {self.id} ===")
        _logger.info("Creating custom journal entries for payment %s", self.id)
        
        if not self.custom_account_id or not self.move_id:
            return
            
        # Create additional move lines in the existing journal entry
        move_lines = []
        amount = self.amount
        
        # Determine debit/credit based on payment type
        if self.payment_type == 'inbound':  # Customer Payment
            custom_debit = amount
            custom_credit = 0.0
            balance_debit = 0.0
            balance_credit = amount
        else:  # Vendor Payment (outbound)
            custom_debit = 0.0
            custom_credit = amount
            balance_debit = amount
            balance_credit = 0.0

        # Custom account line
        custom_line = {
            'name': self.ref or self.payment_reference or '/',
            'account_id': self.custom_account_id.id,
            'partner_id': self.partner_id.id if self.partner_id else False,
            'debit': custom_debit,
            'credit': custom_credit,
            'move_id': self.move_id.id,
        }
        
        # Balancing line (use journal's default account)
        balance_account = self.journal_id.default_account_id
        if balance_account:
            balance_line = {
                'name': self.ref or self.payment_reference or '/',
                'account_id': balance_account.id,
                'partner_id': self.partner_id.id if self.partner_id else False,
                'debit': balance_debit,
                'credit': balance_credit,
                'move_id': self.move_id.id,
            }
            
            # Create the move lines
            self.env['account.move.line'].create([custom_line, balance_line])
            
            print(f"Created custom journal entries: {custom_line}, {balance_line}")
            _logger.info("Created custom journal entries for payment %s", self.id)