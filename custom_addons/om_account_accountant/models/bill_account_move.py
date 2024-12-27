from odoo import models, fields

class BillAccountMove(models.Model):
    _inherit = 'account.move'

    receipt_no = fields.Char(string="Receipt No")
