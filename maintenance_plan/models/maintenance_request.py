# Copyright 2017 Camptocamp SA
# Copyright 2019 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MaintenanceRequest(models.Model):

    _inherit = "maintenance.request"

    maintenance_kind_id = fields.Many2one("maintenance.kind", string="Maintenance kind", ondelete="restrict")

    maintenance_plan_id = fields.Many2one("maintenance.plan", string="Maintenance plan", ondelete="restrict")
    note = fields.Html()
    done_date = fields.Datetime()

    def write(self, vals):
        if vals.get("stage_id"):
            stage_id = self.env["maintenance.stage"].browse(int(vals.get("stage_id")))
            if stage_id.done:
                vals["done_date"] = fields.Datetime.now()
        return super(MaintenanceRequest, self).write(vals)

    def get_base_maintenance_date(self):
        """
        Returns the date used to compute the next maintenance planned
        """
        self.ensure_one()
        base_date = self.env['ir.config_parameter'].sudo().get_param('maintenance.plan.base.date', 'done_date')
        request_date = self.read([base_date])
        return request_date[0].get(base_date) or fields.Date.today()
