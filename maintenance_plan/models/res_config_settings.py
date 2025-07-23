# Copyright 2017 Camptocamp SA
# Copyright 2019 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    maintenance_plan_base_date = fields.Selection(
        [
            ("request_date", "Request Date"),
            ("schedule_date", "Scheduled Date"),
            ("done_date", "Done Date")
        ],
        config_parameter="maintenance.plan.base.date",
        default="done_date",
    )
