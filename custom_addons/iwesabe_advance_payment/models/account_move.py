# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class AccountMove(models.Model):
    _inherit = "account.move"

    def action_post(self):
        result = super().action_post()
        for record in self:
            record._action_reconcile_advance_pymt()
        return result

    def _action_reconcile_advance_pymt(self):
        if self.move_type == "out_invoice":
            payment_ids = (
                self.env["account.payment"]
                .search(
                    [
                        ("is_advance_payment", "=", True),
                        ("payment_type", "=", "inbound"),
                        ("partner_type", "=", "customer"),
                        ("partner_id", "=", self.partner_id.id),
                        ("state", "=", "posted"),
                    ]
                )
                .filtered(lambda x: not x.is_reconciled)
            )
            if payment_ids:
                line_ids = payment_ids.mapped("move_id.line_ids").filtered(
                    lambda x: x.account_type
                    in ("asset_receivable", "liability_payable")
                    and not x.reconciled
                )
                if line_ids:
                    reconcile_line = self.line_ids.filtered(
                        lambda x: x.account_type
                        in ("asset_receivable", "liability_payable")
                        and not x.reconciled
                    )
                    if reconcile_line:
                        line_ids += reconcile_line
                        line_ids.reconcile()
        elif self.move_type == "in_invoice":
            payment_ids = (
                self.env["account.payment"]
                .search(
                    [
                        ("is_advance_payment", "=", True),
                        ("payment_type", "=", "outbound"),
                        ("partner_type", "=", "supplier"),
                        ("partner_id", "=", self.partner_id.id),
                        ("state", "=", "posted"),
                    ]
                )
                .filtered(lambda x: not x.is_reconciled)
            )
            if payment_ids:
                line_ids = payment_ids.mapped("move_id.line_ids").filtered(
                    lambda x: x.account_type
                    in ("asset_receivable", "liability_payable")
                    and not x.reconciled
                )
                if line_ids:
                    reconcile_line = self.line_ids.filtered(
                        lambda x: x.account_type
                        in ("asset_receivable", "liability_payable")
                        and not x.reconciled
                    )
                    if reconcile_line:
                        line_ids += reconcile_line
                        line_ids.reconcile()
