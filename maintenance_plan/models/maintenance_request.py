# Copyright 2017 Camptocamp SA
# Copyright 2019 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models
from datetime import datetime


class MaintenanceRequest(models.Model):

    _inherit = "maintenance.request"

    maintenance_kind_id = fields.Many2one(
        string="Maintenance kind", comodel_name="maintenance.kind", ondelete="restrict"
    )

    maintenance_plan_id = fields.Many2one(
        string="Maintenance plan", comodel_name="maintenance.plan", ondelete="restrict"
    )
    note = fields.Html()
    done_date = fields.Datetime()

    def write(self, vals):
        if vals.get("stage_id"):
            stage_id = self.env["maintenance.stage"].browse(int(vals.get("stage_id")))
            if stage_id.done:
                vals["done_date"] = fields.Datetime.now()
        return super(MaintenanceRequest, self).write(vals)

    def get_base_maintenance_date(self, base_date=False):
        """
        Returns the date used to compute the next maintenance planned
        """
        self.ensure_one()
        if not base_date:
            base_date = self.env['ir.config_parameter'].sudo().get_param('maintenance.plan.base.date', 'done_date')
        request_dict = self.read([base_date, 'request_date'])
        # If base date is not set yet (e.g. when creating requests from horizon planning), we must fall back to
        # standard behavior and use request date as base date
        request_date = request_dict[0].get(base_date) or request_dict[0].get('request_date')
        if request_date and isinstance(request_date, datetime):
            request_date = request_date.date()
        return request_date
